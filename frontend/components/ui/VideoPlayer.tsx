'use client';

interface VideoPlayerProps {
    src: string;
    poster?: string;
}

export function VideoPlayer({ src, poster }: VideoPlayerProps) {
    return (
        <div className="relative group rounded-xl overflow-hidden border border-white/10 shadow-2xl bg-black">
            <div className="absolute inset-0 bg-gradient-to-t from-black/50 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity z-10 pointer-events-none"></div>

            <video
                className="w-full aspect-video object-contain"
                controls
                playsInline
                poster={poster}
                preload="metadata"
            >
                <source src={src} type="video/mp4" />
                Your browser does not support the video tag.
            </video>
        </div>
    );
}
