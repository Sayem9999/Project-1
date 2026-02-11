'use client';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Activity, HardDrive, LayoutDashboard, Shield, Users, Video, Edit2, RefreshCw, Search, ArrowLeft, Database, Server, HeartPulse, Network, Wrench } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';
import * as Sentry from '@sentry/nextjs';
import { apiRequest, ApiError, clearAuth } from '@/lib/api';
import SystemMap from '@/components/admin/SystemMap';

interface SystemStats {
  users: { total: number; active_24h?: number };
  jobs: { total: number; recent_24h: number };
  storage: { used_gb: number; limit_gb: number; percent: number; files: number };
  trends?: {
    jobs_by_day: { date: string; count: number }[];
    failures_by_day: { date: string; count: number }[];
    users_by_day: { date: string; count: number }[];
  };
}

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

interface JobData {
  id: number;
  user_id: number;
  status: string;
  progress_message: string;
  theme: string;
  created_at: string;
  updated_at?: string | null;
}

interface AdminHealth {
  db: { reachable: boolean; error?: string };
  redis: { configured: boolean; reachable: boolean; latency_ms?: number; error?: string };
  storage: { used_gb: number; limit_gb: number; percent: number; files: number };
  cleanup?: { last_run: string | null; deleted_local: number; deleted_r2: number; stalled_jobs?: number };
  llm: Record<
    string,
    {
      configured: boolean;
      is_healthy: boolean;
      success_rate: number;
      avg_latency_ms: number;
    }
  >;
}

interface CreditLedgerEntry {
  id: number;
  user_id: number;
  user_email: string;
  delta: number;
  balance_after: number;
  reason?: string | null;
  source: string;
  job_id?: number | null;
  created_by?: number | null;
  created_by_email?: string | null;
  created_at: string;
}

