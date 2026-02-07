import subprocess


def run_ffmpeg(args: list[str]) -> None:
    process = subprocess.run(["ffmpeg", "-y", *args], capture_output=True, text=True)
    if process.returncode != 0:
        raise RuntimeError(process.stderr)


def remove_silence(input_path: str, output_path: str) -> None:
    run_ffmpeg([
        "-i", input_path,
        "-af", "silenceremove=stop_periods=-1:stop_duration=0.55:stop_threshold=-42dB",
        output_path,
    ])


def burn_subtitles(input_path: str, subtitle_path: str, output_path: str) -> None:
    run_ffmpeg([
        "-i", input_path,
        "-vf", f"subtitles={subtitle_path}:force_style='FontName=Inter,FontSize=18,Outline=1,Shadow=0'",
        output_path,
    ])


def normalize_loudness(input_path: str, output_path: str) -> None:
    run_ffmpeg([
        "-i", input_path,
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
        output_path,
    ])


def normalize_aspect_ratio(input_path: str, output_path: str) -> None:
    run_ffmpeg([
        "-i", input_path,
        "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
        output_path,
    ])
