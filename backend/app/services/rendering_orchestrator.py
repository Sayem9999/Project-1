import asyncio
import os
import shutil
from pathlib import Path
from typing import List, Dict, Any
import structlog
from ..config import settings
from .concurrency import limits
from .workflow_engine import publish_progress

logger = structlog.get_logger()

class RenderingOrchestrator:
    """
    Orchestrates parallel scene rendering and final concatenation.
    Reduces total render time by utilizing multiple CPU cores for independent scenes.
    """
    
    def __init__(self):
        self.output_root = Path(settings.storage_root) / "outputs"
        self.output_root.mkdir(parents=True, exist_ok=True)
        self.ffmpeg_path = self._resolve_ffmpeg()

    def _resolve_ffmpeg(self) -> str:
        ext = ".exe" if os.name == 'nt' else ""
        paths_to_check = [
            f"tools/ffmpeg-8.0.1-essentials_build/bin/ffmpeg{ext}",
            f"../tools/ffmpeg-8.0.1-essentials_build/bin/ffmpeg{ext}",
            f"../../tools/ffmpeg-8.0.1-essentials_build/bin/ffmpeg{ext}"
        ]
        for p in paths_to_check:
            if os.path.exists(p):
                return os.path.abspath(p)
        on_path = shutil.which("ffmpeg")
        if on_path:
            return on_path
        try:
            import imageio_ffmpeg

            return imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            pass
        return "ffmpeg"

    async def render_parallel(
        self, 
        job_id: int, 
        source_path: str, 
        cuts: List[Dict[str, Any]], 
        output_path: str,
        vf_filters: str | None = None,
        af_filters: str | None = None,
        crf: int = 23,
        preset: str = "veryfast",
        user_id: int | None = None,
        transition_style: str = "cut",
        transition_duration: float = 0.25,
    ) -> bool:
        """
        Renders scenes in parallel and merge them.
        """
        if not cuts:
            logger.warning("render_no_cuts", job_id=job_id)
            return False

        temp_dir = self.output_root / f"job-{job_id}-parts"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # 1. Prepare scene tasks
            tasks = []
            scene_files = []
            scene_durations = []
            
            for i, cut in enumerate(cuts):
                start = float(cut.get("start", 0))
                end = float(cut.get("end", 0))
                duration = end - start
                
                if duration <= 0: continue
                
                part_path = temp_dir / f"part_{i:04d}.mp4"
                scene_files.append(part_path)
                speed = float(cut.get("speed", 1.0) or 1.0)
                if speed <= 0:
                    speed = 1.0
                scene_durations.append(duration / speed)
                tasks.append(self._render_scene(
                    job_id, str(cut.get("source_path") or source_path), start, duration, str(part_path),
                    vf_filters=vf_filters,
                    af_filters=af_filters,
                    crf=crf,
                    preset=preset,
                    speed=speed,
                    keyframes=cut.get("keyframes") if isinstance(cut.get("keyframes"), list) else None,
                ))

            if not tasks:
                logger.warning("render_no_valid_cuts", job_id=job_id)
                return False

            # 2. Execute parallel renders
            publish_progress(job_id, "processing", f"Rendering {len(tasks)} scenes in parallel...", 70, user_id=user_id)
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check for failures
            for res in results:
                if isinstance(res, Exception):
                    logger.error("scene_render_failed", job_id=job_id, error=str(res))
                    return False

            scene_files = [f for f in scene_files if f.exists()]
            if not scene_files:
                logger.warning("render_no_scene_outputs", job_id=job_id)
                return False

            # 3. Concatenate scenes
            publish_progress(job_id, "processing", "Merging scenes...", 85, user_id=user_id)
            success = await self._concatenate_scenes(
                job_id,
                scene_files,
                output_path,
                scene_durations=scene_durations,
                transition_style=transition_style,
                transition_duration=transition_duration,
            )
            
            return success

        finally:
            # Cleanup temp parts
            import shutil
            if temp_dir.exists():
                shutil.rmtree(temp_dir)

    async def _render_scene(
        self, 
        job_id: int, 
        source_path: str, 
        start: float, 
        duration: float, 
        out_path: str,
        vf_filters: str | None = None,
        af_filters: str | None = None,
        crf: int = 23,
        preset: str = "veryfast",
        speed: float = 1.0,
        keyframes: list[dict] | None = None,
    ):
        """Renders a single scene with a semaphore."""
        # Convert to absolute paths to avoid FFmpeg CWD issues
        abs_src = os.path.abspath(source_path)
        abs_out = os.path.abspath(out_path)
        
        async with limits.scene_render_semaphore:
            # Use fast-seek (-ss before -i) for speed
            cmd = [
                self.ffmpeg_path, "-y",
                "-ss", str(start),
                "-t", str(duration),
                "-i", abs_src,
                "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
                "-c:a", "aac", "-b:a", "128k",
                "-avoid_negative_ts", "make_zero",
            ]

            vf_chain: list[str] = []
            af_chain: list[str] = []

            if speed and abs(speed - 1.0) > 0.01:
                vf_chain.append(f"setpts={1/speed}*PTS")
                af_chain.extend(self._atempo_chain(speed))

            zoom_kf = self._keyframed_zoom_filter(keyframes)
            if zoom_kf:
                vf_chain.append(zoom_kf)

            if vf_filters:
                vf_chain.append(vf_filters)
            if af_filters:
                af_chain.append(af_filters)

            if vf_chain:
                cmd += ["-vf", ",".join(vf_chain)]
            if af_chain:
                cmd += ["-af", ",".join(af_chain)]
                
            cmd.append(abs_out)
            
            proc = await asyncio.create_subprocess_exec(
                *cmd, 
                stdout=asyncio.subprocess.PIPE, 
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode != 0:
                err_msg = stderr.decode()[-500:]
                # Log full command for debugging on failure
                logger.error("ffmpeg_scene_failed", job_id=job_id, command=" ".join(cmd), error=err_msg)
                raise Exception(f"FFmpeg scene render failed: {err_msg}")

    @staticmethod
    def _atempo_chain(speed: float) -> list[str]:
        """Build FFmpeg atempo filters while respecting per-filter [0.5,2.0] constraints."""
        s = max(0.25, min(speed, 4.0))
        chain = []
        while s > 2.0:
            chain.append("atempo=2.0")
            s /= 2.0
        while s < 0.5:
            chain.append("atempo=0.5")
            s *= 2.0
        chain.append(f"atempo={s:.4f}")
        return chain

    @staticmethod
    def _keyframed_zoom_filter(keyframes: list[dict] | None) -> str | None:
        if not keyframes:
            return None
        zoom_kf = [k for k in keyframes if (k.get("property") or "").lower() == "zoom"]
        if len(zoom_kf) < 2:
            return None
        z0 = float(zoom_kf[0].get("value", 1.0))
        z1 = float(zoom_kf[-1].get("value", z0))
        if abs(z1 - z0) < 0.01:
            return None
        # Lightweight keyframe approximation using gradual zoom.
        step = (z1 - z0) / 240.0
        return f"zoompan=z='if(lte(on,1),{z0:.4f},min(max(zoom+({step:.6f}),{min(z0,z1):.4f}),{max(z0,z1):.4f}))':d=1:s=1280x720"

    async def _concatenate_scenes(
        self,
        job_id: int,
        scene_files: List[Path],
        out_path: str,
        scene_durations: List[float] | None = None,
        transition_style: str = "cut",
        transition_duration: float = 0.25,
    ) -> bool:
        """Merges scenes using the concat demuxer."""
        if transition_style and transition_style.lower() not in {"cut", "none"} and len(scene_files) > 1:
            return await self._concatenate_with_transitions(
                scene_files=scene_files,
                out_path=out_path,
                scene_durations=scene_durations or [],
                transition_style=transition_style,
                transition_duration=transition_duration,
            )

        list_path = self.output_root / f"job-{job_id}-list.txt"
        
        # Create concat list
        with open(list_path, "w") as f:
            for scene in scene_files:
                # FFmpeg concat list needs escaped paths
                abs_p = str(scene.absolute()).replace("\\", "/")
                f.write(f"file '{abs_p}'\n")

        try:
            cmd = [
                self.ffmpeg_path, "-y",
                "-f", "concat", "-safe", "0",
                "-i", str(list_path),
                "-c", "copy",
                out_path
            ]
            
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
            
            return proc.returncode == 0
        finally:
            if list_path.exists():
                list_path.unlink()

    async def _concatenate_with_transitions(
        self,
        scene_files: List[Path],
        out_path: str,
        scene_durations: List[float],
        transition_style: str,
        transition_duration: float,
    ) -> bool:
        xfade_style = {
            "dissolve": "fade",
            "crossfade": "fade",
            "wipe_left": "wipeleft",
            "wipe_right": "wiperight",
            "slide_left": "slideleft",
            "slide_right": "slideright",
        }.get((transition_style or "").lower(), "fade")
        d = max(0.08, min(float(transition_duration or 0.25), 1.0))

        cmd = [self.ffmpeg_path, "-y"]
        for part in scene_files:
            cmd.extend(["-i", str(part.absolute())])

        if not scene_durations or len(scene_durations) != len(scene_files):
            scene_durations = [2.0] * len(scene_files)

        filter_parts: list[str] = []
        v_prev = "[0:v]"
        a_prev = "[0:a]"
        elapsed = float(scene_durations[0])
        for i in range(1, len(scene_files)):
            v_out = f"v{i}"
            a_out = f"a{i}"
            offset = max(0.0, elapsed - d)
            filter_parts.append(
                f"{v_prev}[{i}:v]xfade=transition={xfade_style}:duration={d:.3f}:offset={offset:.3f}[{v_out}]"
            )
            filter_parts.append(f"{a_prev}[{i}:a]acrossfade=d={d:.3f}:c1=tri:c2=tri[{a_out}]")
            v_prev = f"[{v_out}]"
            a_prev = f"[{a_out}]"
            elapsed += float(scene_durations[i]) - d

        cmd.extend([
            "-filter_complex", ";".join(filter_parts),
            "-map", v_prev,
            "-map", a_prev,
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "22",
            "-c:a", "aac",
            "-b:a", "160k",
            out_path,
        ])

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            logger.error("ffmpeg_transition_concat_failed", error=stderr.decode()[-500:])
            return False
        return True

# Singleton
rendering_orchestrator = RenderingOrchestrator()
