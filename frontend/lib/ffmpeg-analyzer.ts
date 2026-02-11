import { FFmpeg } from '@ffmpeg/ffmpeg';
import { fetchFile, toBlobURL } from '@ffmpeg/util';

export interface SceneInfo {
    start_time: number;
    end_time: number;
    duration: number;
    scene_number: number;
}

export interface MediaIntelligence {
    visual: {
        metadata: {
            duration: number;
            width: number;
            height: number;
            has_audio: boolean;
        };
        scenes: SceneInfo[];
        avg_shot_length: number | null;
    };
    audio: {
        overall_lufs: number;
        overall_peak: number;
        needs_normalization: boolean;
    };
}

class FfmpegAnalyzer {
    private ffmpeg: FFmpeg | null = null;
    private loaded = false;

    async load() {
        if (this.loaded) return;

        this.ffmpeg = new FFmpeg();
        const baseURL = 'https://unpkg.com/@ffmpeg/core@0.12.6/dist/umd';

        await this.ffmpeg.load({
            coreURL: await toBlobURL(`${baseURL}/ffmpeg-core.js`, 'text/javascript'),
            wasmURL: await toBlobURL(`${baseURL}/ffmpeg-core.wasm`, 'application/wasm'),
        });

        this.loaded = true;
    }

    async analyze(file: File, onProgress?: (percent: number) => void): Promise<MediaIntelligence> {
        if (!this.loaded) await this.load();
        const ffmpeg = this.ffmpeg!;

        // Write file to virtual FS
        const fileName = 'input.mp4';
        await ffmpeg.writeFile(fileName, await fetchFile(file));

        // 1. Get Metadata (using showinfo on first frame for simplicity or a quick ffprobe-like command)
        // Actually, we can get duration and basic info from a short run
        let duration = 0;
        let width = 0;
        let height = 0;

        ffmpeg.on('log', ({ message }) => {
            if (message.includes('Duration:')) {
                const match = message.match(/Duration: (\d+):(\d+):(\d+.\d+)/);
                if (match) {
                    duration = parseInt(match[1]) * 3600 + parseInt(match[2]) * 60 + parseFloat(match[3]);
                }
            }
            if (message.includes('Video:')) {
                const match = message.match(/(\d+)x(\d+)/);
                if (match) {
                    width = parseInt(match[1]);
                    height = parseInt(match[2]);
                }
            }
        });

        // Run a dummy command to trigger log parsing for metadata
        await ffmpeg.exec(['-i', fileName, '-f', 'null', '-']);

        // 2. Scene Detection
        const timestamps: number[] = [0];

        // Connect progress callback
        if (onProgress) {
            ffmpeg.on('progress', ({ progress }) => {
                // progress is 0-1
                onProgress(Math.round(progress * 100));
            });
        }

        ffmpeg.on('log', ({ message }) => {
            if (message.includes('pts_time:')) {
                const match = message.match(/pts_time:([\d.]+)/);
                if (match) {
                    timestamps.push(parseFloat(match[1]));
                }
            }
        });

        // Run scene detection filter
        // We use a higher threshold for speed/reliability in browser if needed
        await ffmpeg.exec([
            '-i', fileName,
            '-vf', "select='gt(scene,0.4)',showinfo",
            '-f', 'null',
            '-'
        ]);

        // Cleanup progress listener
        if (onProgress) {
            ffmpeg.on('progress', () => { });
        }

        if (duration > timestamps[timestamps.length - 1]) {
            timestamps.push(duration);
        }

        const uniqueTimestamps = Array.from(new Set(timestamps)).sort((a, b) => a - b);
        const scenes: SceneInfo[] = [];
        for (let i = 0; i < uniqueTimestamps.length - 1; i++) {
            const start = uniqueTimestamps[i];
            const end = uniqueTimestamps[i + 1];
            const d = end - start;
            if (d > 0.5) {
                scenes.push({
                    start_time: start,
                    end_time: end,
                    duration: d,
                    scene_number: scenes.length + 1
                });
            }
        }

        const avgShotLength = scenes.length > 0 ? duration / scenes.length : null;

        return {
            visual: {
                metadata: {
                    duration,
                    width,
                    height,
                    has_audio: true, // Optimistically assume for now or parse from logs
                },
                scenes,
                avg_shot_length: avgShotLength
            },
            audio: {
                overall_lufs: -14, // Placeholder for now, can be implemented with ebu r128 filter
                overall_peak: -1,
                needs_normalization: false
            }
        };
    }
}

export const ffmpegAnalyzer = new FfmpegAnalyzer();
