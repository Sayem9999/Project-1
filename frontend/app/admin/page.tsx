'use client';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Activity, HardDrive, LayoutDashboard, Shield, Users, Video, Edit2, RefreshCw, Search } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import * as Sentry from '@sentry/nextjs';
import { apiRequest, ApiError, clearAuth } from '@/lib/api';

interface SystemStats {
  users: { total: number };
  jobs: { total: number; recent_24h: number };
  storage: { used_gb: number; limit_gb: number; percent: number; files: number };
}

interface UserData {
  id: number;
  email: string;
  full_name: string | null;
  credits: number;
  created_at: string;
}

interface JobData {
  id: number;
  user_id: number;
  status: string;
  progress_message: string;
  theme: string;
  created_at: string;
}

export default function AdminDashboardPage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'overview' | 'users' | 'jobs'>('overview');
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [users, setUsers] = useState<UserData[]>([]);
  const [jobs, setJobs] = useState<JobData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [accessDenied, setAccessDenied] = useState(false);
  const [editingCredits, setEditingCredits] = useState<{ id: number; credits: number } | null>(null);
  const [userSearch, setUserSearch] = useState('');
  const [jobSearch, setJobSearch] = useState('');
  const [jobFilter, setJobFilter] = useState<'all' | 'processing' | 'complete' | 'failed'>('all');

  const fetchData = useCallback(async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    try {
      const [statsData, usersData, jobsData] = await Promise.all([
        apiRequest<SystemStats>('/admin/stats', { auth: true }),
        apiRequest<UserData[]>('/admin/users', { auth: true }),
        apiRequest<JobData[]>('/admin/jobs', { auth: true }),
      ]);

      setStats(statsData);
      setUsers(usersData);
      setJobs(jobsData);
      setLoading(false);
      setAccessDenied(false);
    } catch (err: any) {
      Sentry.captureException(err);
      if (err instanceof ApiError) {
        if (err.status === 403) {
          setAccessDenied(true);
        }
        if (err.isAuth) {
          clearAuth();
          router.push('/login');
          return;
        }
        setError(err.message);
      } else {
        setError('Failed to fetch admin data');
      }
      setLoading(false);
    }
  }, [router]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleUpdateCredits = async (userId: number, newCredits: number) => {
    try {
      await apiRequest(`/admin/users/${userId}/credits?credits=${newCredits}`, {
        method: 'PATCH',
        auth: true,
      });
      setEditingCredits(null);
      fetchData();
    } catch (err) {
      console.error('Failed to update credits', err);
    }
  };

  const filteredUsers = useMemo(() => {
    if (!userSearch) return users;
    const q = userSearch.toLowerCase();
    return users.filter((u) => `${u.email} ${u.full_name ?? ''}`.toLowerCase().includes(q));
  }, [users, userSearch]);

  const filteredJobs = useMemo(() => {
    let list = jobs;
    if (jobFilter !== 'all') {
      list = list.filter((j) => j.status === jobFilter);
    }
    if (!jobSearch) return list;
    const q = jobSearch.toLowerCase();
    return list.filter((j) => `${j.id} ${j.user_id} ${j.theme} ${j.progress_message}`.toLowerCase().includes(q));
  }, [jobs, jobFilter, jobSearch]);

  const processingCount = jobs.filter((j) => j.status === 'processing').length;
  const failedCount = jobs.filter((j) => j.status === 'failed').length;
  const completeCount = jobs.filter((j) => j.status === 'complete').length;

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="w-12 h-12 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (accessDenied) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="max-w-md w-full bg-slate-900/40 border border-white/10 rounded-3xl p-8 text-center">
          <div className="w-14 h-14 mx-auto mb-4 rounded-full bg-red-500/10 text-red-400 flex items-center justify-center">
            <Shield className="w-6 h-6" />
          </div>
          <h2 className="text-xl font-bold text-white mb-2">Admin Access Required</h2>
          <p className="text-gray-400 mb-6">You can view the Admin Console link, but only approved admins can open it.</p>
          <button
            onClick={() => router.push('/dashboard')}
            className="px-6 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-white transition-colors"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-10">
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
        <div>
          <div className="flex items-center gap-3 text-brand-cyan text-xs uppercase tracking-[0.2em]">
            <span className="px-2 py-1 rounded-full border border-brand-cyan/30 bg-brand-cyan/10">Secured</span>
            Admin Command Center
          </div>
          <h1 className="text-4xl font-bold text-white mt-3 mb-2">Operations & Oversight</h1>
          <p className="text-gray-400 max-w-2xl">
            Monitor usage, manage credits, and keep the pipeline healthy.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={fetchData}
            className="px-4 py-2 rounded-xl bg-white/10 hover:bg-white/20 text-white text-sm font-semibold flex items-center gap-2"
          >
            <RefreshCw className="w-4 h-4" /> Refresh
          </button>
          <div className="px-4 py-2 rounded-xl border border-white/10 text-xs text-gray-400">
            {new Date().toLocaleTimeString()}
          </div>
        </div>
      </div>

      {error && (
        <div className="rounded-2xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
        <StatCard icon={Users} title="Total Users" value={stats?.users.total ?? 0} subtext="Registered accounts" color="cyan" />
        <StatCard icon={Video} title="Total Jobs" value={stats?.jobs.total ?? 0} subtext={`+${stats?.jobs.recent_24h ?? 0} in 24h`} color="violet" />
        <StatCard icon={Activity} title="Active Jobs" value={processingCount} subtext={`${completeCount} complete, ${failedCount} failed`} color="emerald" />
        <StatCard
          icon={HardDrive}
          title="Cloud Storage"
          value={`${stats?.storage.used_gb ?? 0} GB`}
          subtext={`${stats?.storage.percent ?? 0}% of ${stats?.storage.limit_gb ?? 0}GB`}
          color="amber"
          progress={stats?.storage.percent ?? 0}
        />
      </div>

      <div className="flex items-center gap-3 bg-slate-900/50 p-1.5 rounded-2xl border border-white/5 w-fit">
        {[
          { id: 'overview', label: 'Overview', icon: LayoutDashboard },
          { id: 'users', label: 'Users', icon: Users },
          { id: 'jobs', label: 'Jobs', icon: Video },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-semibold transition-all ${
              activeTab === tab.id
                ? 'bg-gradient-to-r from-cyan-500 to-violet-500 text-white shadow-lg shadow-cyan-500/20'
                : 'text-gray-400 hover:text-white hover:bg-white/5'
            }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      <AnimatePresence mode="wait">
        {activeTab === 'overview' && (
          <motion.div
            key="overview"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="grid grid-cols-1 lg:grid-cols-3 gap-6"
          >
            <div className="lg:col-span-2 bg-slate-900/30 border border-white/10 rounded-3xl p-6 backdrop-blur-xl">
              <h3 className="text-lg font-semibold text-white mb-4">Recent Jobs</h3>
              <div className="space-y-3">
                {jobs.slice(0, 6).map((job) => (
                  <div key={job.id} className="flex items-center justify-between p-3 rounded-2xl bg-white/5">
                    <div>
                      <div className="text-sm font-semibold text-white">Job #{job.id}</div>
                      <div className="text-xs text-gray-400">{job.progress_message}</div>
                    </div>
                    <StatusBadge status={job.status} />
                  </div>
                ))}
              </div>
            </div>
            <div className="bg-slate-900/30 border border-white/10 rounded-3xl p-6 backdrop-blur-xl">
              <h3 className="text-lg font-semibold text-white mb-4">Recent Users</h3>
              <div className="space-y-3">
                {users.slice(0, 6).map((user) => (
                  <div key={user.id} className="flex items-center justify-between p-3 rounded-2xl bg-white/5">
                    <div>
                      <div className="text-sm font-semibold text-white">{user.full_name || 'Anonymous'}</div>
                      <div className="text-xs text-gray-400">{user.email}</div>
                    </div>
                    <div className="text-xs text-amber-400 font-semibold">{user.credits} credits</div>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}

        {activeTab === 'users' && (
          <motion.div
            key="users"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="bg-slate-900/30 border border-white/10 rounded-3xl overflow-hidden backdrop-blur-xl"
          >
            <div className="p-6 border-b border-white/10 flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <h3 className="text-lg font-semibold text-white">Users</h3>
                <p className="text-xs text-gray-500">Manage credits and access.</p>
              </div>
              <div className="relative w-full md:w-72">
                <Search className="w-4 h-4 text-gray-500 absolute left-3 top-3" />
                <input
                  value={userSearch}
                  onChange={(e) => setUserSearch(e.target.value)}
                  placeholder="Search by name or email"
                  className="w-full bg-black/30 border border-white/10 rounded-xl pl-9 pr-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-500/50"
                />
              </div>
            </div>
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
                {filteredUsers.map((user) => (
                  <tr key={user.id} className="hover:bg-white/5 transition-colors">
                    <td className="px-6 py-5">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-500/20 to-violet-500/20 flex items-center justify-center text-cyan-400 font-bold border border-cyan-500/20">
                          {user.email[0].toUpperCase()}
                        </div>
                        <div>
                          <p className="text-white font-medium">{user.full_name || 'Anonymous'}</p>
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
                      <button className="text-xs font-bold text-cyan-400 hover:text-cyan-300 transition-colors">
                        View Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </motion.div>
        )}

        {activeTab === 'jobs' && (
          <motion.div
            key="jobs"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="bg-slate-900/30 border border-white/10 rounded-3xl overflow-hidden backdrop-blur-xl"
          >
            <div className="p-6 border-b border-white/10 flex flex-col lg:flex-row lg:items-center justify-between gap-4">
              <div>
                <h3 className="text-lg font-semibold text-white">Jobs</h3>
                <p className="text-xs text-gray-500">Track pipeline status and errors.</p>
              </div>
              <div className="flex flex-col md:flex-row gap-3 w-full lg:w-auto">
                <div className="relative w-full md:w-64">
                  <Search className="w-4 h-4 text-gray-500 absolute left-3 top-3" />
                  <input
                    value={jobSearch}
                    onChange={(e) => setJobSearch(e.target.value)}
                    placeholder="Search by id, theme"
                    className="w-full bg-black/30 border border-white/10 rounded-xl pl-9 pr-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-500/50"
                  />
                </div>
                <div className="flex items-center gap-2">
                  {['all', 'processing', 'complete', 'failed'].map((status) => (
                    <button
                      key={status}
                      onClick={() => setJobFilter(status as any)}
                      className={`px-3 py-2 rounded-lg text-xs font-semibold uppercase tracking-wider transition-colors ${
                        jobFilter === status
                          ? 'bg-brand-cyan text-black'
                          : 'bg-white/5 text-gray-400 hover:text-white'
                      }`}
                    >
                      {status}
                    </button>
                  ))}
                </div>
              </div>
            </div>
            <table className="w-full text-left">
              <thead className="bg-white/5 text-gray-400 text-xs font-bold uppercase tracking-widest border-b border-white/5">
                <tr>
                  <th className="px-6 py-4">Job ID</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4">Theme</th>
                  <th className="px-6 py-4">Message</th>
                  <th className="px-6 py-4">Created</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {filteredJobs.map((job) => (
                  <tr key={job.id} className="hover:bg-white/5 transition-colors">
                    <td className="px-6 py-5 font-mono text-cyan-400 text-sm">#{job.id}</td>
                    <td className="px-6 py-5">
                      <StatusBadge status={job.status} />
                    </td>
                    <td className="px-6 py-5 text-gray-300 text-sm capitalize">{job.theme}</td>
                    <td className="px-6 py-5 text-gray-400 text-xs italic max-w-xs truncate">{job.progress_message}</td>
                    <td className="px-6 py-5 text-gray-500 text-xs">
                      {new Date(job.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function StatCard({ icon: Icon, title, value, subtext, color, progress }: any) {
  const colors = {
    cyan: 'from-cyan-500/20 to-cyan-500/5 border-cyan-500/30 text-cyan-400',
    violet: 'from-violet-500/20 to-violet-500/5 border-violet-500/30 text-violet-400',
    emerald: 'from-emerald-500/20 to-emerald-500/5 border-emerald-500/30 text-emerald-400',
    amber: 'from-amber-500/20 to-amber-500/5 border-amber-500/30 text-amber-400',
  };

  return (
    <div className={`p-6 bg-gradient-to-br ${colors[color as keyof typeof colors]} border rounded-3xl relative overflow-hidden group`}>
      <div className="absolute top-0 right-0 p-6 opacity-10 group-hover:opacity-20 transition-opacity">
        <Icon className="w-16 h-16" />
      </div>
      <div className="relative z-10">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-white/5 rounded-lg border border-white/10">
            <Icon className="w-4 h-4" />
          </div>
          <h3 className="text-gray-300 font-medium text-sm">{title}</h3>
        </div>
        <div className="text-3xl font-black text-white mb-1 tracking-tighter">{value}</div>
        <p className="text-xs text-gray-500 font-medium">{subtext}</p>

        {progress !== undefined && (
          <div className="mt-4 w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              className={`h-full rounded-full ${progress > 80 ? 'bg-red-500' : 'bg-current'}`}
            />
          </div>
        )}
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const styles =
    status === 'complete'
      ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
      : status === 'failed'
      ? 'bg-red-500/10 border-red-500/30 text-red-400'
      : 'bg-cyan-500/10 border-cyan-500/30 text-cyan-400 animate-pulse';

  return (
    <span className={`px-2 py-1 rounded-md text-[10px] font-black uppercase border ${styles}`}>
      {status}
    </span>
  );
}
