"use client";
import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
  Upload,
  Sparkles,
  Zap,
  Video,
  CheckCircle2,
  X,
  BrainCircuit,
  ScanSearch,
  Layers,
  ArrowLeft,
  Activity,
} from "lucide-react";
import { apiUpload, apiRequest, ApiError, clearAuth } from "@/lib/api";
import { Button } from "@/components/ui/Button";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";

const VIBES = [
  {
    id: "viral",
    label: "Viral Moment",
    icon: <Zap className="w-5 h-5 text-yellow-400" />,
    theme: "energetic",
    description: "Fast-paced, high energy, perfect for social.",
  },
  {
    id: "cinematic",
    label: "Movie Feel",
    icon: <Video className="w-5 h-5 text-indigo-400" />,
    theme: "cinematic",
    description: "Deep colors, smooth transitions, atmospheric.",
  },
  {
    id: "clean",
    label: "Pro Minimalist",
    icon: <Sparkles className="w-5 h-5 text-cyan-400" />,
    theme: "minimal",
    description: "Polished, clear, and professional focus.",
  },
];

export default function CreatorPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [selectedVibe, setSelectedVibe] = useState(VIBES[0]);
  const [uploading, setUploading] = useState(false);
  const [isScanning, setIsScanning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState("");
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(e.type === "dragenter" || e.type === "dragover");
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile?.type.startsWith("video/")) {
      setFile(droppedFile);
      setPreview(URL.createObjectURL(droppedFile));
      setIsScanning(true);
      setTimeout(() => setIsScanning(false), 2000);
    }
  }, []);

  const handleGo = async () => {
    if (!file) return;
    setUploading(true);
    setProgress(0);
    setError("");

    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login?redirect=/creator");
      return;
    }

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("theme", selectedVibe.theme);
      formData.append(
        "pacing",
        selectedVibe.id === "viral" ? "fast" : "medium",
      );
      formData.append("mood", selectedVibe.theme);
      formData.append("platform", "social");
      formData.append("tier", "pro");

      const { promise } = apiUpload<{ id: number }>("/jobs/upload", {
        body: formData,
        auth: true,
        onProgress: (p) => setProgress(Math.floor(p * 0.8)),
      });
      const job = await promise;

      setProgress(100);

      router.push(`/jobs/${job.id}`);
    } catch (err: any) {
      if (err instanceof ApiError && err.isAuth) {
        clearAuth();
        router.push("/login?redirect=/creator");
        return;
      }
      setError(
        err instanceof ApiError
          ? err.message
          : "Something went wrong. Try a smaller file?",
      );
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-obsidian-950 text-white selection:bg-brand-cyan/30 overflow-hidden relative">
      {/* Ambient Experience Layer */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[80vw] h-[80vw] bg-brand-cyan/5 rounded-full blur-[120px] animate-pulse-slow" />
        <div
          className="absolute bottom-[-10%] right-[-10%] w-[80vw] h-[80vw] bg-brand-violet/5 rounded-full blur-[120px] animate-pulse-slow"
          style={{ animationDelay: "2s" }}
        />
        <div className="absolute inset-0 bg-grid-pattern opacity-10" />
      </div>

      {/* Top Navigation */}
      <div className="relative z-20 flex items-center justify-between p-6 md:p-10">
        <Link
          href="/dashboard"
          className="flex items-center gap-3 text-gray-500 hover:text-white transition-all group"
        >
          <div className="p-2.5 rounded-xl bg-white/5 border border-white/5 group-hover:bg-white/10 transition-colors">
            <ArrowLeft className="w-5 h-5" />
          </div>
          <span className="text-[10px] font-black uppercase tracking-[0.3em] hidden sm:block">
            Back to Lab
          </span>
        </Link>

        <div className="flex items-center gap-3">
          <Activity className="w-4 h-4 text-emerald-400" />
          <span className="text-[10px] font-black text-gray-500 uppercase tracking-widest">
            Pipeline Operational
          </span>
        </div>
      </div>

      <main className="max-w-5xl mx-auto px-6 pb-32 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1 }}
          className="text-center mb-16"
        >
          <div className="inline-flex items-center gap-3 mb-6">
            <div className="px-3 py-1 rounded-full bg-brand-cyan/10 border border-brand-cyan/30 text-[10px] font-black uppercase tracking-widest text-brand-cyan">
              EXPRESS_INITIATOR
            </div>
            <span className="text-[10px] font-bold text-gray-600 uppercase tracking-widest">
              v4.0.2 Stable
            </span>
          </div>
          <h1 className="text-4xl md:text-7xl font-black tracking-tighter text-white mb-6 uppercase">
            Drop it.{" "}
            <span className="bg-gradient-to-r from-brand-cyan to-brand-violet bg-clip-text text-transparent italic">
              Vibe it.
            </span>{" "}
            Done.
          </h1>
          <p className="text-gray-500 max-w-2xl mx-auto text-lg font-bold leading-relaxed">
            The world&apos;s most lethal edit engine. Zero configuration.
            Maximum output. Upload your footage and witness true multi-agent
            alignment.
          </p>
        </motion.div>

        <AnimatePresence mode="wait">
          {!file ? (
            <motion.label
              key="dropzone"
              initial={{ opacity: 0, scale: 0.98 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 1.02 }}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              className={`
                                block w-full aspect-[21/9] rounded-[48px] border-2 border-dashed transition-all duration-700 cursor-pointer
                                flex flex-col items-center justify-center p-12 text-center relative overflow-hidden group
                                ${dragActive ? "bg-brand-cyan/10 border-brand-cyan" : "bg-white/[0.02] border-white/5 hover:bg-white/[0.04] hover:border-white/10"}
                            `}
            >
              <div className="absolute inset-0 bg-gradient-to-br from-brand-cyan/5 via-transparent to-brand-violet/5 opacity-0 group-hover:opacity-100 transition-opacity" />
              <div className="w-24 h-24 rounded-[32px] bg-white/5 flex items-center justify-center mb-8 relative z-10 transition-all duration-500 group-hover:scale-110 group-hover:rotate-6">
                <Upload
                  className={`w-10 h-10 ${dragActive ? "text-brand-cyan animate-bounce" : "text-gray-600 group-hover:text-brand-cyan"}`}
                />
              </div>
              <h2 className="text-3xl font-black text-white mb-3 tracking-tight relative z-10">
                Deploy Raw Media
              </h2>
              <p className="text-[10px] font-black text-gray-600 uppercase tracking-[0.3em] relative z-10">
                BROWSE_FS OR DRAG_DROP
              </p>
              <input
                type="file"
                className="hidden"
                accept="video/*"
                onChange={(e) => {
                  const f = e.target.files?.[0];
                  if (f) {
                    setFile(f);
                    setPreview(URL.createObjectURL(f));
                    setIsScanning(true);
                    setTimeout(() => setIsScanning(false), 2000);
                  }
                }}
              />
            </motion.label>
          ) : isScanning ? (
            <motion.div
              key="scanning"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="glass-panel border-brand-cyan/20 rounded-[48px] p-24 flex flex-col items-center justify-center gap-8 bg-obsidian-900/50"
            >
              <div className="relative">
                <BrainCircuit className="w-20 h-20 text-brand-cyan animate-pulse" />
                <div className="absolute inset-0 bg-brand-cyan/20 blur-[60px] animate-pulse" />
              </div>
              <div className="text-center">
                <h3 className="text-3xl font-black text-white mb-2 uppercase tracking-tight">
                  Mapping Neural Beats
                </h3>
                <p className="text-[10px] font-black text-gray-500 uppercase tracking-[0.2em]">
                  Engaging Hollywood Agents to map visual flow...
                </p>
              </div>
              <div className="w-80 h-1.5 bg-white/5 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: "100%" }}
                  transition={{ duration: 2, ease: "easeInOut" }}
                  className="h-full bg-brand-cyan shadow-[0_0_15px_rgba(6,182,212,0.8)]"
                />
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="editor"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-12"
            >
              {/* Analysis Result Card */}
              <div className="glass-panel rounded-[40px] p-6 pr-10 flex flex-col md:flex-row items-center gap-8 border-white/5 relative overflow-hidden group">
                <div className="absolute inset-y-0 left-0 w-1 bg-brand-cyan" />
                <div className="w-full md:w-72 aspect-video rounded-[24px] bg-black overflow-hidden relative border border-white/5 shadow-2xl transition-transform duration-700 group-hover:scale-[1.02]">
                  <video
                    src={preview!}
                    className="w-full h-full object-cover opacity-60 group-hover:opacity-80 transition-opacity"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent" />
                  <button
                    onClick={() => {
                      setFile(null);
                      setPreview(null);
                    }}
                    className="absolute top-4 right-4 p-2 bg-black/60 hover:bg-black text-white rounded-full backdrop-blur-xl transition-all border border-white/10"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
                <div className="flex-1 text-center md:text-left py-4">
                  <div className="flex items-center gap-3 mb-3 justify-center md:justify-start">
                    <ScanSearch className="w-4 h-4 text-brand-cyan" />
                    <span className="text-[10px] font-black uppercase tracking-[0.3em] text-cyan-400">
                      TELEMETRY_SYNC_OK
                    </span>
                  </div>
                  <h3 className="text-2xl font-black text-white mb-2 tracking-tight truncate max-w-sm">
                    {file.name}
                  </h3>
                  <p className="text-[10px] font-bold text-gray-600 uppercase tracking-widest leading-loose">
                    {(file.size / 1024 / 1024).toFixed(1)} MB • 24fps •
                    Intra-frame Mesh detected
                  </p>
                  <div className="mt-8 flex items-center gap-3 text-emerald-400 text-[10px] font-black uppercase tracking-widest justify-center md:justify-start">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Aligned for Pro Deployment</span>
                  </div>
                </div>
              </div>

              {/* Vibe Selection */}
              <div className="space-y-8">
                <div className="flex items-center gap-4 px-2">
                  <Layers className="w-5 h-5 text-brand-violet" />
                  <h3 className="text-xl font-black text-white uppercase tracking-widest">
                    Select Narrative Engine
                  </h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {VIBES.map((v) => (
                    <button
                      key={v.id}
                      onClick={() => setSelectedVibe(v)}
                      className={`
                                                p-8 rounded-[32px] border text-left transition-all duration-700 relative overflow-hidden group/btn
                                                ${
                                                  selectedVibe.id === v.id
                                                    ? "bg-white/[0.06] border-brand-cyan/30 shadow-2xl shadow-brand-cyan/5 scale-105"
                                                    : "bg-white/[0.02] border-white/5 hover:border-white/10 hover:bg-white/[0.04]"
                                                }
                                            `}
                    >
                      {selectedVibe.id === v.id && (
                        <motion.div
                          layoutId="vibe-bg"
                          className="absolute inset-0 bg-gradient-to-br from-brand-cyan/10 via-brand-violet/5 to-transparent"
                        />
                      )}

                      <div
                        className={`w-12 h-12 rounded-[18px] flex items-center justify-center mb-6 bg-white/5 relative z-10 transition-all duration-700 group-hover/btn:scale-110 group-hover/btn:rotate-12 ${selectedVibe.id === v.id ? "bg-brand-cyan/10 shadow-lg shadow-brand-cyan/10" : ""}`}
                      >
                        {v.icon}
                      </div>
                      <h4 className="font-black text-white text-lg mb-2 relative z-10 uppercase tracking-tight">
                        {v.label}
                      </h4>
                      <p className="text-[10px] font-bold text-gray-500 uppercase tracking-widest leading-relaxed relative z-10">
                        {v.description}
                      </p>

                      {selectedVibe.id === v.id && (
                        <motion.div
                          initial={{ opacity: 0, scale: 0 }}
                          animate={{ opacity: 1, scale: 1 }}
                          className="absolute top-6 right-6 z-10"
                        >
                          <CheckCircle2 className="w-6 h-6 text-brand-cyan" />
                        </motion.div>
                      )}
                    </button>
                  ))}
                </div>
              </div>

              {/* Initialization Action */}
              <div className="pt-12 border-t border-white/5">
                {error && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.98 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="mb-8 p-6 rounded-[32px] bg-red-500/10 border border-red-500/20 text-red-400 text-[10px] font-black uppercase tracking-widest text-center"
                  >
                    {error}
                  </motion.div>
                )}

                <Button
                  onClick={handleGo}
                  loading={uploading}
                  variant="glow"
                  className="w-full h-20 rounded-[32px] font-black text-xl tracking-[0.2em] group relative overflow-hidden"
                >
                  <div className="absolute inset-0 bg-white/10 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000" />
                  <span className="relative z-10 flex items-center justify-center gap-4">
                    {uploading ? (
                      <>
                        <div className="w-6 h-6 border-4 border-black/20 border-t-black rounded-full animate-spin" />
                        <span>
                          {progress < 90
                            ? `CALCULATING_ALGORITHMS... ${progress}%`
                            : "FINALIZING_RENDER..."}
                        </span>
                      </>
                    ) : (
                      <>
                        <span>INITIALIZE PIPELINE</span>
                        <Sparkles className="w-6 h-6 animate-pulse" />
                      </>
                    )}
                  </span>
                </Button>

                <div className="flex items-center justify-center gap-6 mt-10">
                  <div className="h-px bg-white/5 flex-1" />
                  <p className="text-gray-600 text-[10px] font-black uppercase tracking-[0.4em] whitespace-nowrap">
                    1 CREDIT REQ • APPROX 270S EXP
                  </p>
                  <div className="h-px bg-white/5 flex-1" />
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Technical Footnote */}
        {!file && (
          <div className="mt-20 flex flex-wrap justify-center gap-16 opacity-30 grayscale hover:grayscale-0 hover:opacity-100 transition-all duration-1000">
            <div className="flex items-center gap-3">
              <Sparkles className="w-5 h-5 text-brand-cyan" />
              <span className="font-black tracking-[0.3em] text-[10px] uppercase">
                Hollywood Agents v4
              </span>
            </div>
            <div className="flex items-center gap-3">
              <Zap className="w-5 h-5 text-brand-violet" />
              <span className="font-black tracking-[0.3em] text-[10px] uppercase">
                Neural Color Match
              </span>
            </div>
            <div className="flex items-center gap-3">
              <Video className="w-5 h-5 text-emerald-400" />
              <span className="font-black tracking-[0.3em] text-[10px] uppercase">
                Auto QC Integrity
              </span>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
