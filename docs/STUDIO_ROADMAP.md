# True Post-Production Depth Roadmap

Scope is intentionally narrowed to one objective: build pro-grade post-production depth.

## Target Outcome

ProEdit should deliver outputs with the depth of a professional editing studio through:
- Pro-grade timeline operations
- Real audio post
- Color pipeline quality
- Graphics pipeline quality

## Workstreams

### 1) Pro-Grade Timeline Operations

Capabilities:
- J/L cuts
- Nested sequences
- Multicam edit support
- Keyframed effects
- Speed ramps
- Advanced transitions

Backend Tickets:
- `TPD-BE-001` Timeline Model v2 (`j_cut`, `l_cut`, `nested_seq_id`, keyframe envelopes)
- `TPD-BE-002` Compiler support for keyframed transforms/effects in render graph
- `TPD-BE-003` Multicam sync + angle selection service
- `TPD-BE-004` Speed-ramp interpolation engine with optical-flow fallback
- `TPD-BE-005` Transition library with parameterized presets and QA checks

Frontend Tickets:
- `TPD-FE-001` Timeline editor with split audio/video handles (J/L cut UX)
- `TPD-FE-002` Nested sequence UI (create/open/collapse)
- `TPD-FE-003` Multicam monitor + angle cut controls
- `TPD-FE-004` Keyframe curve editor (position/scale/opacity/effect params)
- `TPD-FE-005` Speed ramp visual editor with preview markers

Acceptance Gate:
- User can create/edit/render J/L cuts, nested timelines, multicam decisions, keyframes, speed ramps, and advanced transitions without manual backend intervention.

### 2) Real Audio Post

Capabilities:
- Dialogue isolation
- Cleanup (noise/reverb handling)
- Ducking
- Loudness by platform target
- Mastering-grade processing chain

Backend Tickets:
- `TPD-BE-101` Dialogue stem extraction and speech isolation pipeline
- `TPD-BE-102` Noise/reverb cleanup chain with fallback profiles
- `TPD-BE-103` Auto-ducking engine tied to voice activity
- `TPD-BE-104` Platform loudness compliance (`YouTube`, `TikTok`, `IG`) with fail gates
- `TPD-BE-105` Mastering chain presets + per-job audio QA report

Frontend Tickets:
- `TPD-FE-101` Audio post controls (dialogue/music/effects balance)
- `TPD-FE-102` Loudness compliance panel with pass/fail per platform
- `TPD-FE-103` Ducking timeline visualization
- `TPD-FE-104` Audio issue inspector (clipping/noise/reverb warnings)

Acceptance Gate:
- Completed jobs include an audio QA report and pass platform loudness constraints unless explicitly overridden by user.

### 3) Color Pipeline

Capabilities:
- Scene matching
- Look LUT management
- Skin protection
- Consistent grading across shots

Backend Tickets:
- `TPD-BE-201` Scene-match analyzer (exposure/white-balance continuity)
- `TPD-BE-202` LUT registry and validation (safe load/fallback behavior)
- `TPD-BE-203` Skin-tone protection masks + confidence scoring
- `TPD-BE-204` Cross-shot grade consistency scorer with completion threshold

Frontend Tickets:
- `TPD-FE-201` LUT manager UI (upload/select/version/preview)
- `TPD-FE-202` Shot-to-shot color consistency heatmap
- `TPD-FE-203` Skin protection controls (strength + mask preview)

Acceptance Gate:
- Rendered output achieves configured scene consistency threshold and records grade decisions per shot.

### 4) Graphics Pipeline

Capabilities:
- Lower-thirds
- Motion graphics
- Subtitles with styling presets
- Subtitle QA

Backend Tickets:
- `TPD-BE-301` Graphics template engine (lower-thirds, title cards, callouts)
- `TPD-BE-302` Motion graphics compositor with timeline keyframe hooks
- `TPD-BE-303` Subtitle style preset system + per-platform constraints
- `TPD-BE-304` Subtitle QA (timing overlap, CPS, line length, safe area checks)

Frontend Tickets:
- `TPD-FE-301` Lower-third template picker/editor
- `TPD-FE-302` Motion graphics track UI + timing controls
- `TPD-FE-303` Subtitle preset manager + live preview
- `TPD-FE-304` Subtitle QA panel with fix suggestions

Acceptance Gate:
- Graphics and subtitles render deterministically from templates/presets and pass subtitle QA checks by default.

## Delivery Phases

Phase A:
- Timeline core (`TPD-BE/FE-001..005`)

Phase B:
- Audio post chain (`TPD-BE/FE-101..104`)

Phase C:
- Color system (`TPD-BE/FE-201..203`)

Phase D:
- Graphics + subtitle QA (`TPD-BE/FE-301..304`)

## Definition of Done

- All four workstreams are implemented.
- QA gates exist for audio/color/subtitles.
- Outputs are no longer “basic cut + export”; they reflect true post-production depth.
