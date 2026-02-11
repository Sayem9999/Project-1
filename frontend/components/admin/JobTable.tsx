'use client';
import { memo } from 'react';
import StatusBadge from './StatusBadge';

interface JobData {
    id: number;
    user_id: number;
    status: string;
    progress_message: string;
    theme: string;
    created_at: string;
    updated_at?: string | null;
}

interface JobTableProps {
    jobs: JobData[];
    isStalledJob: (job: JobData) => boolean;
    handleAdminForceRetry: (jobId: number) => void;
    handleAdminCancel: (jobId: number) => void;
    handleAdminRetry: (jobId: number) => void;
}

export default memo(function JobTable({
    jobs,
    isStalledJob,
    handleAdminForceRetry,
    handleAdminCancel,
    handleAdminRetry
}: JobTableProps) {
    return (
        <div className="overflow-x-auto">
            <table className="w-full text-left">
                <thead className="bg-white/5 text-gray-400 text-xs font-bold uppercase tracking-widest border-b border-white/5">
                    <tr>
                        <th className="px-6 py-4">Job ID</th>
                        <th className="px-6 py-4">Status</th>
                        <th className="px-6 py-4">Theme</th>
                        <th className="px-6 py-4">Message</th>
                        <th className="px-6 py-4">Created</th>
                        <th className="px-6 py-4 text-right">Actions</th>
                    </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                    {jobs.map((job) => {
                        const stalled = isStalledJob(job);
                        const lastActivity = job.updated_at || job.created_at;
                        return (
                            <tr key={job.id} className="hover:bg-white/5 transition-colors">
                                <td className="px-6 py-5 font-mono text-cyan-400 text-sm">#{job.id}</td>
                                <td className="px-6 py-5">
                                    <div className="flex items-center gap-2">
                                        <StatusBadge status={job.status} />
                                        {stalled && (
                                            <span className="px-2 py-1 rounded-md text-[10px] font-bold uppercase border border-amber-500/30 text-amber-300 bg-amber-500/10">
                                                Stalled
                                            </span>
                                        )}
                                    </div>
                                </td>
                                <td className="px-6 py-5 text-gray-300 text-sm capitalize">{job.theme}</td>
                                <td className="px-6 py-5 text-gray-400 text-xs italic max-w-xs truncate">
                                    {job.progress_message}
                                    {stalled && (
                                        <div className="text-[10px] text-gray-600 mt-1">
                                            Last update: {new Date(lastActivity).toLocaleString()}
                                        </div>
                                    )}
                                </td>
                                <td className="px-6 py-5 text-gray-500 text-xs">
                                    {new Date(job.created_at).toLocaleString()}
                                </td>
                                <td className="px-6 py-5 text-right">
                                    {stalled ? (
                                        <div className="flex items-center justify-end gap-3">
                                            <button
                                                onClick={() => handleAdminForceRetry(job.id)}
                                                className="text-xs font-semibold text-amber-300 hover:text-amber-200"
                                            >
                                                Force Retry
                                            </button>
                                            <button
                                                onClick={() => handleAdminCancel(job.id)}
                                                className="text-xs font-semibold text-red-300 hover:text-red-200"
                                            >
                                                Cancel
                                            </button>
                                        </div>
                                    ) : job.status === 'failed' ? (
                                        <button
                                            onClick={() => handleAdminRetry(job.id)}
                                            className="text-xs font-semibold text-emerald-300 hover:text-emerald-200"
                                        >
                                            Retry
                                        </button>
                                    ) : job.status === 'processing' || job.status === 'queued' ? (
                                        <button
                                            onClick={() => handleAdminCancel(job.id)}
                                            className="text-xs font-semibold text-red-300 hover:text-red-200"
                                        >
                                            Cancel
                                        </button>
                                    ) : (
                                        <span className="text-xs text-gray-500">-</span>
                                    )}
                                </td>
                            </tr>
                        );
                    })}
                </tbody>
            </table>
        </div>
    );
});
