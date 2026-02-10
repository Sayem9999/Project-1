import React from 'react';

interface MediaStatsProps {
    intelligence?: {
        video?: {
            width?: number;
            height?: number;
            fps?: number;
            duration?: number;
            scene_count?: number;
            avg_motion_score?: number;
        };
        audio?: {
            loudness_i?: number;
            loudness_lra?: number;
            speech_percentage?: number;
            silent_regions?: number;
        };
    };
}

export default function MediaStats({ intelligence }: MediaStatsProps) {
    if (!intelligence) return null;

    const { video, audio } = intelligence;

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Video Stats */}
            <div className="bg-[#1a1a24] rounded-xl p-5 border border-white/5">
                <h3 className="text-sm font-semibold text-gray-400 mb-4 flex items-center gap-2">
                    <span className="text-cyan-400">📹</span> Visual Intelligence
                </h3>
                <div className="grid grid-cols-2 gap-y-4 gap-x-2">
                    <div>
                        <p className="text-xs text-gray-500">Resolution</p>
                        <p className="text-sm font-mono text-white">{video?.width || '?'}x{video?.height || '?'}</p>
                    </div>
                    <div>
                        <p className="text-xs text-gray-500">Frame Rate</p>
                        <p className="text-sm font-mono text-white">{video?.fps ? Math.round(video.fps) : '?'} FPS</p>
                    </div>
                    <div>
                        <p className="text-xs text-gray-500">Scene Count</p>
                        <p className="text-sm font-mono text-white">{video?.scene_count ?? 0} Scenes</p>
                    </div>
                    <div>
                        <p className="text-xs text-gray-500">Motion Score</p>
                        <p className="text-sm font-mono text-white">{(video?.avg_motion_score ?? 0).toFixed(2)} / 10</p>
                    </div>
                </div>
            </div>

            {/* Audio Stats */}
            <div className="bg-[#1a1a24] rounded-xl p-5 border border-white/5">
                <h3 className="text-sm font-semibold text-gray-400 mb-4 flex items-center gap-2">
                    <span className="text-violet-400">🔊</span> Audio Intelligence
                </h3>
                <div className="grid grid-cols-2 gap-y-4 gap-x-2">
                    <div>
                        <p className="text-xs text-gray-500">Integrated Loudness</p>
                        <p className="text-sm font-mono text-white">{audio?.loudness_i ? audio.loudness_i.toFixed(1) : '-'} LUFS</p>
                    </div>
                    <div>
                        <p className="text-xs text-gray-500">Dynamic Range</p>
                        <p className="text-sm font-mono text-white">{audio?.loudness_lra ? audio.loudness_lra.toFixed(1) : '-'} LU</p>
                    </div>
                    <div>
                        <p className="text-xs text-gray-500">Speech Detected</p>
                        <p className="text-sm font-mono text-white">{audio?.speech_percentage ? Math.round(audio.speech_percentage * 100) : 0}%</p>
                    </div>
                    <div>
                        <p className="text-xs text-gray-500">Silent Regions</p>
                        <p className="text-sm font-mono text-white">{audio?.silent_regions ?? 0}</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
