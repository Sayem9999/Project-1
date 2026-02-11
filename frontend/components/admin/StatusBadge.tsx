'use client';
import { memo } from 'react';

export default memo(function StatusBadge({ status }: { status: string }) {
    switch (status) {
        case 'complete':
            return (
                <span className="px-2 py-1 rounded-md text-[10px] font-bold uppercase border border-emerald-500/30 text-emerald-300 bg-emerald-500/10">
                    Ready
                </span>
            );
        case 'failed':
            return (
                <span className="px-2 py-1 rounded-md text-[10px] font-bold uppercase border border-red-500/30 text-red-300 bg-red-500/10">
                    Failed
                </span>
            );
        case 'processing':
            return (
                <span className="px-2 py-1 rounded-md text-[10px] font-bold uppercase border border-cyan-500/30 text-cyan-300 bg-cyan-500/10 animate-pulse">
                    Processing
                </span>
            );
        default:
            return (
                <span className="px-2 py-1 rounded-md text-[10px] font-bold uppercase border border-gray-500/30 text-gray-400 bg-gray-500/10">
                    {status}
                </span>
            );
    }
});
