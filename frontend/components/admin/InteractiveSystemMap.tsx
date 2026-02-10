"use client";

import { useEffect, useRef, useState, useCallback } from 'react';
import dynamic from 'next/dynamic';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Loader2, RefreshCw, ZoomIn, ZoomOut, Maximize2 } from 'lucide-react';
import { toast } from 'sonner';

// Dynamically import ForceGraph2D to avoid SSR issues
const ForceGraph2D = dynamic(() => import('react-force-graph-2d'), {
    ssr: false,
    loading: () => <div className="h-full w-full flex items-center justify-center text-slate-400"><Loader2 className="w-8 h-8 animate-spin" /></div>
});

interface GraphNode {
    id: string;
    label: string;
    type: string;
    val: number;
    color: string;
    file?: string;
    x?: number;
    y?: number;
}

interface GraphEdge {
    source: string | GraphNode;
    target: string | GraphNode;
    type: string;
}

interface GraphData {
    nodes: GraphNode[];
    links: GraphEdge[]; // Changed from edges to links for react-force-graph
}

export default function InteractiveSystemMap() {
    const fgRef = useRef<any>(null);
    const [data, setData] = useState<GraphData>({ nodes: [], links: [] });
    const [loading, setLoading] = useState(true);
    const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
    const [isLive, setIsLive] = useState(false);
    const [searchQuery, setSearchQuery] = useState("");
    const containerRef = useRef<HTMLDivElement>(null);
    const [dimensions, setDimensions] = useState({ width: 800, height: 600 });

    const fetchGraph = async () => {
        try {
            setLoading(true);
            // Assuming a proxy or auth header is handled by a wrapper or cookie
            // For this demo, we'll try to fetch directly. 
            // In a real app, use your apiRequest helper.
            const token = localStorage.getItem('token');
            const headers: HeadersInit = token ? { 'Authorization': `Bearer ${token}` } : {};

            const res = await fetch('/api/maintenance/graph', { headers });
            if (!res.ok) throw new Error("Failed to fetch graph");

            const graphData = await res.json();

            // Transform backend data if necessary (backend already returns proper structure)
            setData({
                nodes: graphData.nodes,
                links: graphData.edges.map((e: any) => ({
                    source: e.source,
                    target: e.target,
                    type: e.type
                }))
            });

            if (fgRef.current) {
                fgRef.current.d3Force('charge').strength(-120);
                fgRef.current.zoomToFit(400, 50); // duration, padding
            }

            toast.success("System Map Updated");
        } catch (err) {
            console.error(err);
            toast.error("Failed to load System Map");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchGraph();

        // Resize handler
        const updateDimensions = () => {
            if (containerRef.current) {
                setDimensions({
                    width: containerRef.current.clientWidth,
                    height: containerRef.current.clientHeight
                });
            }
        };

        window.addEventListener('resize', updateDimensions);
        updateDimensions();

        return () => window.removeEventListener('resize', updateDimensions);
    }, []);

    // Live polling
    useEffect(() => {
        if (!isLive) return;
        const interval = setInterval(fetchGraph, 5000);
        return () => clearInterval(interval);
    }, [isLive]);

    const handleNodeClick = useCallback((node: any) => { // Use any or extended type for force-graph node
        if (!node) return;
        const typedNode = node as GraphNode;
        setSelectedNode(typedNode);

        // Smooth camera fly-to
        if (fgRef.current) {
            const distance = 40;
            const distRatio = 1 + distance / Math.hypot(node.x || 0, node.y || 0, 0);

            fgRef.current.centerAt(
                (node.x || 0),
                (node.y || 0),
                1000
            );
            fgRef.current.zoom(3, 2000);
        }
    }, [fgRef]);

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        const node = data.nodes.find(n => n.label.toLowerCase().includes(searchQuery.toLowerCase()));
        if (node) {
            handleNodeClick(node);
            toast.success(`Found: ${node.label}`);
        } else {
            toast.error("Node not found");
        }
    };

    return (
        <div className="relative h-[800px] w-full bg-slate-950 border border-white/10 rounded-3xl overflow-hidden flex flex-col">
            {/* Header Controls */}
            <div className="absolute top-4 left-4 right-4 z-10 flex flex-wrap items-center justify-between gap-4 pointer-events-none">
                {/* Search */}
                <form onSubmit={handleSearch} className="pointer-events-auto flex items-center bg-slate-900/80 backdrop-blur-md rounded-full px-4 py-2 border border-white/10 shadow-xl">
                    <Search className="w-4 h-4 text-slate-400 mr-2" />
                    <input
                        type="text"
                        placeholder="Search node..."
                        className="bg-transparent border-none outline-none text-sm text-white placeholder-slate-500 w-48"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                    />
                </form>

                {/* Actions */}
                <div className="pointer-events-auto flex items-center gap-2">
                    <button
                        onClick={() => setIsLive(!isLive)}
                        className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold backdrop-blur-md border transition-all ${isLive
                            ? 'bg-green-500/20 text-green-400 border-green-500/30 animate-pulse'
                            : 'bg-slate-900/80 text-slate-400 border-white/10 hover:bg-white/5'
                            }`}
                    >
                        <div className={`w-2 h-2 rounded-full ${isLive ? 'bg-green-500' : 'bg-slate-500'}`} />
                        {isLive ? 'LIVE' : 'PAUSED'}
                    </button>

                    <button
                        onClick={fetchGraph}
                        disabled={loading}
                        className="p-2 bg-slate-900/80 backdrop-blur-md rounded-full border border-white/10 text-white hover:bg-white/10 transition-colors"
                    >
                        <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                    </button>
                </div>
            </div>

            {/* The Graph */}
            <div ref={containerRef} className="flex-1 w-full h-full cursor-move">
                <ForceGraph2D
                    ref={fgRef}
                    width={dimensions.width}
                    height={dimensions.height}
                    graphData={data}
                    nodeLabel="label"
                    nodeColor="color"
                    nodeRelSize={6}
                    linkColor={() => 'rgba(255,255,255,0.2)'}
                    linkDirectionalParticles={isLive ? 2 : 0}
                    linkDirectionalParticleSpeed={0.005}
                    linkDirectionalArrowLength={3.5}
                    linkDirectionalArrowRelPos={1}
                    backgroundColor="#020617"
                    onNodeClick={handleNodeClick}
                    cooldownTicks={100}
                    d3VelocityDecay={0.3}
                />
            </div>

            {/* Selected Node Details Panel */}
            <AnimatePresence>
                {selectedNode && (
                    <motion.div
                        initial={{ x: 300, opacity: 0 }}
                        animate={{ x: 0, opacity: 1 }}
                        exit={{ x: 300, opacity: 0 }}
                        className="absolute top-20 right-4 w-72 bg-slate-900/90 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-2xl z-20"
                    >
                        <div className="flex items-start justify-between mb-4">
                            <div className="flex items-center gap-3">
                                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: selectedNode.color }} />
                                <span className="text-xs font-mono uppercase text-slate-400 tracking-wider text-opacity-80 border border-white/10 px-2 py-0.5 rounded-md">{selectedNode.type}</span>
                            </div>
                            <button onClick={() => setSelectedNode(null)} className="text-slate-400 hover:text-white">&times;</button>
                        </div>

                        <h3 className="text-xl font-bold text-white mb-2 break-words">{selectedNode.label}</h3>

                        {selectedNode.file && (
                            <div className="mb-4">
                                <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">File Path</p>
                                <code className="text-xs text-blue-300 break-all bg-blue-500/10 px-2 py-1 rounded block border border-blue-500/20">
                                    {selectedNode.file.split('Project-1-1')[1] || selectedNode.file}
                                </code>
                            </div>
                        )}

                        <div className="flex flex-col gap-2 mt-4">
                            <button className="w-full py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-sm text-slate-300 transition-colors flex items-center justify-center gap-2">
                                <Maximize2 className="w-4 h-4" /> Inspect Code
                            </button>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Stats Overlay */}
            <div className="absolute bottom-6 left-6 pointer-events-none">
                <div className="flex gap-6 text-sm">
                    <div className="flex flex-col">
                        <span className="text-slate-500 text-xs uppercase tracking-wider">Nodes</span>
                        <span className="text-white font-mono text-xl">{data.nodes.length}</span>
                    </div>
                    <div className="flex flex-col">
                        <span className="text-slate-500 text-xs uppercase tracking-wider">Edges</span>
                        <span className="text-white font-mono text-xl">{data.links.length}</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
