import { useEffect, useState, useCallback } from 'react';
import { AreaChart, Area, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Activity, HardDrive, Cpu, AlertTriangle, Info, MemoryStick, Gauge, Clock, RefreshCw } from 'lucide-react';

// =========================================================================
// Models
// =========================================================================
interface Metric {
  timestamp: string;
  cpu_percent: number;
  memory_percent: number;
  memory_used_gb: number;
  memory_total_gb: number;
  disk_percent: number;
  disk_used_gb: number;
  disk_total_gb: number;
}

interface Insight {
  timestamp: string;
  severity: string;
  component: string;
  message: string;
  root_cause: string | null;
}

// =========================================================================
// Time Range Options
// =========================================================================
const TIME_RANGES = [
  { label: '1H', hours: 1 },
  { label: '6H', hours: 6 },
  { label: '24H', hours: 24 },
  { label: '3D', hours: 72 },
  { label: '7D', hours: 168 },
  { label: '14D', hours: 336 },
];

// =========================================================================
// API Service
// =========================================================================
const API_BASE = 'http://127.0.0.1:8000/api/v1';

const apiService = {
  async fetchMetrics(hours?: number, limit?: number): Promise<Metric[]> {
    const params = new URLSearchParams();
    if (hours) params.set('hours', hours.toString());
    if (limit) params.set('limit', limit.toString());
    const res = await fetch(`${API_BASE}/metrics?${params.toString()}&_t=${Date.now()}`);
    if (!res.ok) throw new Error('Failed to fetch metrics');
    return res.json();
  },
  async fetchInsights(limit = 10): Promise<Insight[]> {
    const res = await fetch(`${API_BASE}/insights?limit=${limit}&_t=${Date.now()}`);
    if (!res.ok) throw new Error('Failed to fetch insights');
    return res.json();
  }
};

// =========================================================================
// Mock Data
// =========================================================================
function generateMockMetrics(count: number): Metric[] {
  const now = Date.now();
  return Array.from({ length: count }, (_, i) => ({
    timestamp: new Date(now - (count - i) * 5000).toISOString(),
    cpu_percent: Math.round(15 + Math.random() * 55 + Math.sin(i * 0.3) * 15),
    memory_percent: Math.round(45 + Math.random() * 20 + Math.cos(i * 0.2) * 10),
    memory_used_gb: +(6.2 + Math.random() * 3).toFixed(2),
    memory_total_gb: 16,
    disk_percent: Math.round(62 + Math.random() * 5),
    disk_used_gb: +(450 + Math.random() * 30).toFixed(2),
    disk_total_gb: 512,
  }));
}

function generateMockInsights(): Insight[] {
  return [
    { timestamp: new Date().toISOString(), severity: "WARNING", component: "CPU", message: "CPU usage elevated at 78.5% — above baseline average.", root_cause: "Node.js process consuming high CPU during build." },
    { timestamp: new Date(Date.now() - 30000).toISOString(), severity: "CRITICAL", component: "Memory", message: "Memory usage reached 92.3% — critically high.", root_cause: "Potential memory leak in background service worker." },
    { timestamp: new Date(Date.now() - 120000).toISOString(), severity: "WARNING", component: "CPU", message: "Unusual CPU spike detected. Current: 85%, Average: 42.3%", root_cause: "Sudden burst in process activity." },
  ];
}

