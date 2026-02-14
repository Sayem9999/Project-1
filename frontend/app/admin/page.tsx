'use client';
import { useCallback, useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Activity, HardDrive, LayoutDashboard, Shield, Users, Video, Edit2, RefreshCw, Search, ArrowLeft, Database, Server, HeartPulse, Network, Wrench, CreditCard, ChevronRight, Sparkles, AlertCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';
import * as Sentry from '@sentry/nextjs';
import { apiRequest, ApiError, clearAuth } from '@/lib/api';
import SystemMap from '@/components/admin/SystemMap';
import StatCard from '@/components/admin/StatCard';
import StatusBadge from '@/components/admin/StatusBadge';
import UserTable from '@/components/admin/UserTable';
import JobTable from '@/components/admin/JobTable';
import SystemTrends from '@/components/admin/SystemTrends';
import UsageLeaderboard from '@/components/admin/UsageLeaderboard';
import AutonomyPanel from '@/components/admin/AutonomyPanel';
import { Button } from '@/components/ui/Button';

interface SystemStats {
  users: { total: number; active_24h?: number };
  jobs: { total: number; recent_24h: number };
  storage: { used_gb: number; limit_gb: number; percent: number; files: number };
  trends?: {
    jobs_by_day: { date: string; count: number }[];
    failures_by_day: { date: string; count: number }[];
    users_by_day: { date: string; count: number }[];
  };
  performance?: {
    avg_latency_ms: number;
    tracked_count: number;
  };
  analytics?: {
    pro_jobs: number;
    standard_jobs: number;
    revenue_est: number;
    leaderboard: { email: string; count: number }[];
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

interface AutonomyStatus {
  enabled: boolean;
  running: boolean;
  profile_mode: string;
  profile: Record<string, number>;
  available_profiles: string[];
  metrics: {
    run_count: number;
    heal_count: number;
    improve_count: number;
    skip_high_load_count: number;
  };
  last_heal_at?: string | null;
  last_improve_at?: string | null;
  last_result?: {
    idle?: boolean;
    high_load?: boolean;
    load?: {
      cpu_percent?: number;
      memory_percent?: number;
    };
  };
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

interface AdminActionLogEntry {
  id: number;
  admin_user_id: number;
  admin_email: string;
  action: string;
  target_type: string;
  target_id?: string | null;
  details?: Record<string, any> | null;
  created_at: string;
}

export default function AdminDashboardPage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'overview' | 'users' | 'jobs' | 'credits' | 'system'>('overview');
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [health, setHealth] = useState<AdminHealth | null>(null);
  const [autonomy, setAutonomy] = useState<AutonomyStatus | null>(null);
  const [autonomyLoading, setAutonomyLoading] = useState(false);
  const [autonomyActionLoading, setAutonomyActionLoading] = useState(false);
  const [autonomyAuditLogs, setAutonomyAuditLogs] = useState<AdminActionLogEntry[]>([]);
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
  const [creditForm, setCreditForm] = useState({ userId: '', delta: 1, reason: '' });
  const [selectedUser, setSelectedUser] = useState<UserData | null>(null);
  const [userJobs, setUserJobs] = useState<JobData[]>([]);
  const [userLedger, setUserLedger] = useState<CreditLedgerEntry[]>([]);
  const [userLoading, setUserLoading] = useState(false);
  const [architectQuery, setArchitectQuery] = useState('');
  const [architectAnswer, setArchitectAnswer] = useState('');
  const [architectLoading, setArchitectLoading] = useState(false);
  const [mounted, setMounted] = useState(false);
  const STALL_THRESHOLD_MINUTES = 10;
  const STALL_THRESHOLD_MS = STALL_THRESHOLD_MINUTES * 60 * 1000;

  useEffect(() => {
    setMounted(true);
  }, []);

  const fetchData = useCallback(async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    try {
      const results = await Promise.allSettled([
        apiRequest<SystemStats>('/admin/stats', { auth: true }),
        apiRequest<UserData[]>('/admin/users', { auth: true }),
        apiRequest<JobData[]>('/admin/jobs', { auth: true }),
        apiRequest<AdminHealth>('/admin/health', { auth: true }),
        apiRequest<AutonomyStatus>('/maintenance/autonomy/status', { auth: true }),
      ]);

      const statsData = results[0].status === 'fulfilled' ? results[0].value : null;
      const usersData = results[1].status === 'fulfilled' ? results[1].value : [];
      const jobsData = results[2].status === 'fulfilled' ? results[2].value : [];
      const healthData = results[3].status === 'fulfilled' ? results[3].value : null;
      const autonomyData = results[4].status === 'fulfilled' ? results[4].value : null;

      if (statsData) setStats(statsData);
      setUsers(Array.isArray(usersData) ? usersData : []);
      setJobs(Array.isArray(jobsData) ? jobsData : []);
      if (healthData) setHealth(healthData);
      if (autonomyData) setAutonomy(autonomyData);

      setLoading(false);
      setAccessDenied(false);
    } catch (err: any) {
      Sentry.captureException(err);
      if (err instanceof ApiError) {
        if (err.status === 403) setAccessDenied(true);
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

  const fetchAutonomyStatus = useCallback(async () => {
    setAutonomyLoading(true);
    try {
      const [status, audit] = await Promise.all([
        apiRequest<AutonomyStatus>('/maintenance/autonomy/status', { auth: true }),
        apiRequest<AdminActionLogEntry[]>('/admin/audit/actions?action_prefix=autonomy&limit=50', { auth: true }),
      ]);
      setAutonomy(status);
      setAutonomyAuditLogs(audit);
    } catch (err: any) {
      if (err instanceof ApiError && err.isAuth) {
        clearAuth();
        router.push('/login');
        return;
      }
      toast.error('Autonomy status failed');
    } finally {
      setAutonomyLoading(false);
    }
  }, [router]);

  const runAutonomy = useCallback(async (opts: { force_heal?: boolean; force_improve?: boolean }) => {
    setAutonomyActionLoading(true);
    try {
      const query = new URLSearchParams();
      if (opts.force_heal) query.set('force_heal', 'true');
      if (opts.force_improve) query.set('force_improve', 'true');
      await apiRequest(`/maintenance/autonomy/run?${query.toString()}`, { method: 'POST', auth: true });
      await fetchAutonomyStatus();
      toast.success('Autonomy cycle completed');
    } catch (err: any) {
      toast.error(err instanceof ApiError ? err.message : 'Autonomy run failed');
    } finally {
      setAutonomyActionLoading(false);
    }
  }, [fetchAutonomyStatus]);

  const setAutonomyProfile = useCallback(async (mode: string) => {
    setAutonomyActionLoading(true);
    try {
      const query = new URLSearchParams({ mode });
      const data = await apiRequest<AutonomyStatus>(`/maintenance/autonomy/profile?${query.toString()}`, { method: 'POST', auth: true });
      setAutonomy(data);
      await fetchAutonomyStatus();
      toast.success(`Autonomy mode switched to ${mode}`);
    } catch (err: any) {
      toast.error(err instanceof ApiError ? err.message : 'Failed to switch autonomy mode');
    } finally {
      setAutonomyActionLoading(false);
    }
  }, [fetchAutonomyStatus]);

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
      if (err instanceof ApiError && err.isAuth) {
        clearAuth();
        router.push('/login');
        return;
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
    if (activeTab === 'credits') fetchLedger();
  }, [activeTab, fetchLedger]);

  useEffect(() => {
    if (activeTab !== 'jobs') return;
    fetchJobs(true);
    const interval = setInterval(() => fetchJobs(true), 15000);
    return () => clearInterval(interval);
  }, [activeTab, fetchJobs]);

  useEffect(() => {
    if (activeTab !== 'system') return;
    fetchAutonomyStatus();
    const interval = setInterval(fetchAutonomyStatus, 15000);
    return () => clearInterval(interval);
  }, [activeTab, fetchAutonomyStatus]);

  const handleUpdateCredits = async (userId: number, newCredits: number, reason = 'manual_set') => {
    const toastId = toast.loading('Syncing credits...');
    try {
      await apiRequest(`/admin/users/${userId}/credits?credits=${newCredits}&reason=${encodeURIComponent(reason)}`, {
        method: 'PATCH',
        auth: true,
      });
      setEditingCredits(null);
      fetchData();
      fetchLedger();
      toast.success('Credits synchronized', { id: toastId });
    } catch (err: any) {
      toast.error('Sync failed', { id: toastId, description: err.message });
    }
  };

  const handleAddCredits = async (userId: number, delta: number, reason = 'manual_adjustment') => {
    const toastId = toast.loading('Updating balance...');
    try {
      await apiRequest(`/admin/users/${userId}/credits/add?delta=${delta}&reason=${encodeURIComponent(reason)}`, {
        method: 'PATCH',
        auth: true,
      });
      fetchData();
      fetchLedger();
      toast.success('Balance updated', { id: toastId });
    } catch (err: any) {
      toast.error('Update failed', { id: toastId, description: err.message });
    }
  };

  const handleAdminAction = async (jobId: number, action: 'cancel' | 'retry' | 'force-retry') => {
    const toastId = toast.loading(`Executing ${action}...`);
    try {
      await apiRequest(`/admin/jobs/${jobId}/${action}`, { method: 'POST', auth: true });
      fetchJobs(true);
      toast.success(`Action ${action} executed`, { id: toastId });
    } catch (err: any) {
      toast.error(`Execution failed`, { id: toastId, description: err.message });
    }
  };

  const handleCleanup = async () => {
    const toastId = toast.loading('Running storage cleanup...');
    try {
      const res: any = await apiRequest('/admin/cleanup', { method: 'POST', auth: true });
      fetchData();
      toast.success('Cleanup complete', { id: toastId, description: `Freed ${res.mb_freed} MB` });
    } catch (err: any) {
      toast.error('Cleanup failed', { id: toastId, description: err.message });
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

  const filteredUsers = useMemo(() => {
    if (!userSearch) return users;
    const q = userSearch.toLowerCase();
    return users.filter((u) => `${u.email} ${u.full_name ?? ''}`.toLowerCase().includes(q));
  }, [users, userSearch]);

  const processingCount = useMemo(() => jobs.filter(j => j.status === 'processing').length, [jobs]);

  const filteredJobs = useMemo(() => {
    let list = jobs;
    if (jobFilter !== 'all') list = list.filter((j) => j.status === jobFilter);
    if (!jobSearch) return list;
    const q = jobSearch.toLowerCase();
    return list.filter((j) => `${j.id} ${j.user_id} ${j.theme} ${j.progress_message}`.toLowerCase().includes(q));
  }, [jobs, jobFilter, jobSearch]);

  const isStalledJob = (job: JobData) => {
    if (job.status !== 'processing' && job.status !== 'queued') return false;
    const last = new Date(job.updated_at || job.created_at).getTime();
    return !Number.isNaN(last) && Date.now() - last > STALL_THRESHOLD_MS;
  };

  if (!mounted) return null;

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <div className="w-12 h-12 border-4 border-brand-cyan/20 border-t-brand-cyan rounded-full animate-spin mb-4" />
        <p className="text-xs font-black uppercase tracking-[0.3em] text-gray-500 animate-pulse">Syncing Admin Node</p>
      </div>
    );
  }

  if (accessDenied) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center p-6">
        <div className="max-w-md w-full glass-panel border-red-500/20 rounded-[32px] p-10 text-center relative overflow-hidden">
          <div className="absolute inset-0 bg-red-500/5 blur-3xl opacity-20" />
          <div className="w-20 h-20 mx-auto mb-6 rounded-3xl bg-red-500/10 text-red-400 flex items-center justify-center border border-red-500/20 relative z-10">
            <Shield className="w-10 h-10" />
          </div>
          <h2 className="text-2xl font-black text-white mb-3 tracking-tight relative z-10">Secure Access Only</h2>
          <p className="text-gray-500 mb-10 text-sm leading-relaxed relative z-10">Administrative oversight requires elevated privileges. Your account is currently restricted.</p>
          <Link href="/dashboard" className="relative z-10">
            <Button variant="secondary" size="lg" className="w-full">Return to Dashboard</Button>
          </Link>
        </div>
      </div>
    );
  }

  const tabs = [
    { id: 'overview', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'users', label: 'Users', icon: Users },
    { id: 'jobs', label: 'Operations', icon: Video },
    { id: 'credits', label: 'Economics', icon: CreditCard },
    { id: 'system', label: 'Architecture', icon: Network },
  ];

  return (
    <div className="max-w-[1600px] mx-auto space-y-8 md:space-y-12 px-2 md:px-0">
      {/* Header Area */}
      <div className="flex flex-col xl:flex-row xl:items-end justify-between gap-8">
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <div className="px-3 py-1 rounded-full bg-brand-cyan/10 border border-brand-cyan/30 text-[10px] font-black uppercase tracking-widest text-brand-cyan">SECURE_NODE</div>
            <div className="flex items-center gap-2 text-[10px] font-bold text-gray-500 uppercase tracking-widest">
              <Activity className="w-3 h-3 text-emerald-400" />
              Live Telemetry Active
            </div>
          </div>
          <div>
            <h1 className="text-4xl md:text-5xl font-black tracking-tighter text-white mb-4">Operations Center</h1>
            <p className="text-gray-500 max-w-2xl text-base md:text-lg leading-relaxed">Executive oversight and system governance. Orchestrate resources, scale impact, and maintain pipeline health.</p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-4">
          <Button variant="secondary" onClick={handleCleanup} className="font-black text-[10px] uppercase tracking-widest border-brand-cyan/20 text-brand-cyan">
            <Wrench className="w-4 h-4 mr-2" /> Storage Cleanup
          </Button>
          <Button variant="secondary" onClick={fetchData} className="font-black text-[10px] uppercase tracking-widest">
            <RefreshCw className="w-4 h-4 mr-2" /> Refresh State
          </Button>
          <div className="px-6 py-3 glass-panel rounded-2xl border-white/5 text-xs font-mono text-gray-400">
            NODE_TIME: <span className="text-white">{new Date().toLocaleTimeString()}</span>
          </div>
          <Link href="/dashboard">
            <button className="p-3 bg-white/5 hover:bg-white/10 rounded-2xl transition-all border border-white/5 group">
              <ArrowLeft className="w-5 h-5 text-gray-500 group-hover:text-white transition-colors" />
            </button>
          </Link>
        </div>
      </div>

      {error && (
        <div className="glass-panel border-red-500/20 bg-red-500/5 p-4 rounded-2xl flex items-center gap-3 animate-in slide-in-from-top-4">
          <AlertCircle className="w-5 h-5 text-red-500" />
          <span className="text-sm font-bold text-red-200">{error}</span>
        </div>
      )}

      {/* Premium Stat Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-5 gap-6">
        {[
          { icon: Users, title: "Total Fleet", value: stats?.users?.total ?? 0, sub: "Registered Entities", color: "cyan" },
          { icon: Sparkles, title: "Pro Volume", value: stats?.analytics?.pro_jobs ?? 0, sub: `${stats?.analytics?.standard_jobs ?? 0} Standard Jobs`, color: "emerald" },
          { icon: CreditCard, title: "Rev. Estimate", value: `$${stats?.analytics?.revenue_est ?? 0}`, sub: "Projected Gross (Pro)", color: "amber" },
          { icon: Video, title: "Pipeline Volume", value: stats?.jobs?.total ?? 0, sub: `+${stats?.jobs?.recent_24h ?? 0} New Exports`, color: "violet" },
          { icon: HardDrive, title: "Storage Index", value: `${stats?.storage?.percent ?? 0}%`, sub: `${stats?.storage?.used_gb ?? 0}GB Utilized`, color: "amber", progress: stats?.storage?.percent },
        ].map((s, i) => (
          <StatCard key={i} icon={s.icon} title={s.title} value={s.value} subtext={s.sub} color={s.color as any} progress={s.progress} />
        ))}
      </div>

      {/* System Health View */}
      {health && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 glass-panel p-8 rounded-[32px] border-white/5 relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-64 h-64 bg-brand-cyan/5 rounded-full blur-[80px] -translate-y-1/2 translate-x-1/2 group-hover:bg-brand-cyan/10 transition-colors duration-1000" />
            <div className="flex items-center justify-between mb-8 relative z-10">
              <div>
                <h3 className="text-lg font-black tracking-tight text-white mb-1">Core Infrastructure</h3>
                <p className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Connectivity & Resource States</p>
              </div>
              <HeartPulse className="w-6 h-6 text-emerald-400 animate-pulse" />
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 relative z-10">
              <div className="p-5 rounded-[24px] bg-white/[0.03] border border-white/5 hover:border-white/10 transition-colors">
                <div className="text-[10px] font-black text-gray-400 mb-3 flex items-center gap-2 uppercase tracking-widest">
                  <Database className="w-4 h-4 text-brand-cyan" /> Persistence Layer
                </div>
                <div className="flex items-center justify-between">
                  <span className={`text-sm font-black uppercase tracking-widest ${health?.db?.reachable ? 'text-emerald-400' : 'text-red-400'}`}>
                    {health?.db?.reachable ? 'Online_Reachable' : 'Persistent_Fail'}
                  </span>
                  <div className={`w-2 h-2 rounded-full ${health?.db?.reachable ? 'bg-emerald-400' : 'bg-red-400'} shadow-[0_0_10px_rgba(52,211,153,0.5)]`} />
                </div>
              </div>
              <div className="p-5 rounded-[24px] bg-white/[0.03] border border-white/5 hover:border-white/10 transition-colors">
                <div className="text-[10px] font-black text-gray-400 mb-3 flex items-center gap-2 uppercase tracking-widest">
                  <Server className="w-4 h-4 text-brand-violet" /> Cache Orchestrator
                </div>
                <div className="flex items-center justify-between">
                  <span className={`text-sm font-black uppercase tracking-widest ${health?.redis?.reachable ? 'text-emerald-400' : 'text-red-400'}`}>
                    {health?.redis?.configured ? (health?.redis?.reachable ? 'Redis_Active' : 'Broker_Hang') : 'Void_Config'}
                  </span>
                  <div className={`w-2 h-2 rounded-full ${health?.redis?.reachable ? 'bg-emerald-400' : 'bg-red-400'}`} />
                </div>
              </div>
            </div>
          </div>

          <div className="space-y-6">
            <div className="glass-panel p-8 rounded-[32px] border-white/5 relative overflow-hidden bg-gradient-to-br from-white/[0.02] to-transparent">
              <h3 className="text-[10px] font-black font-bold text-gray-500 uppercase tracking-[0.3em] mb-6">Agent LLM Cluster</h3>
              <div className="space-y-4">
                {Object.entries(health.llm || {}).map(([name, item]) => (
                  <div key={name} className="flex items-center justify-between p-3 rounded-2xl bg-white/[0.02] border border-white/5">
                    <span className="text-[10px] font-black text-white uppercase tracking-widest">{name}</span>
                    <div className={`text-[10px] font-black px-3 py-1 rounded-lg ${item.is_healthy ? 'bg-emerald-400/10 text-emerald-400' : 'bg-red-400/10 text-red-300'}`}>
                      {item.is_healthy ? 'HEALTH_OK' : 'FAIL_STATE'}
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <UsageLeaderboard entries={stats?.analytics?.leaderboard ?? []} />
          </div>
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="flex items-center gap-2 md:gap-4 p-2 glass-panel rounded-[24px] border-white/5 overflow-x-auto no-scrollbar scroll-smooth">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex items-center gap-3 px-6 py-3.5 rounded-2xl text-[10px] font-black uppercase tracking-[0.2em] transition-all whitespace-nowrap min-w-fit ${activeTab === tab.id
              ? 'bg-gradient-to-r from-brand-cyan to-brand-violet text-white shadow-xl shadow-brand-cyan/20 scale-105'
              : 'text-gray-500 hover:text-white hover:bg-white/5'
              }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Main Content Render */}
      <AnimatePresence mode="wait">
        {activeTab === 'overview' && (
          <motion.div key="overview" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 glass-panel rounded-[32px] overflow-hidden border-white/5">
              <div className="p-8 border-b border-white/5">
                <h3 className="text-lg font-black tracking-tight text-white uppercase tracking-widest">Global Operations Feed</h3>
              </div>
              <div className="p-4 space-y-3">
                {jobs.slice(0, 6).map((job) => (
                  <div key={job.id} className="flex items-center justify-between p-5 rounded-3xl bg-white/[0.02] hover:bg-white/[0.04] transition-all group border border-transparent hover:border-white/5">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-2xl bg-white/5 flex items-center justify-center font-mono text-[10px] text-brand-cyan group-hover:scale-110 transition-transform">#{job.id}</div>
                      <div>
                        <div className="text-sm font-black text-white mb-1 group-hover:text-brand-cyan transition-colors">{job.theme.toUpperCase()} • {job.id}</div>
                        <div className="text-[10px] font-bold text-gray-500 uppercase tracking-widest line-clamp-1">{job.progress_message}</div>
                      </div>
                    </div>
                    <StatusBadge status={job.status} />
                  </div>
                ))}
              </div>
            </div>
            <div className="glass-panel rounded-[32px] overflow-hidden border-white/5">
              <div className="p-8 border-b border-white/5">
                <h3 className="text-lg font-black tracking-tight text-white uppercase tracking-widest">Active Creators</h3>
              </div>
              <div className="p-4 space-y-3">
                {users.slice(0, 6).map((user) => (
                  <div key={user.id} className="flex items-center justify-between p-5 rounded-3xl bg-white/[0.02] border border-transparent hover:border-white/5">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-brand-cyan/20 to-brand-violet/20 flex items-center justify-center font-black text-[10px] text-white overflow-hidden">
                        {user.email[0].toUpperCase()}
                      </div>
                      <div>
                        <div className="text-sm font-black text-white truncate max-w-[120px]">{user.full_name || 'Creator'}</div>
                        <div className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">{user.email}</div>
                      </div>
                    </div>
                    <div className="px-3 py-1 rounded-lg bg-amber-400/10 text-amber-400 text-[10px] font-black">{user.credits} CR</div>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}

        {activeTab === 'users' && (
          <motion.div key="users" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} className="glass-panel rounded-[32px] overflow-hidden border-white/5">
            <div className="p-8 border-b border-white/5 flex flex-col md:flex-row md:items-center justify-between gap-6">
              <div>
                <h3 className="text-lg font-black text-white uppercase tracking-widest mb-1">Creator Registry</h3>
                <p className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Economic Oversight & Perms</p>
              </div>
              <div className="relative w-full md:w-80">
                <Search className="w-5 h-5 text-gray-500 absolute left-4 top-1/2 -translate-y-1/2" />
                <input
                  value={userSearch}
                  onChange={(e) => setUserSearch(e.target.value)}
                  placeholder="SEARCH BY IDENTITY"
                  className="w-full bg-white/5 border border-white/10 rounded-2xl pl-12 pr-6 py-3.5 text-xs text-white focus:outline-none focus:border-brand-cyan/50 font-bold tracking-widest transition-all"
                />
              </div>
            </div>
            <UserTable
              users={filteredUsers}
              editingCredits={editingCredits}
              setEditingCredits={setEditingCredits}
              handleUpdateCredits={handleUpdateCredits}
              handleAddCredits={handleAddCredits}
              openUserDetails={openUserDetails}
            />
          </motion.div>
        )}

        {activeTab === 'jobs' && (
          <motion.div key="jobs" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} className="glass-panel rounded-[32px] overflow-hidden border-white/5">
            <div className="p-8 border-b border-white/5 flex flex-col xl:flex-row xl:items-center justify-between gap-6">
              <div>
                <h3 className="text-lg font-black text-white uppercase tracking-widest mb-1">Operation Threads</h3>
                <p className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">System Load: {processingCount} Parallel Agents</p>
              </div>
              <div className="flex flex-col md:flex-row items-center gap-4">
                <div className="relative w-full md:w-64">
                  <Search className="w-5 h-5 text-gray-500 absolute left-4 top-1/2 -translate-y-1/2" />
                  <input
                    value={jobSearch}
                    onChange={(e) => setJobSearch(e.target.value)}
                    placeholder="FILTER_ID_OR_THEME"
                    className="w-full bg-white/5 border border-white/10 rounded-2xl pl-12 pr-6 py-3.5 text-[10px] text-white focus:outline-none focus:border-brand-cyan/50 font-black tracking-widest transition-all"
                  />
                </div>
                <div className="flex bg-white/5 p-1.5 rounded-2xl border border-white/5 overflow-x-auto no-scrollbar">
                  {['all', 'processing', 'complete', 'failed'].map((val) => (
                    <button
                      key={val}
                      onClick={() => setJobFilter(val as any)}
                      className={`px-4 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${jobFilter === val ? 'bg-brand-cyan text-black shadow-lg shadow-brand-cyan/20' : 'text-gray-500 hover:text-white'}`}
                    >
                      {val}
                    </button>
                  ))}
                </div>
              </div>
            </div>
            <JobTable
              jobs={filteredJobs}
              isStalledJob={isStalledJob}
              handleAdminForceRetry={(id) => handleAdminAction(id, 'force-retry')}
              handleAdminCancel={(id) => handleAdminAction(id, 'cancel')}
              handleAdminRetry={(id) => handleAdminAction(id, 'retry')}
            />
          </motion.div>
        )}

        {activeTab === 'system' && (
          <motion.div key="system" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} className="space-y-8">
            <AutonomyPanel
              autonomy={autonomy}
              loading={autonomyLoading}
              actionLoading={autonomyActionLoading}
              onRefresh={fetchAutonomyStatus}
              onSetMode={setAutonomyProfile}
              onRun={runAutonomy}
              auditLogs={autonomyAuditLogs}
            />
            <SystemMap />
            <div className="glass-panel p-10 rounded-[40px] border-white/5 relative overflow-hidden">
              <div className="flex items-center gap-6 mb-10 relative z-10">
                <div className="p-4 bg-brand-cyan/10 rounded-3xl text-brand-cyan border border-brand-cyan/20">
                  <Network className="w-8 h-8" />
                </div>
                <div>
                  <h3 className="text-2xl font-black text-white tracking-tight mb-2 uppercase tracking-widest">Architectural Analysis</h3>
                  <p className="text-sm text-gray-500 max-w-xl">Deep cognitive scan of the structural integrity and logic flow across the Proedit ecosystem.</p>
                </div>
              </div>
              <div className="space-y-6 relative z-10">
                {architectAnswer && (
                  <div className="p-8 bg-white/[0.03] rounded-[32px] border border-white/10 animate-in fade-in zoom-in-95">
                    <div className="flex items-center gap-3 mb-6">
                      <Sparkles className="w-4 h-4 text-brand-cyan animate-pulse" />
                      <span className="text-[10px] font-black text-brand-cyan uppercase tracking-[0.4em]">Integrated Intelligence Output</span>
                    </div>
                    <div className="text-sm text-gray-300 whitespace-pre-wrap font-mono leading-loose tracking-tight whitespace-pre-wrap">
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
                      const res: any = await apiRequest('/maintenance/architect', {
                        method: 'POST', auth: true, body: { query: architectQuery }
                      });
                      setArchitectAnswer(res.answer);
                    } catch { toast.error("Architect node timed out"); } finally { setArchitectLoading(false); }
                  }}
                  className="flex flex-col sm:flex-row gap-4"
                >
                  <input
                    value={architectQuery}
                    onChange={(e) => setArchitectQuery(e.target.value)}
                    placeholder="QUERRY_SYSTEM_ARCHITECT_..."
                    className="flex-1 bg-white/5 border border-white/10 rounded-[24px] px-8 py-4 text-sm text-white focus:outline-none focus:border-brand-cyan/50 font-bold transition-all placeholder:text-gray-600 uppercase tracking-widest font-mono"
                  />
                  <Button variant="glow" size="lg" loading={architectLoading} className="px-10 font-black text-xs uppercase tracking-[0.3em]">
                    CONSULT
                  </Button>
                </form>
              </div>
            </div>
          </motion.div>
        )}

        {activeTab === 'credits' && (
          <motion.div key="credits" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} className="space-y-8">
            <div className="glass-panel p-8 rounded-[32px] border-white/5 relative overflow-hidden">
              <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-8 relative z-10">
                <div>
                  <h3 className="text-lg font-black text-white uppercase tracking-widest mb-1">Economic Adjustments</h3>
                  <p className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Manual Balance Modulation</p>
                </div>
                <div className="flex flex-wrap items-center gap-4">
                  <select
                    value={creditForm.userId}
                    onChange={(e) => setCreditForm(s => ({ ...s, userId: e.target.value }))}
                    className="bg-white/5 border border-white/10 rounded-2xl px-6 py-3.5 text-xs text-white focus:border-brand-cyan/50 font-black uppercase tracking-widest transition-all"
                  >
                    <option value="" className="bg-obsidian-900">SELECT IDENTITY</option>
                    {users.map(u => <option key={u.id} value={u.id} className="bg-obsidian-900">{u.email}</option>)}
                  </select>
                  <input
                    type="number"
                    value={creditForm.delta}
                    onChange={(e) => setCreditForm(s => ({ ...s, delta: Number(e.target.value) }))}
                    className="w-32 bg-white/5 border border-white/10 rounded-2xl px-6 py-3.5 text-xs text-white focus:border-brand-cyan/50 font-black uppercase tracking-widest text-center"
                    placeholder="UNIT_Δ"
                  />
                  <input
                    type="text"
                    value={creditForm.reason}
                    onChange={(e) => setCreditForm(s => ({ ...s, reason: e.target.value }))}
                    className="min-w-[280px] bg-white/5 border border-white/10 rounded-2xl px-6 py-3.5 text-xs text-white focus:border-brand-cyan/50 font-bold uppercase tracking-widest"
                    placeholder="AUDIT_LOG_REASON"
                  />
                  <Button variant="glow" onClick={() => {
                    if (!creditForm.userId || !creditForm.delta) return;
                    handleAddCredits(Number(creditForm.userId), creditForm.delta, creditForm.reason || 'manual_adjustment');
                    setCreditForm(s => ({ ...s, reason: '' }));
                  }} className="px-10">MODULATE</Button>
                </div>
              </div>
            </div>

            <div className="glass-panel rounded-[32px] overflow-hidden border-white/5">
              <div className="p-8 border-b border-white/5 flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-black text-white uppercase tracking-widest mb-1">Economic Ledger</h3>
                  <p className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Historical Transaction Log</p>
                </div>
                <Button variant="secondary" onClick={fetchLedger} className="font-black text-[10px] uppercase tracking-widest">
                  <RefreshCw className="w-4 h-4 mr-2" /> Sync Ledger
                </Button>
              </div>
              <div className="overflow-x-auto no-scrollbar">
                <table className="w-full text-left">
                  <thead className="bg-white/[0.03] text-gray-500 text-[10px] font-black uppercase tracking-[0.2em] border-b border-white/5">
                    <tr>
                      <th className="px-8 py-5">Identity</th>
                      <th className="px-8 py-5">Delta_Value</th>
                      <th className="px-8 py-5">Post_Balance</th>
                      <th className="px-8 py-5">Event_Reason</th>
                      <th className="px-8 py-5">Timestamp</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {ledger.map((entry) => (
                      <tr key={entry.id} className="hover:bg-white/[0.02] transition-colors border-l-2 border-transparent hover:border-brand-cyan">
                        <td className="px-8 py-6">
                          <div className="text-xs font-black text-white uppercase tracking-widest">{entry.user_email}</div>
                          <div className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mt-1 opacity-50">{entry.source}</div>
                        </td>
                        <td className={`px-8 py-6 text-sm font-black italic tracking-tighter ${entry.delta >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                          {entry.delta >= 0 ? '+' : ''}{entry.delta}
                        </td>
                        <td className="px-8 py-6 text-sm font-black text-amber-400 font-mono">{entry.balance_after} CR</td>
                        <td className="px-8 py-6 text-[10px] font-bold text-gray-400 uppercase tracking-widest max-w-xs truncate">{entry.reason || 'SYSTEM_EVENT'}</td>
                        <td className="px-8 py-6 text-[10px] font-bold text-gray-600 uppercase tracking-widest whitespace-nowrap">{new Date(entry.created_at).toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div >
  );
}

// SVG defined above, lucide-react import fixed at top
