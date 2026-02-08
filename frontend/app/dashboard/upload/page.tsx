'use client';
import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import Navbar from '@/components/ui/Navbar';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? 'http://localhost:8000/api';

export default function UploadPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [dragActive, setDragActive] = useState(false);

  const [settings, setSettings] = useState({
    theme: 'cinematic',
    pacing: 'medium',
    mood: 'professional',
    ratio: '16:9',
  });

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.type.startsWith('video/')) {
      setFile(droppedFile);
      setPreview(URL.createObjectURL(droppedFile));
    }
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) {
      setFile(selected);
      setPreview(URL.createObjectURL(selected));
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setError('');

    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('theme', settings.theme);
      formData.append('pacing', settings.pacing);
      formData.append('mood', settings.mood);
      formData.append('ratio', settings.ratio);

      const res = await fetch(`${API_BASE}/jobs/upload`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || 'Upload failed');
      }

      const job = await res.json();
      router.push(`/jobs/${job.id}`);
    } catch (err: any) {
      setError(err.message || 'Upload failed');
      setUploading(false);
    }
  };

  const themes = [
    { id: 'cinematic', label: 'Cinematic', icon: '🎬' },
    { id: 'energetic', label: 'Energetic', icon: '⚡' },
    { id: 'minimal', label: 'Minimal', icon: '✨' },
    { id: 'documentary', label: 'Documentary', icon: '📹' },
  ];

  const pacings = [
    { id: 'slow', label: 'Slow & Dramatic' },
    { id: 'medium', label: 'Balanced' },
    { id: 'fast', label: 'Fast & Punchy' },
  ];

  const ratios = [
    { id: '16:9', label: '16:9 YouTube' },
    { id: '9:16', label: '9:16 TikTok' },
    { id: '1:1', label: '1:1 Instagram' },
  ];

  return (
    <main className="min-h-screen bg-[#0a0a0f]">
      <Navbar />

      <div className="container mx-auto px-6 pt-24 pb-16">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-10">
            <h1 className="text-3xl md:text-4xl font-bold text-white mb-2">
              Create New Project
            </h1>
            <p className="text-gray-400">Upload your video and let AI do the magic</p>
          </div>

          <div className="grid lg:grid-cols-2 gap-8">
            {/* Upload Zone */}
            <div
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              className={`relative rounded-2xl border-2 border-dashed transition-all ${dragActive
                ? 'border-cyan-500 bg-cyan-500/10'
                : file
                  ? 'border-emerald-500/50 bg-emerald-500/5'
                  : 'border-white/20 bg-[#12121a] hover:border-white/40'
                }`}
            >
              {preview ? (
                <div className="relative rounded-xl overflow-hidden bg-black" style={{ maxHeight: '300px' }}>
                  <video src={preview} className="w-full h-full object-contain max-h-[300px]" controls />
                  <button
                    onClick={() => { setFile(null); setPreview(null); }}
                    className="absolute top-3 right-3 p-2 bg-black/50 rounded-lg text-white hover:bg-black/70 transition-colors"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                  <div className="absolute bottom-3 left-3 right-3 flex items-center justify-between">
                    <span className="px-3 py-1 bg-black/50 rounded-lg text-sm text-white truncate max-w-[200px]">
                      {file?.name}
                    </span>
                    <span className="px-3 py-1 bg-emerald-500/20 rounded-lg text-sm text-emerald-400">
                      Ready
                    </span>
                  </div>
                </div>
              ) : (
                <label className="flex flex-col items-center justify-center p-12 cursor-pointer aspect-video">
                  <div className="w-16 h-16 mb-4 rounded-full bg-gradient-to-br from-cyan-500/20 to-violet-500/20 flex items-center justify-center">
                    <svg className="w-8 h-8 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                  </div>
                  <p className="text-lg font-medium text-white mb-1">Drop your video here</p>
                  <p className="text-sm text-gray-400 mb-4">or click to browse</p>
                  <span className="px-4 py-2 bg-white/10 rounded-lg text-sm text-white">
                    Select File
                  </span>
                  <p className="text-xs text-gray-500 mt-4">MP4, MOV, AVI up to 100MB</p>
                  <input type="file" accept="video/*" onChange={handleFileChange} className="hidden" />
                </label>
              )}
            </div>

            {/* Settings */}
            <div className="space-y-6">
              {/* Theme */}
              <div>
                <label className="block text-sm font-medium text-white mb-3">Style Theme</label>
                <div className="grid grid-cols-2 gap-3">
                  {themes.map((theme) => (
                    <button
                      key={theme.id}
                      onClick={() => setSettings(s => ({ ...s, theme: theme.id }))}
                      className={`p-4 rounded-xl border text-left transition-all ${settings.theme === theme.id
                        ? 'border-cyan-500 bg-cyan-500/10'
                        : 'border-white/10 bg-[#12121a] hover:border-white/20'
                        }`}
                    >
                      <span className="text-2xl mb-2 block">{theme.icon}</span>
                      <span className="text-sm font-medium text-white">{theme.label}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Pacing */}
              <div>
                <label className="block text-sm font-medium text-white mb-3">Pacing</label>
                <div className="flex gap-2">
                  {pacings.map((pace) => (
                    <button
                      key={pace.id}
                      onClick={() => setSettings(s => ({ ...s, pacing: pace.id }))}
                      className={`flex-1 py-2.5 px-3 rounded-lg border text-sm font-medium transition-all ${settings.pacing === pace.id
                        ? 'border-cyan-500 bg-cyan-500/10 text-white'
                        : 'border-white/10 text-gray-400 hover:text-white'
                        }`}
                    >
                      {pace.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Aspect Ratio */}
              <div>
                <label className="block text-sm font-medium text-white mb-3">Aspect Ratio</label>
                <div className="flex gap-2">
                  {ratios.map((r) => (
                    <button
                      key={r.id}
                      onClick={() => setSettings(s => ({ ...s, ratio: r.id }))}
                      className={`flex-1 py-2.5 px-3 rounded-lg border text-sm font-medium transition-all ${settings.ratio === r.id
                        ? 'border-cyan-500 bg-cyan-500/10 text-white'
                        : 'border-white/10 text-gray-400 hover:text-white'
                        }`}
                    >
                      {r.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Error */}
              {error && (
                <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
                  {error}
                </div>
              )}

              {/* Submit */}
              <button
                onClick={handleUpload}
                disabled={!file || uploading}
                className={`w-full py-4 rounded-xl text-lg font-semibold transition-all ${file && !uploading
                  ? 'bg-gradient-to-r from-cyan-500 to-violet-500 text-white hover:opacity-90'
                  : 'bg-white/10 text-gray-500 cursor-not-allowed'
                  }`}
              >
                {uploading ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Processing...
                  </span>
                ) : (
                  '✨ Start AI Editing'
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
