'use client';
import { memo } from 'react';
import { Edit2 } from 'lucide-react';
import StatusBadge from './StatusBadge';

interface UserData {
    id: number;
    email: string;
    full_name: string | null;
    credits: number;
    monthly_credits?: number;
    last_credit_reset?: string | null;
    is_admin?: boolean;
    created_at: string;
}

interface UserTableProps {
    users: UserData[];
    editingCredits: { id: number; credits: number } | null;
    setEditingCredits: (val: { id: number; credits: number } | null) => void;
    handleUpdateCredits: (userId: number, newCredits: number) => void;
    handleAddCredits: (userId: number, delta: number, reason: string) => void;
    openUserDetails: (user: UserData) => void;
}

export default memo(function UserTable({
    users,
    editingCredits,
    setEditingCredits,
    handleUpdateCredits,
    handleAddCredits,
    openUserDetails
}: UserTableProps) {
    const quickCreditAdds = [1, 5, 10];

    return (
        <div className="overflow-x-auto">
            <table className="w-full text-left">
                <thead className="bg-white/5 text-gray-400 text-xs font-bold uppercase tracking-widest border-b border-white/5">
                    <tr>
                        <th className="px-6 py-4">User</th>
                        <th className="px-6 py-4">Credits</th>
                        <th className="px-6 py-4">Created</th>
                        <th className="px-6 py-4 text-right">Actions</th>
                    </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                    {users.map((user) => (
                        <tr key={user.id} className="hover:bg-white/5 transition-colors">
                            <td className="px-6 py-5">
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-500/20 to-violet-500/20 flex items-center justify-center text-cyan-400 font-bold border border-cyan-500/20">
                                        {user.email[0].toUpperCase()}
                                    </div>
                                    <div>
                                        <div className="flex items-center gap-2">
                                            <p className="text-white font-medium">{user.full_name || 'Anonymous'}</p>
                                            {user.is_admin && (
                                                <span className="text-[10px] uppercase tracking-widest font-semibold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
                                                    Admin
                                                </span>
                                            )}
                                        </div>
                                        <p className="text-xs text-gray-500">{user.email}</p>
                                    </div>
                                </div>
                            </td>
                            <td className="px-6 py-5">
                                {editingCredits?.id === user.id ? (
                                    <div className="flex items-center gap-2">
                                        <input
                                            type="number"
                                            value={editingCredits.credits}
                                            onChange={(e) =>
                                                setEditingCredits({ ...editingCredits, credits: parseInt(e.target.value, 10) })
                                            }
                                            className="w-20 bg-black border border-white/20 rounded px-2 py-1 text-white text-sm"
                                        />
                                        <button
                                            onClick={() => handleUpdateCredits(user.id, editingCredits.credits)}
                                            className="text-emerald-400 text-xs hover:underline"
                                        >
                                            Save
                                        </button>
                                    </div>
                                ) : (
                                    <div className="flex items-center gap-2">
                                        <span className="text-amber-400 font-bold font-mono">{user.credits}</span>
                                        <button
                                            onClick={() => setEditingCredits({ id: user.id, credits: user.credits })}
                                            className="text-gray-600 hover:text-white transition-colors"
                                        >
                                            <Edit2 className="w-3 h-3" />
                                        </button>
                                    </div>
                                )}
                            </td>
                            <td className="px-6 py-5 text-gray-400 text-sm">
                                {new Date(user.created_at).toLocaleDateString()}
                            </td>
                            <td className="px-6 py-5 text-right">
                                <div className="flex items-center justify-end gap-2">
                                    {quickCreditAdds.map((delta) => (
                                        <button
                                            key={delta}
                                            onClick={() => handleAddCredits(user.id, delta, "quick_add")}
                                            className="px-2 py-1 rounded-lg bg-white/5 text-[10px] font-bold text-cyan-300 hover:bg-cyan-500/10 hover:text-cyan-200 transition-colors"
                                        >
                                            +{delta}
                                        </button>
                                    ))}
                                    <button
                                        onClick={() => setEditingCredits({ id: user.id, credits: user.credits })}
                                        className="text-[10px] font-bold text-gray-400 hover:text-white transition-colors"
                                    >
                                        Set
                                    </button>
                                    <button
                                        onClick={() => openUserDetails(user)}
                                        className="text-[10px] font-bold text-brand-cyan hover:text-brand-accent transition-colors"
                                    >
                                        Details
                                    </button>
                                </div>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
});
