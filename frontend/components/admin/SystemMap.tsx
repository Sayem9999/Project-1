'use client';
import { useEffect, useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Network, Terminal, Shield, Zap, Database, Cpu, Activity, Info, AlertTriangle } from 'lucide-react';
import { apiRequest } from '@/lib/api';

interface SystemNode {
    id: string;
    type: string;
    label: string;
    file?: string;
}

interface SystemGraph {
    nodes: SystemNode[];
    edges: any[];
    stats: {
        source_files: number;
        total_nodes: number;
        total_edges: number;
        lines_of_code: number;
    };
}

const TYPE_ICONS: Record<string, any> = {
    endpoint: Zap,
    model: Database,
    service: Cpu,
    agent: Shield,
    utility: Terminal,
};

const TYPE_COLORS: Record<string, string> = {
    endpoint: 'cyan',
    model: 'amber',
    service: 'indigo',
    agent: 'emerald',
    utility: 'slate',
};

export default function SystemMap() {
    const [data, setData] = useState<SystemGraph | null>(null);
    const [loading, setLoading] = useState(true);
    const [selectedNode, setSelectedNode] = useState<SystemNode | null>(null);
    const [activeFilter, setActiveFilter] = useState<string | 'all'>('all');

    useEffect(() => {
        const fetchGraph = async () => {
            try {
                const graph = await apiRequest<SystemGraph>('/maintenance/graph', { auth: true });
                setData(graph);
            } catch (err) {
                console.error('Failed to fetch system graph', err);
            } finally {
                setLoading(false);
            }
        };
        fetchGraph();
    }, []);

    const filteredNodes = useMemo(() => {
        if (!data) return [];
        if (activeFilter === 'all') return data.nodes;
        return data.nodes.filter(n => n.type === activeFilter);
    }, [data, activeFilter]);

    const stats = data?.stats;

    if (loading) {
        return (
            <div className="h-[600px] flex items-center justify-center">
                <div className="flex flex-col items-center gap-4">
                    <div className="w-12 h-12 border-4 border-brand-cyan border-t-transparent rounded-full animate-spin" />
                    <p className="text-gray-400 text-sm animate-pulse">Mapping Codebase Architecture...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <StatItem icon={Terminal} label="Files" value={stats?.source_files ?? 0} />
                <StatItem icon={Network} label="Nodes" value={stats?.total_nodes ?? 0} />
                <StatItem icon={Activity} label="LOC" value={stats?.lines_of_code?.toLocaleString() ?? 0} />
                <StatItem icon={Zap} label="Endpoints" value={data?.nodes.filter(n => n.type === 'endpoint').length ?? 0} />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                {/* Sidebar Filters */}
                <div className="space-y-4">
                    <div className="bg-slate-900/40 border border-white/10 rounded-3xl p-6 backdrop-blur-xl">
                        <h3 className="text-sm font-semibold text-gray-400 mb-4 uppercase tracking-widest">Filters</h3>
                        <div className="space-y-2">
                            <FilterButton
                                label="All Nodes"
                                active={activeFilter === 'all'}
                                onClick={() => setActiveFilter('all')}
                                type="all"
                            />
                            {Object.keys(TYPE_COLORS).map(type => (
                                <FilterButton
                                    key={type}
                                    label={type.charAt(0).toUpperCase() + type.slice(1)}
                                    active={activeFilter === type}
                                    onClick={() => setActiveFilter(type)}
                                    type={type}
                                />
                            ))}
                        </div>
                    </div>

                    <AnimatePresence>
                        {selectedNode && (
                            <motion.div
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                exit={{ opacity: 0, scale: 0.95 }}
                                className="bg-brand-cyan/5 border border-brand-cyan/20 rounded-3xl p-6 backdrop-blur-xl"
                            >
                                <div className="flex items-start justify-between mb-4">
                                    <div className={`p-2 rounded-xl bg-${TYPE_COLORS[selectedNode.type] || 'slate'}-500/10 text-${TYPE_COLORS[selectedNode.type] || 'slate'}-400`}>
                                        {(() => {
                                            const Icon = TYPE_ICONS[selectedNode.type] || Info;
                                            return <Icon className="w-5 h-5" />;
                                        })()}
                                    </div>
                                    <button onClick={() => setSelectedNode(null)} className="text-gray-500 hover:text-white transition-colors">
                                        &times;
                                    </button>
                                </div>
                                <h4 className="text-lg font-bold text-white mb-2">{selectedNode.label}</h4>
                                <div className="space-y-3 text-xs">
                                    <div className="flex items-center justify-between">
                                        <span className="text-gray-500">ID</span>
                                        <span className="font-mono text-gray-300">{selectedNode.id}</span>
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <span className="text-gray-500">Source File</span>
                                        <span className="text-brand-cyan truncate max-w-[150px]">{selectedNode.file?.split('\\').pop()}</span>
                                    </div>
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>

                {/* Graph Area */}
                <div className="lg:col-span-3 bg-slate-900/20 border border-white/10 rounded-3xl p-8 backdrop-blur-xl relative overflow-hidden min-h-[500px]">
                    {/* Neural Background Grid */}
                    <div className="absolute inset-0 opacity-10 pointer-events-none" style={{ backgroundImage: 'radial-gradient(circle, #06b6d4 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

                    <div className="relative grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 xl:grid-cols-5 gap-4">
                        <AnimatePresence mode='popLayout'>
                            {filteredNodes.map((node) => {
                                const Icon = TYPE_ICONS[node.type] || Info;
                                const color = TYPE_COLORS[node.type] || 'slate';
                                const isSelected = selectedNode?.id === node.id;

                                return (
                                    <motion.button
                                        key={node.id}
                                        layout
                                        initial={{ opacity: 0, scale: 0.8 }}
                                        animate={{ opacity: 1, scale: 1 }}
                                        exit={{ opacity: 0, scale: 0.8 }}
                                        whileHover={{ scale: 1.05 }}
                                        onClick={() => setSelectedNode(node)}
                                        className={`
                      relative group p-4 rounded-2xl border transition-all text-left
                      ${isSelected
                                                ? `bg-${color}-500/10 border-${color}-400/50 shadow-lg shadow-${color}-500/10`
                                                : 'bg-white/5 border-white/10 hover:border-white/20'
                                            }
                    `}
                                    >
                                        <div className={`
                      w-8 h-8 rounded-lg flex items-center justify-center mb-3 transition-colors
                      ${isSelected ? `bg-${color}-500 text-white` : `bg-${color}-500/10 text-${color}-400 group-hover:bg-${color}-500/20`}
                    `}>
                                            <Icon className="w-5 h-5" />
                                        </div>
                                        <div className="text-[10px] font-bold uppercase tracking-widest text-gray-500 mb-1">{node.type}</div>
                                        <div className="text-xs font-semibold text-white truncate">{node.label}</div>
                                    </motion.button>
                                );
                            })}
                        </AnimatePresence>
                    </div>
                </div>
            </div>
        </div>
    );
}

function StatItem({ icon: Icon, label, value }: { icon: any, label: string, value: string | number }) {
    return (
        <div className="bg-slate-900/30 border border-white/5 rounded-2xl p-4">
            <div className="flex items-center gap-3">
                <div className="p-2 rounded-xl bg-white/5 text-gray-400">
                    <Icon className="w-4 h-4" />
                </div>
                <div>
                    <div className="text-xs text-gray-500">{label}</div>
                    <div className="text-lg font-bold text-white">{value}</div>
                </div>
            </div>
        </div>
    );
}

function FilterButton({ label, active, onClick, type }: { label: string, active: boolean, onClick: () => void, type: string }) {
    const colorClass = TYPE_COLORS[type] || 'cyan';
    return (
        <button
            onClick={onClick}
            className={`
        w-full flex items-center justify-between px-4 py-2.5 rounded-xl text-xs font-semibold transition-all
        ${active
                    ? `bg-${colorClass}-500 text-white shadow-lg shadow-${colorClass}-500/20`
                    : 'text-gray-400 hover:text-white hover:bg-white/5'}
      `}
        >
            {label}
            {active && <Zap className="w-3 h-3 fill-current" />}
        </button>
    );
}
