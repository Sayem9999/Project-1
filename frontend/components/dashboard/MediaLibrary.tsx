'use client';
import { useState } from 'react';
import { Search, Folder, Grid, List, MoreVertical, Play, HardDrive, Filter } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import Image from 'next/image';

interface MediaAsset {
    id: string;
    name: string;
    type: 'video' | 'audio' | 'image';
    thumbnail?: string;
    size: string;
    date: string;
}

const MOCK_ASSETS: MediaAsset[] = [
    { id: '1', name: 'Raw_Footage_01.mp4', type: 'video', size: '45.2 MB', date: '2 hours ago' },
    { id: '2', name: 'B-Roll_City_Skyline.mp4', type: 'video', size: '128 MB', date: 'Yesterday' },
    { id: '3', name: 'Background_Music_Vibe.mp3', type: 'audio', size: '4.5 MB', date: '3 days ago' },
    { id: '4', name: 'Logo_Final_White.png', type: 'image', size: '1.2 MB', date: '1 week ago' },
];

export default function MediaLibrary() {
    const [view, setView] = useState<'grid' | 'list'>('grid');
    const [search, setSearch] = useState('');

    return (
        <div className="space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="relative flex-1 max-w-md">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                    <input
                        type="text"
                        placeholder="Search assets..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="w-full pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded-xl text-sm focus:outline-none focus:border-brand-cyan/50 transition-colors"
                    />
                </div>

                <div className="flex items-center gap-2">
                    <div className="flex items-center bg-white/5 rounded-lg p-1 border border-white/10">
                        <button
                            onClick={() => setView('grid')}
                            className={`p-1.5 rounded-md transition-colors ${view === 'grid' ? 'bg-white/10 text-white' : 'text-gray-500 hover:text-gray-300'}`}
                        >
                            <Grid className="w-4 h-4" />
                        </button>
                        <button
                            onClick={() => setView('list')}
                            className={`p-1.5 rounded-md transition-colors ${view === 'list' ? 'bg-white/10 text-white' : 'text-gray-500 hover:text-gray-300'}`}
                        >
                            <List className="w-4 h-4" />
                        </button>
                    </div>
                    <button className="flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-sm text-gray-400 hover:text-white transition-colors">
                        <Filter className="w-4 h-4" />
                        <span>Filter</span>
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-brand-cyan/10 border border-brand-cyan/20 rounded-2xl p-4 flex items-center gap-4">
                    <div className="w-10 h-10 rounded-xl bg-brand-cyan/20 flex items-center justify-center text-brand-cyan">
                        <HardDrive className="w-5 h-5" />
                    </div>
                    <div>
                        <div className="text-[10px] text-gray-500 font-bold uppercase tracking-wider">Storage</div>
                        <div className="text-sm font-bold text-white">4.2 GB / 10 GB</div>
                    </div>
                </div>
                {/* Placeholder stats */}
                <div className="bg-white/5 border border-white/10 rounded-2xl p-4 flex items-center gap-4 hover:bg-white/10 transition-colors cursor-pointer group">
                    <div className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center group-hover:bg-brand-violet/20 group-hover:text-brand-violet transition-colors">
                        <Folder className="w-5 h-5" />
                    </div>
                    <div>
                        <div className="text-[10px] text-gray-500 font-bold uppercase tracking-wider">Assets</div>
                        <div className="text-sm font-bold text-white">124 Items</div>
                    </div>
                </div>
            </div>

            {view === 'grid' ? (
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
                    {MOCK_ASSETS.map((asset) => (
                        <Card key={asset.id} className="p-0 group relative overflow-hidden" gradient>
                            <div className="aspect-video bg-black/40 relative flex items-center justify-center border-b border-white/5">
                                {asset.type === 'video' ? (
                                    <Play className="w-8 h-8 text-white/20 group-hover:text-white/60 transition-colors" />
                                ) : (
                                    <Folder className="w-8 h-8 text-white/20" />
                                )}
                                <div className="absolute inset-0 bg-brand-cyan opacity-0 group-hover:opacity-10 transition-opacity" />
                            </div>
                            <div className="p-3">
                                <div className="flex items-center justify-between mb-1">
                                    <span className="text-sm font-medium truncate pr-2 text-gray-200">{asset.name}</span>
                                    <button className="text-gray-500 hover:text-white">
                                        <MoreVertical className="w-4 h-4" />
                                    </button>
                                </div>
                                <div className="flex items-center justify-between text-[10px] text-gray-500">
                                    <span>{asset.size}</span>
                                    <span>{asset.date}</span>
                                </div>
                            </div>
                        </Card>
                    ))}
                    {/* Upload Placeholder */}
                    <div className="aspect-square md:aspect-auto border-2 border-dashed border-white/5 rounded-2xl flex flex-col items-center justify-center p-4 hover:border-brand-cyan/50 hover:bg-brand-cyan/5 transition-all group cursor-pointer">
                        <div className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center mb-3 group-hover:bg-brand-cyan/20 group-hover:text-brand-cyan transition-colors">
                            <Play className="w-5 h-5 rotate-90" />
                        </div>
                        <span className="text-xs font-bold text-gray-500 group-hover:text-brand-cyan transition-colors">Upload Asset</span>
                    </div>
                </div>
            ) : (
                <div className="glass-panel border-white/5 rounded-2xl overflow-hidden">
                    <table className="w-full text-left">
                        <thead>
                            <tr className="border-b border-white/5 text-[10px] uppercase tracking-widest text-gray-500 bg-white/5">
                                <th className="px-6 py-4 font-bold">Asset Name</th>
                                <th className="px-6 py-4 font-bold">Size</th>
                                <th className="px-6 py-4 font-bold">Modified</th>
                                <th className="px-6 py-4"></th>
                            </tr>
                        </thead>
                        <tbody>
                            {MOCK_ASSETS.map((asset) => (
                                <tr key={asset.id} className="border-b border-white/5 hover:bg-white/5 transition-colors group">
                                    <td className="px-6 py-4 flex items-center gap-3">
                                        <Play className="w-4 h-4 text-gray-500 group-hover:text-brand-cyan" />
                                        <span className="text-sm font-medium text-gray-300">{asset.name}</span>
                                    </td>
                                    <td className="px-6 py-4 text-sm text-gray-500">{asset.size}</td>
                                    <td className="px-6 py-4 text-sm text-gray-500">{asset.date}</td>
                                    <td className="px-6 py-4 text-right">
                                        <button className="text-gray-500 hover:text-white">
                                            <MoreVertical className="w-4 h-4" />
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}
