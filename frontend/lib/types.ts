/**
 * Frontend Type Definitions
 * Mirrored from backend/app/schemas.py
 * Single Source of Truth: Backend
 */

export type JobStatus = 
  | "queued"
  | "processing"
  | "complete"
  | "failed"
  | "cancelled";

export type TransitionStyle = 
  | "cut"
  | "dissolve"
  | "wipe"
  | "crossfade"
  | "wipe_left"
  | "wipe_right"
  | "slide_left"
  | "slide_right";

export type SpeedProfile = "slow" | "balanced" | "fast";
export type SubtitlePreset = "platform_default" | "broadcast" | "social";
export type ColorProfile = "natural" | "cinematic" | "punchy";

export interface PostSettings {
  transition_style: TransitionStyle;
  transition_duration: number; // 0.1 to 1.5
  speed_profile: SpeedProfile;
  subtitle_preset: SubtitlePreset;
  color_profile: ColorProfile;
  skin_protect_strength: number; // 0.0 to 1.0
}



export interface MediaIntelligence {
  video?: {
    width?: number;
    height?: number;
    fps?: number;
    duration?: number;
    scene_count?: number;
    avg_motion_score?: number;
  };
  audio?: {
    duration?: number;
    sample_rate?: number;
    channels?: number;
    avg_loudness?: number;
    loudness_i?: number;
    loudness_lra?: number;
    speech_percentage?: number;
    silent_regions?: number;
  };
}

export interface QCResult {
  approved: boolean;
  feedback?: string;
  overall_score?: number;
  metrics?: {
    technical_integrity: number;
    aesthetic_appeal: number;
    pacing_flow: number;
    platform_optimization: number;
    audience_retention: number;
  };
}


export interface Violation {
  type: string;
  severity: string;
  timestamp?: number;
  description: string;
}

export interface BrandSafetyResult {
  is_safe: boolean;
  violations: Violation[];
  risk_score: number;
  recommendations: string[];
}

export interface Variant {
  id: string;
  type: string;
  content: {
      description: string;
      implementation: string;
      title?: string;
      hook_text?: string;
  };
  predicted_performance: number;
}

export interface ABTestResult {
  variants: Variant[];
  rankings: string[];
  rationale: string;
}

export interface Job {
  id: number;
  status: JobStatus;
  theme: string;
  tier?: string | null;
  credits_cost?: number | null;
  pacing?: string | null;
  mood?: string | null;
  ratio?: string | null;
  platform?: string | null;
  brand_safety?: string | null;
  cancel_requested?: boolean | null;
  progress_message: string;
  output_path?: string | null;
  thumbnail_path?: string | null;
  created_at: string; // ISO Date string
  updated_at?: string | null;

  // Phase 5 Fields
  media_intelligence?: MediaIntelligence | null;
  qc_result?: QCResult | null;
  director_plan?: Record<string, any> | null;
  brand_safety_result?: BrandSafetyResult | null;
  ab_test_result?: ABTestResult | null;
  performance_metrics?: Record<string, any> | null;
  post_settings?: PostSettings | null; // Use PostSettings instead of Record
  audio_qa?: Record<string, any> | null;
  color_qa?: Record<string, any> | null;
  subtitle_qa?: Record<string, any> | null;
}

export interface User {
  id: number;
  email: string;
  full_name?: string | null;
  avatar_url?: string | null;
  credits: number;
  is_admin: boolean;
}

export interface EditJobRequest {
  theme?: string;
  pacing?: string;
  mood?: string;
  ratio?: string;
  platform?: string;
  tier?: string;
  brand_safety?: string;
  transition_style?: TransitionStyle;
  transition_duration?: number;
  speed_profile?: SpeedProfile;
  subtitle_preset?: SubtitlePreset;
  color_profile?: ColorProfile;
  skin_protect_strength?: number;
}
