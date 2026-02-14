import asyncio
import os
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
        user_id: int | None = None
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
            
            for i, cut in enumerate(cuts):
                start = float(cut.get("start", 0))
                end = float(cut.get("end", 0))
                duration = end - start
                
                if duration <= 0: continue
                
                part_path = temp_dir / f"part_{i:04d}.mp4"
                scene_files.append(part_path)
                tasks.append(self._render_scene(
                    job_id, source_path, start, duration, str(part_path),
                    vf_filters=vf_filters,
                    af_filters=af_filters,
                    crf=crf,
                    preset=preset
                ))

            # 2. Execute parallel renders
            publish_progress(job_id, "processing", f"Rendering {len(tasks)} scenes in parallel...", 70, user_id=user_id)
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check for failures
            for res in results:
                if isinstance(res, Exception):
                    logger.error("scene_render_failed", job_id=job_id, error=str(res))
                    return False

            # 3. Concatenate scenes
            publish_progress(job_id, "processing", "Merging scenes...", 85, user_id=user_id)
            success = await self._concatenate_scenes(job_id, scene_files, output_path)
            
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
        preset: str = "veryfast"
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
            
            if vf_filters:
                cmd += ["-vf", vf_filters]
            if af_filters:
                cmd += ["-af", af_filters]
                
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

    async def _concatenate_scenes(self, job_id: int, scene_files: List[Path], out_path: str) -> bool:
        """Merges scenes using the concat demuxer."""
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

# Singleton
rendering_orchestrator = RenderingOrchestrator()
