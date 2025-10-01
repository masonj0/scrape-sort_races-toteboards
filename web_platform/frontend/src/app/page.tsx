'use client';

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  Play, Pause, RefreshCw, TrendingUp, TrendingDown,
  Clock, AlertCircle, Target, Zap, Activity, CheckCircle2,
  Wifi, WifiOff, Terminal as TerminalIcon, X
} from 'lucide-react';

// Types
interface Odds { betfair: number; pointsbet: number; tvg: number; best: number; best_source: string; spread: number; }
interface Horse { number: number; name: string; odds: Odds; value_score: number; trend: 'up' | 'down' | 'stable'; }
interface Race { id: string; track: string; race_number: number; post_time: string; minutes_to_post: number; horses: Horse[]; status: 'upcoming' | 'imminent' | 'post'; }
interface LogEntry { timestamp: Date; level: 'info' | 'success' | 'error' | 'warning'; message: string; }

// Configuration
const CONFIG = {
  API_BASE: typeof window !== 'undefined' && window.location.hostname === 'localhost' ? 'http://localhost:8000' : '/api',
  REFRESH_INTERVALS: { IMMINENT: 10, UPCOMING: 30, DISTANT: 60 },
  VALUE_THRESHOLDS: { EXCELLENT: 5.0, GOOD: 3.0, FAIR: 1.5 }
};