// =========================================================================
// Dashboard
// =========================================================================
function Dashboard() {
  const [metrics, setMetrics] = useState<Metric[]>([]);
  const [insights, setInsights] = useState<Insight[]>([]);
  const [isLive, setIsLive] = useState(false);
  const [selectedRange, setSelectedRange] = useState(1); // hours
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  const fetchData = useCallback(async () => {
    try {
      const [metricsData, insightsData] = await Promise.all([
        apiService.fetchMetrics(selectedRange),
        apiService.fetchInsights(10),
      ]);
      setMetrics(metricsData);
      setInsights(insightsData);
      setIsLive(true);
    } catch {
      setMetrics(generateMockMetrics(30));
      setInsights(generateMockInsights());
      setIsLive(false);
    }
    setLastUpdated(new Date());
  }, [selectedRange]);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, [fetchData]);

  const latest = metrics[metrics.length - 1];

  const getStatus = (value: number | undefined, warn: number, crit: number) => {
    if (!value) return 'success';
    if (value >= crit) return 'danger';
    if (value >= warn) return 'warning';
    return 'success';
  };

  const formatTime = (ts: string) => {
    try {
      // Ensure the timestamp is treated as UTC if it doesn't have a timezone indicator
      const timeStr = ts.endsWith('Z') || ts.includes('+') ? ts : ts + 'Z';
      const d = new Date(timeStr);
      if (selectedRange <= 24) return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
      return d.toLocaleDateString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    } catch { return ts; }
  };

  // Downsample data for large ranges to keep chart readable
  const chartData = selectedRange > 24 && metrics.length > 200
    ? metrics.filter((_, i) => i % Math.ceil(metrics.length / 200) === 0)
    : metrics;

  return (
    <div className="min-h-screen p-4 md:p-8 max-w-[1400px] mx-auto space-y-5">
      {/* Header */}
      <header className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold flex items-center gap-3 text-slate-100">
            <Gauge className="text-primary w-7 h-7" />
            InfraMonitor
          </h1>
          <p className="text-slate-500 mt-1 text-sm">Real-time local infrastructure observability</p>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-[10px] text-slate-600">Updated {lastUpdated.toLocaleTimeString()}</span>
          <div className="flex items-center gap-2 bg-surface px-3 py-1.5 rounded-lg border border-slate-700/50">
            <span className="relative flex h-2 w-2">
              <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${isLive ? 'bg-success' : 'bg-warning'}`}></span>
              <span className={`relative inline-flex rounded-full h-2 w-2 ${isLive ? 'bg-success' : 'bg-warning'}`}></span>
            </span>
            <span className="text-xs font-medium text-slate-400">{isLive ? 'Live' : 'Demo'}</span>
          </div>
        </div>
      </header>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <KpiCard title="CPU Usage" value={latest ? `${latest.cpu_percent}%` : '--'} subtitle="Processor load" icon={<Cpu className="w-5 h-5 text-primary" />} status={getStatus(latest?.cpu_percent, 80, 95)} sparkData={metrics.map(m => m.cpu_percent)} color="#3b82f6" />
        <KpiCard title="Memory Usage" value={latest ? `${latest.memory_percent}%` : '--'} subtitle={latest ? `${latest.memory_used_gb} / ${latest.memory_total_gb} GB` : ''} icon={<MemoryStick className="w-5 h-5 text-primary" />} status={getStatus(latest?.memory_percent, 85, 95)} sparkData={metrics.map(m => m.memory_percent)} color="#f59e0b" />
        <KpiCard title="Disk Usage" value={latest ? `${latest.disk_percent}%` : '--'} subtitle={latest ? `${latest.disk_used_gb} / ${latest.disk_total_gb} GB` : ''} icon={<HardDrive className="w-5 h-5 text-primary" />} status={getStatus(latest?.disk_percent, 85, 95)} sparkData={metrics.map(m => m.disk_percent)} color="#10b981" />
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Chart */}
        <div className="lg:col-span-2 bg-surface p-5 rounded-xl border border-slate-700/50 shadow-xl">
          <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
            <h2 className="text-base font-semibold text-slate-200 flex items-center gap-2">
              <Clock className="w-4 h-4 text-slate-400" />
              Resource Utilization
            </h2>
            {/* Time Range Selector */}
            <div className="flex items-center gap-1 bg-background rounded-lg p-1">
              {TIME_RANGES.map((range) => (
                <button
                  key={range.hours}
                  onClick={() => setSelectedRange(range.hours)}
                  className={`px-3 py-1 text-xs font-medium rounded-md transition-all ${
                    selectedRange === range.hours
                      ? 'bg-primary text-white shadow-md'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/50'
                  }`}
                >
                  {range.label}
                </button>
              ))}
            </div>
          </div>
          <div className="h-64 md:h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="gradCpu" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.25} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="gradMem" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.25} />
                    <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="timestamp" stroke="#475569" tick={{ fontSize: 10 }} tickFormatter={formatTime} />
                <YAxis stroke="#475569" tick={{ fontSize: 10 }} domain={[0, 100]} />
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', fontSize: '11px' }} labelFormatter={formatTime} />
                <Area type="monotone" dataKey="cpu_percent" stroke="#3b82f6" strokeWidth={2} fill="url(#gradCpu)" name="CPU %" />
                <Area type="monotone" dataKey="memory_percent" stroke="#f59e0b" strokeWidth={2} fill="url(#gradMem)" name="Memory %" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Insights */}
        <div className="bg-surface p-5 rounded-xl border border-slate-700/50 shadow-xl flex flex-col max-h-[430px]">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-semibold text-slate-200">Insights</h2>
            <span className="text-[10px] text-slate-500 bg-background px-2 py-0.5 rounded-full">{insights.length} alerts</span>
          </div>
          <div className="flex-1 overflow-y-auto space-y-2.5 pr-1">
            {insights.length === 0 ? (
              <div className="text-slate-500 text-center py-10 text-sm">
                <Activity className="w-8 h-8 mx-auto mb-2 text-slate-600" />
                All systems nominal.
              </div>
            ) : (
              insights.map((insight, idx) => <InsightCard key={idx} insight={insight} />)
            )}
          </div>
        </div>
      </div>

      {/* Disk Chart */}
      <div className="bg-surface p-5 rounded-xl border border-slate-700/50 shadow-xl">
        <h2 className="text-base font-semibold text-slate-200 mb-4">Disk Utilization</h2>
        <div className="h-40 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="timestamp" stroke="#475569" tick={{ fontSize: 10 }} tickFormatter={formatTime} />
              <YAxis stroke="#475569" tick={{ fontSize: 10 }} domain={[0, 100]} />
              <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', fontSize: '11px' }} labelFormatter={formatTime} />
              <Line type="monotone" dataKey="disk_percent" stroke="#10b981" strokeWidth={2} dot={false} name="Disk %" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <footer className="text-center text-[10px] text-slate-600 py-3 border-t border-slate-800">
        InfraMonitor SRE — FastAPI · React · TypeScript · PostgreSQL
      </footer>
    </div>
  );
}

// =========================================================================
// KPI Card
// =========================================================================
interface KpiCardProps { title: string; value: string; subtitle?: string; icon: React.ReactNode; status: string; sparkData: number[]; color: string; }

function KpiCard({ title, value, subtitle, icon, status, sparkData, color }: KpiCardProps) {
  const statusColors: Record<string, string> = { success: 'text-success', warning: 'text-warning', danger: 'text-danger' };
  const statusBorder: Record<string, string> = { success: 'border-success/20', warning: 'border-warning/20', danger: 'border-danger/20' };
  const miniData = sparkData.slice(-15).map((v, i) => ({ v, i }));

  return (
    <div className={`bg-surface p-4 rounded-xl border ${statusBorder[status] || 'border-slate-700/50'} shadow-lg`}>
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <div className="p-1 bg-primary/10 rounded">{icon}</div>
            <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">{title}</p>
          </div>
          <p className={`text-2xl font-bold ${statusColors[status] || 'text-slate-300'}`}>{value}</p>
          {subtitle && <p className="text-[10px] text-slate-500 mt-0.5">{subtitle}</p>}
        </div>
      </div>
      <div className="h-8 mt-2 opacity-40">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={miniData}><Line type="monotone" dataKey="v" stroke={color} strokeWidth={1.5} dot={false} /></LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

// =========================================================================
// Insight Card
// =========================================================================
function InsightCard({ insight }: { insight: Insight }) {
  const cfg: Record<string, { icon: React.ReactNode; border: string; bg: string; badge: string }> = {
    CRITICAL: { icon: <AlertTriangle className="w-3.5 h-3.5 text-danger" />, border: 'border-l-danger', bg: 'bg-danger/5', badge: 'bg-danger/20 text-danger' },
    WARNING: { icon: <AlertTriangle className="w-3.5 h-3.5 text-warning" />, border: 'border-l-warning', bg: 'bg-warning/5', badge: 'bg-warning/20 text-warning' },
    INFO: { icon: <Info className="w-3.5 h-3.5 text-primary" />, border: 'border-l-primary', bg: 'bg-primary/5', badge: 'bg-primary/20 text-primary' },
  };
  const c = cfg[insight.severity] || cfg.INFO;

  return (
    <div className={`${c.bg} p-2.5 rounded-lg border-l-2 ${c.border}`}>
      <div className="flex items-start gap-2">
        <div className="mt-0.5 flex-shrink-0">{c.icon}</div>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-1.5 mb-0.5">
            <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${c.badge}`}>{insight.severity}</span>
            <span className="text-[9px] text-slate-500">{insight.component}</span>
          </div>
          <p className="text-[11px] text-slate-300 leading-relaxed">{insight.message}</p>
          {insight.root_cause && (
            <p className="text-[10px] text-slate-500 mt-1 bg-background/50 p-1 rounded">
              <span className="font-semibold text-slate-400">Cause:</span> {insight.root_cause}
            </p>
          )}
          <span className="text-[8px] text-slate-600 block mt-1">{new Date(insight.timestamp).toLocaleString()}</span>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
