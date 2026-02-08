'use client';
import { useEffect, useState, useRef } from 'react';

interface AgentConsoleProps {
    status: string;
    lastMessage: string;
}

interface LogEntry {
    id: number;
    timestamp: string;
    agent: string;
    message: string;
    type: 'info' | 'success' | 'warning' | 'error';
}

export function AgentConsole({ status, lastMessage }: AgentConsoleProps) {
    const [logs, setLogs] = useState<LogEntry[]>([]);
    const scrollRef = useRef<HTMLDivElement>(null);
    const lastMsgRef = useRef(lastMessage);

    useEffect(() => {
        if (lastMessage && lastMessage !== lastMsgRef.current) {
            lastMsgRef.current = lastMessage;

            // Parse Agent Name if present (e.g., "[Director] Analyzing...")
            let agent = 'System';
            let message = lastMessage;
            let type: LogEntry['type'] = 'info';

            if (lastMessage.includes('[Director]')) { agent = 'Director'; message = lastMessage.replace('[Director]', '').trim(); }
            else if (lastMessage.includes('[Cutter]')) { agent = 'Cutter'; message = lastMessage.replace('[Cutter]', '').trim(); }
            else if (lastMessage.includes('[Color]')) { agent = 'Colorist'; message = lastMessage.replace('[Color]', '').trim(); }
            else if (lastMessage.includes('[Audio]')) { agent = 'Audio'; message = lastMessage.replace('[Audio]', '').trim(); }
            else if (status === 'complete') { agent = 'Studio'; type = 'success'; }
            else if (status === 'failed') { agent = 'System'; type = 'error'; }

            const newLog: LogEntry = {
                id: Date.now(),
                timestamp: new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }),
                agent,
                message,
                type
            };

            setLogs(prev => [...prev.slice(-20), newLog]); // Keep last 20 logs
        }
    }, [lastMessage, status]);

    // Auto-scroll
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [logs]);

    return (
        <div className="font-mono text-sm bg-slate-950/80 rounded-xl border border-slate-800 shadow-2xl overflow-hidden backdrop-blur-md">
            {/* Terminal Header */}
            <div className="flex items-center gap-2 px-4 py-2 bg-slate-900/50 border-b border-slate-800">
                <div className="flex gap-1.5">
                    <div className="w-2.5 h-2.5 rounded-full bg-red-500/50"></div>
                    <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/50"></div>
                    <div className="w-2.5 h-2.5 rounded-full bg-emerald-500/50"></div>
                </div>
                <div className="ml-2 text-xs text-slate-500">ai_studio_link.exe — {status}</div>
            </div>

            {/* Terminal Body */}
            <div ref={scrollRef} className="h-48 overflow-y-auto p-4 space-y-2 scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent">
                {logs.length === 0 && (
                    <div className="text-slate-600 italic">Waiting for agent connection...</div>
                )}

                {logs.map((log) => (
                    <div key={log.id} className="flex gap-3 animate-in fade-in slide-in-from-left-2 duration-300">
                        <span className="text-slate-600 select-none">[{log.timestamp}]</span>
                        <span className={`font-bold w-20 text-right ${log.agent === 'Director' ? 'text-brand-cyan' :
                                log.agent === 'Cutter' ? 'text-brand-violet' :
                                    log.agent === 'Colorist' ? 'text-brand-fuchsia' :
                                        'text-emerald-400'
                            }`}>
                            {log.agent}:
                        </span>
                        <span className={`${log.type === 'error' ? 'text-red-400' :
                                log.type === 'success' ? 'text-emerald-300' :
                                    'text-slate-300'
                            }`}>
                            {log.message}
                        </span>
                    </div>
                ))}

                {status === 'processing' && (
                    <div className="flex gap-3 animate-pulse">
                        <span className="text-slate-600 invisible">[{new Date().toLocaleTimeString()}]</span>
                        <span className="font-bold w-20 text-right text-slate-500">System:</span>
                        <span className="text-slate-500">_</span>
                    </div>
                )}
            </div>
        </div>
    );
}
