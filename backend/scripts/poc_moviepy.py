from moviepy import ColorClip, TextClip, CompositeVideoClip, VideoFileClip
import os

def test_moviepy_render():
    print("Testing MoviePy rendering...")
    try:
        # Create a red background (HD)
        bg = ColorClip(size=(1280, 720), color=(255, 0, 0), duration=2)
        
        # Create text (requires ImageMagick usually, but we'll try)
        # If TextClip fails, it means ImageMagick is missing.
        try:
            txt = TextClip("MoviePy Test", fontsize=70, color='white')
            txt = txt.set_pos('center').set_duration(2)
            final = CompositeVideoClip([bg, txt])
        except Exception as e:
            print(f"TextClip failed (ImageMagick missing?): {e}")
            print("Fallback to simple color clip.")
            final = bg

        output_path = "moviepy_test.mp4"
        final.write_videofile(output_path, fps=24)
        
        if os.path.exists(output_path):
            print(f"SUCCESS: Rendered to {output_path}")
            os.remove(output_path)
            return True
        else:
            print("FAILURE: Output file not found.")
            return False
            
    except Exception as e:
        print(f"CRITICAL FAILURE: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_moviepy_render()
