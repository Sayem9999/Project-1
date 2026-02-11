from pydantic import BaseModel, Field
import json

class AudioOutput(BaseModel):
    """Output from ECHO - the Audio Engineer Agent."""
    ffmpeg_audio_filter: str = Field(..., description="FFmpeg audio filter chain")
    audio_character: str = Field(..., description="One-word descriptor")
    notes: str = Field(..., description="Brief sonic signature explanation")
    audio_tracks: list[dict] = Field(default=[], description="List of selected audio tracks")

def test_schema():
    print("--- Testing AudioOutput Schema (Standalone) ---")
    
    # Case 1: Minimal valid JSON
    data_min = {
        "ffmpeg_audio_filter": "anull",
        "audio_character": "Valid",
        "notes": "Test"
    }
    obj = AudioOutput(**data_min)
    print("Case 1 (Minimal) passed.")
    assert obj.audio_tracks == []

    # Case 2: With audio_tracks
    data_full = {
        "ffmpeg_audio_filter": "lowpass=f=100",
        "audio_character": "Dark",
        "notes": "Testing tracks",
        "audio_tracks": [{"id": "1", "name": "Track A"}]
    }
    obj = AudioOutput(**data_full)
    print("Case 2 (Full) passed.")
    assert len(obj.audio_tracks) == 1
    assert obj.audio_tracks[0]["name"] == "Track A"

    # Case 3: Verify it works with previous structure (empty tracks implicit)
    data_implicit = {
        "ffmpeg_audio_filter": "anull",
        "audio_character": "Implicit",
        "notes": "Implicit check"
    }
    obj = AudioOutput(**data_implicit)
    print("Case 3 (Implicit) passed.")
    assert obj.audio_tracks == []

    print("--- Test Complete ---")

if __name__ == "__main__":
    test_schema()
