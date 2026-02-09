"""
GPU Capabilities - One-time GPU capability detection and caching.
"""
import structlog
import subprocess
import json
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from pathlib import Path

logger = structlog.get_logger()


@dataclass
class GPUInfo:
    """Information about a GPU."""
    index: int
    name: str
    driver_version: str
    memory_total_mb: int
    cuda_cores: Optional[int] = None
    compute_capability: Optional[str] = None
    
    # Encoding capabilities
    supports_nvenc: bool = False
    supports_hevc_nvenc: bool = False
    supports_av1: bool = False
    
    # Decoding capabilities
    supports_cuvid: bool = False


@dataclass
class GPUCapabilities:
    """System GPU capabilities."""
    has_gpu: bool = False
    gpus: List[GPUInfo] = field(default_factory=list)
    recommended_encoder: str = "libx264"
    recommended_decoder: str = "default"
    
    # FFmpeg hardware acceleration
    ffmpeg_hwaccels: List[str] = field(default_factory=list)
    ffmpeg_encoders: List[str] = field(default_factory=list)
    ffmpeg_decoders: List[str] = field(default_factory=list)


class GPUCapabilityDetector:
    """
    Detects and caches GPU capabilities.
    Runs once per worker to avoid per-job overhead.
    """
    
    CACHE_FILE = "storage/gpu_capabilities.json"
    
    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        self.ffmpeg = ffmpeg_path
        self._capabilities: Optional[GPUCapabilities] = None
    
    def get_capabilities(self, force_refresh: bool = False) -> GPUCapabilities:
        """Get GPU capabilities, using cache if available."""
        if self._capabilities and not force_refresh:
            return self._capabilities
        
        # Try to load from cache
        if not force_refresh:
            cached = self._load_cache()
            if cached:
                self._capabilities = cached
                return cached
        
        # Detect capabilities
        self._capabilities = self._detect_capabilities()
        
        # Save to cache
        self._save_cache(self._capabilities)
        
        return self._capabilities
    
    def _detect_capabilities(self) -> GPUCapabilities:
        """Detect GPU capabilities from system."""
        logger.info("gpu_detection_start")
        
        caps = GPUCapabilities()
        
        # Detect NVIDIA GPUs
        nvidia_gpus = self._detect_nvidia_gpus()
        if nvidia_gpus:
            caps.has_gpu = True
            caps.gpus = nvidia_gpus
        
        # Detect FFmpeg hardware acceleration
        hwaccels = self._detect_ffmpeg_hwaccels()
        caps.ffmpeg_hwaccels = hwaccels
        
        # Detect FFmpeg encoders
        encoders = self._detect_ffmpeg_encoders()
        caps.ffmpeg_encoders = encoders
        
        # Recommend encoder based on capabilities
        caps.recommended_encoder = self._recommend_encoder(caps)
        caps.recommended_decoder = self._recommend_decoder(caps)
        
        logger.info(
            "gpu_detection_complete",
            has_gpu=caps.has_gpu,
            gpu_count=len(caps.gpus),
            encoder=caps.recommended_encoder
        )
        
        return caps
    
    def _detect_nvidia_gpus(self) -> List[GPUInfo]:
        """Detect NVIDIA GPUs using nvidia-smi."""
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=index,name,driver_version,memory.total", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return []
            
            gpus = []
            for line in result.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 4:
                    gpu = GPUInfo(
                        index=int(parts[0]),
                        name=parts[1],
                        driver_version=parts[2],
                        memory_total_mb=int(float(parts[3])),
                        supports_nvenc=True,  # Assume modern NVIDIA has NVENC
                        supports_cuvid=True,
                    )
                    gpus.append(gpu)
            
            return gpus
            
        except FileNotFoundError:
            logger.debug("nvidia_smi_not_found")
            return []
        except Exception as e:
            logger.warning("nvidia_detection_failed", error=str(e))
            return []
    
    def _detect_ffmpeg_hwaccels(self) -> List[str]:
        """Detect available FFmpeg hardware accelerations."""
        try:
            result = subprocess.run(
                [self.ffmpeg, "-hwaccels"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return []
            
            hwaccels = []
            for line in result.stdout.split("\n"):
                line = line.strip()
                if line and line not in ["Hardware acceleration methods:", ""]:
                    hwaccels.append(line)
            
            return hwaccels
            
        except Exception as e:
            logger.warning("hwaccel_detection_failed", error=str(e))
            return []
    
    def _detect_ffmpeg_encoders(self) -> List[str]:
        """Detect available FFmpeg encoders."""
        try:
            result = subprocess.run(
                [self.ffmpeg, "-encoders"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return []
            
            # Look for hardware encoders
            hw_encoders = []
            for line in result.stdout.split("\n"):
                if any(hw in line for hw in ["nvenc", "qsv", "amf", "vaapi", "videotoolbox"]):
                    # Extract encoder name
                    parts = line.split()
                    if len(parts) >= 2:
                        hw_encoders.append(parts[1])
            
            return hw_encoders
            
        except Exception as e:
            logger.warning("encoder_detection_failed", error=str(e))
            return []
    
    def _recommend_encoder(self, caps: GPUCapabilities) -> str:
        """Recommend best encoder based on capabilities."""
        # Check for NVENC (NVIDIA)
        if "h264_nvenc" in caps.ffmpeg_encoders:
            return "h264_nvenc"
        
        # Check for QuickSync (Intel)
        if "h264_qsv" in caps.ffmpeg_encoders:
            return "h264_qsv"
        
        # Check for AMF (AMD)
        if "h264_amf" in caps.ffmpeg_encoders:
            return "h264_amf"
        
        # Check for VideoToolbox (macOS)
        if "h264_videotoolbox" in caps.ffmpeg_encoders:
            return "h264_videotoolbox"
        
        # Fallback to software
        return "libx264"
    
    def _recommend_decoder(self, caps: GPUCapabilities) -> str:
        """Recommend best decoder based on capabilities."""
        if "cuda" in caps.ffmpeg_hwaccels:
            return "cuda"
        if "qsv" in caps.ffmpeg_hwaccels:
            return "qsv"
        if "dxva2" in caps.ffmpeg_hwaccels:
            return "dxva2"
        if "d3d11va" in caps.ffmpeg_hwaccels:
            return "d3d11va"
        return "default"
    
    def _load_cache(self) -> Optional[GPUCapabilities]:
        """Load capabilities from cache file."""
        try:
            cache_path = Path(self.CACHE_FILE)
            if not cache_path.exists():
                return None
            
            with open(cache_path, "r") as f:
                data = json.load(f)
            
            gpus = [GPUInfo(**g) for g in data.get("gpus", [])]
            
            return GPUCapabilities(
                has_gpu=data.get("has_gpu", False),
                gpus=gpus,
                recommended_encoder=data.get("recommended_encoder", "libx264"),
                recommended_decoder=data.get("recommended_decoder", "default"),
                ffmpeg_hwaccels=data.get("ffmpeg_hwaccels", []),
                ffmpeg_encoders=data.get("ffmpeg_encoders", []),
            )
            
        except Exception as e:
            logger.warning("cache_load_failed", error=str(e))
            return None
    
    def _save_cache(self, caps: GPUCapabilities):
        """Save capabilities to cache file."""
        try:
            cache_path = Path(self.CACHE_FILE)
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "has_gpu": caps.has_gpu,
                "gpus": [
                    {
                        "index": g.index,
                        "name": g.name,
                        "driver_version": g.driver_version,
                        "memory_total_mb": g.memory_total_mb,
                        "supports_nvenc": g.supports_nvenc,
                        "supports_hevc_nvenc": g.supports_hevc_nvenc,
                        "supports_cuvid": g.supports_cuvid,
                    }
                    for g in caps.gpus
                ],
                "recommended_encoder": caps.recommended_encoder,
                "recommended_decoder": caps.recommended_decoder,
                "ffmpeg_hwaccels": caps.ffmpeg_hwaccels,
                "ffmpeg_encoders": caps.ffmpeg_encoders,
            }
            
            with open(cache_path, "w") as f:
                json.dump(data, f, indent=2)
            
            logger.info("gpu_cache_saved", path=str(cache_path))
            
        except Exception as e:
            logger.warning("cache_save_failed", error=str(e))
    
    def get_encoding_args(self) -> List[str]:
        """Get FFmpeg encoding arguments for optimal performance."""
        caps = self.get_capabilities()
        
        encoder = caps.recommended_encoder
        
        if encoder == "h264_nvenc":
            return [
                "-c:v", "h264_nvenc",
                "-preset", "p4",  # Balanced preset
                "-rc", "vbr",
                "-cq", "23",
            ]
        elif encoder == "h264_qsv":
            return [
                "-c:v", "h264_qsv",
                "-preset", "medium",
                "-global_quality", "23",
            ]
        else:
            return [
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "23",
            ]


# Global detector instance
gpu_detector = GPUCapabilityDetector()