const CheckmateUltimate: React.FC = () => {
  const [races, setRaces] = useState<Race[]>([]);
  const [isLive, setIsLive] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [minValueScore, setMinValueScore] = useState(2.0);
  const [autoRefresh, setAutoRefresh] = useState(30);
  const [isConnected, setIsConnected] = useState(false);
  const [isFetching, setIsFetching] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showTerminal, setShowTerminal] = useState(false);
  const [logs, setLogs] = useState<LogEntry[]>([]);

  const addLog = useCallback((level: LogEntry['level'], message: string) => {
    setLogs(prev => [...prev.slice(-99), { timestamp: new Date(), level, message }]);
  }, []);

  const filteredRaces = useMemo(() => races.map(race => ({ ...race, horses: race.horses.filter(h => h.value_score >= minValueScore) })).filter(race => race.horses.length > 0), [races, minValueScore]);

  const refreshData = useCallback(async () => {
    setIsFetching(true); setError(null);
    addLog('info', `Fetching from ${CONFIG.API_BASE}/api/races/live`);
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000);
      const response = await fetch(`${CONFIG.API_BASE}/api/races/live`, { signal: controller.signal });
      clearTimeout(timeoutId);
      if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      const data = await response.json();
      if (!Array.isArray(data)) throw new Error('Invalid response format');
      const processedRaces = data.map((race: any) => ({ ...race, minutes_to_post: Math.floor((new Date(race.post_time).getTime() - Date.now()) / 60000), status: race.minutes_to_post < 5 ? 'imminent' : 'upcoming' }));
      setRaces(processedRaces); setLastUpdate(new Date()); setIsConnected(true);
      addLog('success', `Fetched ${processedRaces.length} races.`);
    } catch (err: any) {
      setIsConnected(false);
      const errorMessage = err.name === 'AbortError' ? 'Request timeout' : 'Network error: Unable to reach backend';
      setError(errorMessage); addLog('error', `Fetch failed: ${errorMessage}`);
    } finally {
      setIsFetching(false);
    }
  }, [addLog]);

  useEffect(() => {
    if (isLive && autoRefresh > 0) {
      refreshData();
      const interval = setInterval(refreshData, autoRefresh * 1000);
      addLog('info', `Live mode enabled with ${autoRefresh}s refresh.`);
      return () => { clearInterval(interval); addLog('warning', 'Live mode disabled.'); };
    }
  }, [isLive, autoRefresh, refreshData, addLog]);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch(`${CONFIG.API_BASE}/api/health`);
        if (response.ok) { setIsConnected(true); setError(null); } else { setIsConnected(false); setError('Backend is reachable but not healthy.'); }
      } catch (err) { setIsConnected(false); setError('Backend is unreachable. Please ensure the Python service is running.'); }
    };
    checkHealth();
  }, []);

  const getValueColor = (score: number): string => {
    if (score >= CONFIG.VALUE_THRESHOLDS.EXCELLENT) return 'bg-green-500';
    if (score >= CONFIG.VALUE_THRESHOLDS.GOOD) return 'bg-yellow-500';
    return 'bg-gray-500';
  };

  const getOddsColor = (odds: number, best: number): string => {
    return Math.abs(odds - best) < 0.01 ? 'text-green-400 font-bold' : 'text-gray-400';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white p-4">
      <div className="max-w-7xl mx-auto mb-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent flex items-center gap-3"><Target className="w-10 h-10 text-blue-400" />Checkmate Ultimate Solo</h1>
          <div className="flex items-center gap-3">
            <div className={`flex items-center gap-2 bg-slate-800 px-4 py-2 rounded-lg border border-slate-700 text-sm ${isConnected ? 'text-green-400' : 'text-red-400'}`}>{isConnected ? <Wifi className="w-4 h-4" /> : <WifiOff className="w-4 h-4" />}{isConnected ? 'Connected' : 'Disconnected'}</div>
            <button onClick={refreshData} disabled={isFetching} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg flex items-center gap-2 transition-all disabled:opacity-50"><RefreshCw className={`w-4 h-4 ${isFetching ? 'animate-spin' : ''}`} />{isFetching ? 'Fetching...' : 'Refresh'}</button>
            <button onClick={() => setIsLive(!isLive)} className={`px-6 py-2 rounded-lg flex items-center gap-2 transition-all ${isLive ? 'bg-red-600' : 'bg-green-600'}`}>{isLive ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}{isLive ? 'Stop Live' : 'Start Live'}</button>
          </div>
        </div>
        {/* Error Banner */}
        {error && <div className="bg-red-900/50 border border-red-700 rounded-lg p-4 mb-6 flex items-center gap-3"><AlertCircle className="w-5 h-5 text-red-400" /><p className="text-red-300 text-sm">{error}</p></div>}
      </div>
      {/* Race Cards */}
      <div className="max-w-7xl mx-auto space-y-6">
        {races.length > 0 ? filteredRaces.map(race => (
          <div key={race.id} className="bg-slate-800 rounded-lg overflow-hidden border border-slate-700">
            <div className="bg-gradient-to-r from-slate-800 to-slate-700 px-6 py-4 border-b border-slate-600 flex items-center justify-between">
              <div><h3 className="text-xl font-bold text-white">{race.track}</h3><p className="text-gray-400">Race {race.race_number}</p></div>
              <div className="text-right"><p className="text-sm text-gray-400">Post Time</p><p className="text-white font-semibold">{new Date(race.post_time).toLocaleTimeString()}</p></div>
            </div>
            <table className="w-full"><thead><tr className="bg-slate-700 text-left text-sm text-gray-300"><th className="px-6 py-3">Horse</th><th className="px-6 py-3 text-center">Value</th><th className="px-6 py-3 text-center">Best Odds</th><th className="px-6 py-3 text-center">Betfair</th><th className="px-6 py-3 text-center">PointsBet</th><th className="px-6 py-3 text-center">TVG</th><th className="px-6 py-3 text-center">Trend</th></tr></thead>
              <tbody>{race.horses.map(horse => (
                <tr key={horse.number} className="border-t border-slate-700 hover:bg-slate-700/50">
                  <td className="px-6 py-4"><div className="font-semibold text-white">{horse.name}</div></td>
                  <td className="px-6 py-4 text-center"><span className={`px-3 py-1 rounded-full text-white font-semibold ${getValueColor(horse.value_score)}`}>{horse.value_score.toFixed(1)}%</span></td>
                  <td className="px-6 py-4 text-center"><div className="inline-flex flex-col"><span className="font-bold text-green-400 text-lg">{horse.odds.best.toFixed(2)}</span><span className="text-xs text-gray-500">{horse.odds.best_source}</span></div></td>
                  <td className={`px-6 py-4 text-center ${getOddsColor(horse.odds.betfair, horse.odds.best)}`}>{horse.odds.betfair.toFixed(2)}</td>
                  <td className={`px-6 py-4 text-center ${getOddsColor(horse.odds.pointsbet, horse.odds.best)}`}>{horse.odds.pointsbet.toFixed(2)}</td>
                  <td className={`px-6 py-4 text-center ${getOddsColor(horse.odds.tvg, horse.odds.best)}`}>{horse.odds.tvg.toFixed(2)}</td>
                  <td className="px-6 py-4 text-center">{horse.trend === 'up' ? <TrendingUp className="w-5 h-5 text-green-400 mx-auto" /> : <TrendingDown className="w-5 h-5 text-red-400 mx-auto" />}</td>
                </tr>
              ))}</tbody>
            </table>
          </div>
        )) : <div className="bg-slate-800 rounded-lg p-12 text-center border border-slate-700"><AlertCircle className="w-16 h-16 mx-auto mb-4 text-gray-600" /><p className="text-gray-400 text-lg">Awaiting data...</p></div>}
      </div>
    </div>
  );
};

export default CheckmateUltimate;