export default function AdminDashboardPage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'overview' | 'users' | 'jobs' | 'credits' | 'system'>('overview');
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [health, setHealth] = useState<AdminHealth | null>(null);
  const [users, setUsers] = useState<UserData[]>([]);
  const [jobs, setJobs] = useState<JobData[]>([]);
  const [jobsLoading, setJobsLoading] = useState(false);
  const [lastJobsRefresh, setLastJobsRefresh] = useState<string | null>(null);
  const [ledger, setLedger] = useState<CreditLedgerEntry[]>([]);
  const [ledgerLoading, setLedgerLoading] = useState(false);
  const [ledgerError, setLedgerError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [accessDenied, setAccessDenied] = useState(false);
  const [editingCredits, setEditingCredits] = useState<{ id: number; credits: number } | null>(null);
  const [userSearch, setUserSearch] = useState('');
  const [jobSearch, setJobSearch] = useState('');
  const [jobFilter, setJobFilter] = useState<'all' | 'processing' | 'complete' | 'failed'>('all');
  const quickCreditAdds = [1, 5, 10];
  const [creditForm, setCreditForm] = useState({ userId: '', delta: 1, reason: '' });
  const [selectedUser, setSelectedUser] = useState<UserData | null>(null);
  const [userJobs, setUserJobs] = useState<JobData[]>([]);
  const [userLedger, setUserLedger] = useState<CreditLedgerEntry[]>([]);
  const [userLoading, setUserLoading] = useState(false);
  const [architectQuery, setArchitectQuery] = useState('');
  const [architectAnswer, setArchitectAnswer] = useState('');
  const [architectLoading, setArchitectLoading] = useState(false);
  const STALL_THRESHOLD_MINUTES = 10;
  const STALL_THRESHOLD_MS = STALL_THRESHOLD_MINUTES * 60 * 1000;

  const fetchData = useCallback(async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    try {
      const [statsData, usersData, jobsData, healthData] = await Promise.all([
        apiRequest<SystemStats>('/admin/stats', { auth: true }),
        apiRequest<UserData[]>('/admin/users', { auth: true }),
        apiRequest<JobData[]>('/admin/jobs', { auth: true }),
        apiRequest<AdminHealth>('/admin/health', { auth: true }),
      ]);

      setStats(statsData);
      setUsers(usersData);
      setJobs(jobsData);
      setHealth(healthData);
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

  const fetchJobs = useCallback(async (silent = false) => {
    if (accessDenied) return;
    if (!silent) setJobsLoading(true);
    try {
      const data = await apiRequest<JobData[]>('/admin/jobs', { auth: true });
      setJobs(data);
      setLastJobsRefresh(new Date().toISOString());
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
        setError('Failed to fetch admin jobs');
      }
    } finally {
      if (!silent) setJobsLoading(false);
    }
  }, [accessDenied, router]);

  const fetchLedger = useCallback(async () => {
    if (accessDenied) return;
    setLedgerLoading(true);
    setLedgerError(null);
    try {
      const data = await apiRequest<CreditLedgerEntry[]>('/admin/credits/ledger?limit=200', { auth: true });
      setLedger(data);
    } catch (err: any) {
      if (err instanceof ApiError && err.isAuth) {
        clearAuth();
        router.push('/login');
        return;
      }
      setLedgerError(err instanceof ApiError ? err.message : 'Failed to load ledger');
    } finally {
      setLedgerLoading(false);
    }
  }, [accessDenied, router]);

  useEffect(() => {
    if (activeTab === 'credits') {
      fetchLedger();
    }
  }, [activeTab, fetchLedger]);

  useEffect(() => {
    if (activeTab !== 'jobs') return;
    fetchJobs(true);
    const interval = setInterval(() => fetchJobs(true), 15000);
    return () => clearInterval(interval);
  }, [activeTab, fetchJobs]);

  const handleUpdateCredits = async (userId: number, newCredits: number, reason = 'manual_set') => {
    try {
      await apiRequest(`/admin/users/${userId}/credits?credits=${newCredits}&reason=${encodeURIComponent(reason)}`, {
        method: 'PATCH',
        auth: true,
      });
      setEditingCredits(null);
      fetchData();
      fetchLedger();
    } catch (err) {
      console.error('Failed to update credits', err);
    }
  };

  const handleAddCredits = async (userId: number, delta: number, reason = 'manual_adjustment') => {
    const toastId = toast.loading('Updating credits...');
    try {
      await apiRequest(`/admin/users/${userId}/credits/add?delta=${delta}&reason=${encodeURIComponent(reason)}`, {
        method: 'PATCH',
        auth: true,
      });
      fetchData();
      fetchLedger();
      toast.success('Credits updated successfully', { id: toastId });
    } catch (err: any) {
      console.error('Failed to add credits', err);
      toast.error('Failed to update credits', { id: toastId, description: err.message });
    }
  };

  const handleAdminCancel = async (jobId: number) => {
    try {
      await apiRequest(`/admin/jobs/${jobId}/cancel`, { method: 'POST', auth: true });
      fetchJobs(true);
    } catch (err) {
      console.error('Failed to cancel job', err);
    }
  };

  const handleAdminRetry = async (jobId: number) => {
    try {
      await apiRequest(`/admin/jobs/${jobId}/retry`, { method: 'POST', auth: true });
      fetchJobs(true);
    } catch (err) {
      console.error('Failed to retry job', err);
    }
  };

  const handleAdminForceRetry = async (jobId: number) => {
    try {
      await apiRequest(`/admin/jobs/${jobId}/force-retry`, { method: 'POST', auth: true });
      fetchJobs(true);
    } catch (err) {
      console.error('Failed to force retry job', err);
    }
  };

  const openUserDetails = async (user: UserData) => {
    setSelectedUser(user);
    setUserLoading(true);
    try {
      const [jobsData, ledgerData] = await Promise.all([
        apiRequest<JobData[]>(`/admin/users/${user.id}/jobs?limit=10`, { auth: true }),
        apiRequest<CreditLedgerEntry[]>(`/admin/credits/ledger?user_id=${user.id}&limit=20`, { auth: true }),
      ]);
      setUserJobs(jobsData);
      setUserLedger(ledgerData);
    } catch (err) {
      console.error('Failed to load user details', err);
    } finally {
      setUserLoading(false);
    }
  };

  const closeUserDetails = () => {
    setSelectedUser(null);
    setUserJobs([]);
    setUserLedger([]);
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
  const isStalledJob = (job: JobData) => {
    if (job.status !== 'processing' && job.status !== 'queued') return false;
    const stamp = job.updated_at || job.created_at;
    const last = new Date(stamp).getTime();
    if (Number.isNaN(last)) return false;
    return Date.now() - last > STALL_THRESHOLD_MS;
  };
  const stalledCount = jobs.filter(isStalledJob).length;

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
            onClick={() => router.push('/dashboard')}
            className="px-4 py-2 rounded-xl border border-white/10 text-white text-sm font-semibold flex items-center gap-2 hover:bg-white/10 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" /> Back to Dashboard
          </button>
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

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-5 gap-6">
        <StatCard icon={Users} title="Total Users" value={stats?.users.total ?? 0} subtext="Registered accounts" color="cyan" />
        <StatCard icon={Activity} title="Active Users" value={stats?.users.active_24h ?? 0} subtext="Last 24h" color="emerald" />
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

      {health && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-slate-900/30 border border-white/10 rounded-3xl p-6 backdrop-blur-xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">System Health</h3>
              <div className="flex items-center gap-2 text-xs text-gray-400">
                <HeartPulse className="w-4 h-4" /> Live
              </div>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="rounded-2xl bg-white/5 border border-white/10 p-4">
                <div className="text-xs text-gray-400 mb-2 flex items-center gap-2">
                  <Database className="w-4 h-4" /> Database
                </div>
                <div className={`text-sm font-semibold ${health.db.reachable ? 'text-emerald-400' : 'text-red-400'}`}>
                  {health.db.reachable ? 'Connected' : 'Offline'}
                </div>
              </div>
              <div className="rounded-2xl bg-white/5 border border-white/10 p-4">
                <div className="text-xs text-gray-400 mb-2 flex items-center gap-2">
                  <Server className="w-4 h-4" /> Redis
                </div>
                <div className={`text-sm font-semibold ${health.redis.reachable ? 'text-emerald-400' : 'text-red-400'}`}>
                  {health.redis.configured ? (health.redis.reachable ? 'Connected' : 'Error') : 'Not Configured'}
                </div>
              </div>
            </div>
          </div>
          <div className="bg-slate-900/30 border border-white/10 rounded-3xl p-6 backdrop-blur-xl">
            <h3 className="text-sm font-semibold text-gray-400 mb-4">LLM Providers</h3>
            <div className="space-y-3">
              {Object.entries(health.llm || {}).map(([name, item]) => (
                <div key={name} className="flex items-center justify-between text-sm">
                  <span className="text-gray-300 capitalize">{name}</span>
                  <span className={`text-xs font-bold px-2 py-1 rounded-full ${item.is_healthy ? 'bg-emerald-500/10 text-emerald-300' : 'bg-red-500/10 text-red-300'}`}>
                    {item.is_healthy ? 'Healthy' : item.configured ? 'Down' : 'Disabled'}
                  </span>
                </div>
              ))}
            </div>
            {health.cleanup && (
              <div className="mt-6 border-t border-white/10 pt-4 text-xs text-gray-500">
                <div className="flex items-center justify-between">
                  <span>Last Cleanup</span>
                  <span>{health.cleanup.last_run ? new Date(health.cleanup.last_run).toLocaleString() : 'Never'}</span>
                </div>
                <div className="flex items-center justify-between mt-2">
                  <span>Deleted (Local/R2)</span>
                  <span>{health.cleanup.deleted_local}/{health.cleanup.deleted_r2}</span>
                </div>
                <div className="flex items-center justify-between mt-2">
                  <span>Stalled Jobs</span>
                  <span>{health.cleanup.stalled_jobs ?? 0}</span>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      <div className="flex items-center gap-3 bg-slate-900/50 p-1.5 rounded-2xl border border-white/5 w-fit">
        {[
          { id: 'overview', label: 'Overview', icon: LayoutDashboard },
          { id: 'users', label: 'Users', icon: Users },
          { id: 'jobs', label: 'Jobs', icon: Video },
          { id: 'credits', label: 'Credits', icon: Activity },
          { id: 'system', label: 'System Map', icon: Network },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-semibold transition-all ${activeTab === tab.id
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
            {stats?.trends && (
              <div className="lg:col-span-3 bg-slate-900/30 border border-white/10 rounded-3xl p-6 backdrop-blur-xl">
                <h3 className="text-lg font-semibold text-white mb-4">7-Day Trends</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {[
                    { label: 'Jobs', data: stats.trends.jobs_by_day, color: 'bg-cyan-500' },
                    { label: 'Failures', data: stats.trends.failures_by_day, color: 'bg-red-500' },
                    { label: 'New Users', data: stats.trends.users_by_day, color: 'bg-emerald-500' },
                  ].map((trend) => {
                    const max = Math.max(...trend.data.map((d) => d.count), 1);
                    return (
                      <div key={trend.label} className="rounded-2xl bg-white/5 border border-white/10 p-4">
                        <div className="text-xs text-gray-400 mb-3">{trend.label}</div>
                        <div className="space-y-2">
                          {trend.data.map((point) => (
                            <div key={point.date} className="flex items-center gap-3">
                              <span className="text-[10px] text-gray-500 w-16">{point.date}</span>
                              <div className="flex-1 h-2 bg-white/5 rounded-full overflow-hidden">
                                <div
                                  className={`h-full ${trend.color}`}
                                  style={{ width: `${Math.round((point.count / max) * 100)}%` }}
                                />
                              </div>
                              <span className="text-xs text-gray-300 w-6 text-right">{point.count}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
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
                <p className="text-[10px] text-gray-600 mt-1">
                  Auto-refresh every 15s - Stalled: {stalledCount}
                  {lastJobsRefresh && (
                    <span className="ml-2">- Last refresh: {new Date(lastJobsRefresh).toLocaleTimeString()}</span>
                  )}
                  {jobsLoading && <span className="ml-2">- Refreshing...</span>}
                </p>
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
                      className={`px-3 py-2 rounded-lg text-xs font-semibold uppercase tracking-wider transition-colors ${jobFilter === status
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
                  <th className="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {filteredJobs.map((job) => {
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
          </motion.div>
        )}

        {activeTab === 'system' && (
          <motion.div
            key="system"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            <SystemMap />

            <div className="bg-slate-900/30 border border-white/10 rounded-3xl p-6 backdrop-blur-xl">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-blue-500/10 rounded-lg text-blue-400 border border-blue-500/20">
                  <Network className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white">System Architect</h3>
                  <p className="text-xs text-gray-400"> AI-powered analysis of the live dependency graph.</p>
                </div>
              </div>

              <div className="flex flex-col gap-4">
                {architectAnswer && (
                  <div className="p-4 bg-white/5 rounded-2xl border border-white/10 animate-in fade-in slide-in-from-bottom-2">
                    <div className="flex items-center gap-2 mb-2">
                      <div className="w-2 h-2 rounded-full bg-blue-400 animate-pulse" />
                      <span className="text-xs font-bold text-blue-300 uppercase tracking-wider">Architect Plan</span>
                    </div>
                    <div className="text-sm text-gray-300 whitespace-pre-wrap font-mono leading-relaxed">
                      {architectAnswer}
                    </div>
                  </div>
                )}

                <form
                  onSubmit={async (e) => {
                    e.preventDefault();
                    if (!architectQuery.trim()) return;
                    setArchitectLoading(true);
                    try {
                      // Using pure fetch if apiRequest types are strict, or cast if needed
                      // Assuming apiRequest handles generic response
                      const res: any = await apiRequest('/maintenance/architect', {
                        method: 'POST',
                        auth: true,
                        body: { query: architectQuery }
                      });
                      setArchitectAnswer(res.answer);
                    } catch (err) {
                      toast.error("Failed to consult architect");
                    } finally {
                      setArchitectLoading(false);
                    }
                  }}
                  className="flex gap-4 relative"
                >
                  <input
                    value={architectQuery}
                    onChange={(e) => setArchitectQuery(e.target.value)}
                    placeholder="Ask a question (e.g., 'How do I add a new payment provider?')..."
                    className="flex-1 bg-black/30 border border-white/10 rounded-xl px-5 py-3 text-white focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 transition-all"
                  />
                  <button
                    type="submit"
                    disabled={architectLoading}
                    className="px-6 py-2 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-lg shadow-blue-900/20"
                  >
                    {architectLoading ? (
                      <RefreshCw className="w-4 h-4 animate-spin" />
                    ) : (
                      <>
                        Ask <ArrowLeft className="w-4 h-4 rotate-180" />
                      </>
                    )}
                  </button>
                </form>
              </div>
            </div>
          </motion.div>
        )}

        {activeTab === 'credits' && (
          <motion.div
            key="credits"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            <div className="bg-slate-900/30 border border-white/10 rounded-3xl p-6 backdrop-blur-xl">
              <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                <div>
                  <h3 className="text-lg font-semibold text-white">Grant / Revoke Credits</h3>
                  <p className="text-xs text-gray-500">Add or remove credits with a reason for the ledger.</p>
                </div>
                <div className="flex flex-col md:flex-row gap-3 w-full lg:w-auto">
                  <select
                    value={creditForm.userId}
                    onChange={(e) => setCreditForm((s) => ({ ...s, userId: e.target.value }))}
                    className="bg-black/40 border border-white/10 rounded-xl px-3 py-2 text-sm text-white"
                  >
                    <option value="">Select user</option>
                    {users.map((user) => (
                      <option key={user.id} value={user.id}>
                        {user.email}
                      </option>
                    ))}
                  </select>
                  <input
                    type="number"
                    value={creditForm.delta}
                    onChange={(e) => setCreditForm((s) => ({ ...s, delta: Number(e.target.value) }))}
                    className="w-28 bg-black/40 border border-white/10 rounded-xl px-3 py-2 text-sm text-white"
                    placeholder="+/- credits"
                  />
                  <input
                    type="text"
                    value={creditForm.reason}
                    onChange={(e) => setCreditForm((s) => ({ ...s, reason: e.target.value }))}
                    className="min-w-[200px] bg-black/40 border border-white/10 rounded-xl px-3 py-2 text-sm text-white"
                    placeholder="Reason (optional)"
                  />
                  <button
                    onClick={() => {
                      if (!creditForm.userId || !creditForm.delta) return;
                      handleAddCredits(
                        Number(creditForm.userId),
                        creditForm.delta,
                        creditForm.reason || 'manual_adjustment'
                      );
                      setCreditForm((s) => ({ ...s, reason: '' }));
                    }}
                    className="px-4 py-2 rounded-xl bg-brand-cyan text-black text-sm font-semibold hover:bg-brand-accent transition-colors"
                  >
                    Apply
                  </button>
                </div>
              </div>
            </div>



            <div className="bg-slate-900/30 border border-white/10 rounded-3xl overflow-hidden backdrop-blur-xl">
              <div className="p-6 border-b border-white/10 flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-white">Credit Ledger</h3>
                  <p className="text-xs text-gray-500">Most recent credit changes.</p>
                </div>
                <button
                  onClick={fetchLedger}
                  className="px-4 py-2 rounded-xl bg-white/10 hover:bg-white/20 text-white text-xs font-semibold flex items-center gap-2"
                >
                  <RefreshCw className="w-4 h-4" /> Refresh
                </button>
              </div>
              {ledgerError && (
                <div className="px-6 py-3 text-xs text-red-300 bg-red-500/10 border-b border-red-500/20">
                  {ledgerError}
                </div>
              )}
              {ledgerLoading ? (
                <div className="p-8 text-center text-gray-400">Loading ledger...</div>
              ) : (
                <>
                  {ledger.length === 0 ? (
                    <div className="p-8 text-center text-gray-400">No credit activity yet.</div>
                  ) : (
                    <table className="w-full text-left">
                      <thead className="bg-white/5 text-gray-400 text-xs font-bold uppercase tracking-widest border-b border-white/5">
                        <tr>
                          <th className="px-6 py-4">User</th>
                          <th className="px-6 py-4">Delta</th>
                          <th className="px-6 py-4">Balance</th>
                          <th className="px-6 py-4">Reason</th>
                          <th className="px-6 py-4">Source</th>
                          <th className="px-6 py-4">When</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-white/5">
                        {ledger.map((entry) => (
                          <tr key={entry.id} className="hover:bg-white/5 transition-colors">
                            <td className="px-6 py-4 text-sm text-white">{entry.user_email}</td>
                            <td className={`px-6 py-4 text-sm font-mono ${entry.delta >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                              {entry.delta >= 0 ? '+' : ''}
                              {entry.delta}
                            </td>
                            <td className="px-6 py-4 text-sm text-amber-400 font-mono">{entry.balance_after}</td>
                            <td className="px-6 py-4 text-xs text-gray-400">{entry.reason || '-'}</td>
                            <td className="px-6 py-4 text-xs text-gray-500">{entry.source}</td>
                            <td className="px-6 py-4 text-xs text-gray-500">{new Date(entry.created_at).toLocaleString()}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </>
              )}
            </div>
          </motion.div >
        )
        }
      </AnimatePresence >

      {
        selectedUser && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-6">
            <div className="w-full max-w-4xl bg-slate-900 border border-white/10 rounded-3xl p-6 space-y-6">
              <div className="flex items-start justify-between">
                <div>
                  <div className="text-xs uppercase tracking-[0.2em] text-gray-500">User Detail</div>
                  <h3 className="text-2xl font-bold text-white">{selectedUser.full_name || 'Anonymous'}</h3>
                  <p className="text-sm text-gray-400">{selectedUser.email}</p>
                  <div className="mt-3 flex items-center gap-4 text-xs text-gray-400">
                    <span>Credits: <span className="text-amber-300 font-semibold">{selectedUser.credits}</span></span>
                    {selectedUser.monthly_credits !== undefined && (
                      <span>Monthly: <span className="text-gray-200 font-semibold">{selectedUser.monthly_credits}</span></span>
                    )}
                  </div>
                </div>
                <button
                  onClick={closeUserDetails}
                  className="px-3 py-2 rounded-lg bg-white/5 hover:bg-white/10 text-gray-300 text-xs"
                >
                  Close
                </button>
              </div>

              {userLoading ? (
                <div className="text-center text-gray-400">Loading user details...</div>
              ) : (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="bg-white/5 border border-white/10 rounded-2xl p-4">
                    <h4 className="text-sm font-semibold text-white mb-3">Recent Jobs</h4>
                    {userJobs.length === 0 ? (
                      <p className="text-xs text-gray-500">No jobs found.</p>
                    ) : (
                      <div className="space-y-2">
                        {userJobs.map((job) => (
                          <div key={job.id} className="flex items-center justify-between text-xs text-gray-400">
                            <span>#{job.id}</span>
                            <span className="capitalize">{job.status}</span>
                            <span>{new Date(job.created_at).toLocaleDateString()}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="bg-white/5 border border-white/10 rounded-2xl p-4">
                    <h4 className="text-sm font-semibold text-white mb-3">Credit Activity</h4>
                    {userLedger.length === 0 ? (
                      <p className="text-xs text-gray-500">No ledger entries yet.</p>
                    ) : (
                      <div className="space-y-2">
                        {userLedger.map((entry) => (
                          <div key={entry.id} className="flex items-center justify-between text-xs text-gray-400">
                            <span className={entry.delta >= 0 ? 'text-emerald-300' : 'text-red-300'}>
                              {entry.delta >= 0 ? '+' : ''}
                              {entry.delta}
                            </span>
                            <span>{entry.reason || entry.source}</span>
                            <span>{new Date(entry.created_at).toLocaleDateString()}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        )
      }
    </div >
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


