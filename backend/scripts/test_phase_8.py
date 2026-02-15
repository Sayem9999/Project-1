import asyncio
from app.services.post_production_depth import (
    build_lower_third_filter,
    build_kinetic_highlight_filters
)

def test_graphics_pipeline():
    print("🎬 Testing Phase 8: Social Graphics Logic...")
    
    # 1. Test Animated Lower Thirds
    print("\n[Graphics] Verifying Lower-Third Animations...")
    lt_filters = build_lower_third_filter("John Doe", "Founder of ProEdit")
    print(f" > Generated LT Filters: {lt_filters}")
    
    assert len(lt_filters) == 2, "Should have both title and subtitle filters"
    assert "if(lt(t,0.5)" in lt_filters[0], "Title slide-in animation missing!"
    assert "if(lt(t,0.6)" in lt_filters[1], "Subtitle staggered animation missing!"
    
    # 2. Test Kinetic Word Highlights
    print("\n[Graphics] Verifying Kinetic Word Highlights...")
    word_timings = [
        {"word": "AMAZING", "start": 1.5, "end": 2.2, "should_highlight": True},
        {"word": "results", "start": 2.2, "end": 2.8, "should_highlight": False}
    ]
    kinetic_filters = build_kinetic_highlight_filters(word_timings, highlight_color="#00FF00")
    print(f" > Generated Kinetic Filters: {kinetic_filters}")
    
    assert len(kinetic_filters) == 1, "Only one word should be highlighted"
    assert "AMAZING" in kinetic_filters[0], "Word text missing!"
    assert "0x00FF00" in kinetic_filters[0], "Highlight color mismatch!"
    assert "between(t,1.5,2.2)" in kinetic_filters[0], "Timing incorrect!"
    
    print("\n✅ Phase 8 Verification PASSED!")

if __name__ == "__main__":
    test_graphics_pipeline()
