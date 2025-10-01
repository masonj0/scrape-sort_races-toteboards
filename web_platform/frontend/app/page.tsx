'use client';

// ==============================================================================
// == Checkmate Solo - The Sanctioned and Final User Interface
// ==============================================================================
// This component replaces the entire previous web interface. It is the new North Star.
// ==============================================================================

import React, { useState, useEffect } from 'react';
import { Play, Pause, RefreshCw, TrendingUp, TrendingDown, DollarSign, Clock, AlertCircle } from 'lucide-react';

// Mock data generator - to be replaced with actual fetch
const generateMockRace = (id) => {
  const tracks = ['Belmont Park', 'Churchill Downs', 'Santa Anita', 'Keeneland', 'Del Mar'];
  const horses = ['Thunder Strike', 'Lightning Bolt', 'Swift Arrow', 'Golden Dream', 'Storm Chaser', 'Midnight Runner', 'Royal Flash', 'Desert Wind'];
  return {
    id, track: tracks[Math.floor(Math.random() * tracks.length)], race_number: Math.floor(Math.random() * 10) + 1,
    post_time: new Date(Date.now() + Math.random() * 3600000).toISOString(),
    horses: Array.from({ length: 8 }, (_, i) => {
      const betfair = 2 + Math.random() * 15; const pointsbet = betfair * (0.9 + Math.random() * 0.2); const tvg = betfair * (0.85 + Math.random() * 0.3);
      const best = Math.min(betfair, pointsbet, tvg); const avg = (betfair + pointsbet + tvg) / 3; const value = ((avg - best) / best) * 100;
      return { number: i + 1, name: horses[Math.floor(Math.random() * horses.length)], odds: { betfair: betfair.toFixed(2), pointsbet: pointsbet.toFixed(2), tvg: tvg.toFixed(2), best: best.toFixed(2), best_source: betfair === best ? 'Betfair' : pointsbet === best ? 'PointsBet' : 'TVG' }, value_score: value.toFixed(1), trend: Math.random() > 0.5 ? 'up' : 'down' };
    }).sort((a, b) => parseFloat(b.value_score) - parseFloat(a.value_score))
  };
};

const CheckmateSolo = () => {
  const [races, setRaces] = useState([]);
  const [isLive, setIsLive] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [minValueScore, setMinValueScore] = useState(2.0);
  const [autoRefresh, setAutoRefresh] = useState(30);

  const fetchRaces = async () => {
    // TODO: Replace with fetch('http://localhost:8000/api/races/live');
    const mockRaces = Array.from({ length: 5 }, (_, i) => generateMockRace(i));
    setRaces(mockRaces);
    setLastUpdate(new Date());
  };

  useEffect(() => {
    if (isLive && autoRefresh > 0) {
      fetchRaces();
      const interval = setInterval(fetchRaces, autoRefresh * 1000);
      return () => clearInterval(interval);
    }
  }, [isLive, autoRefresh]);

  const getValueColor = (score) => {
    const val = parseFloat(score);
    if (val >= 5) return 'bg-green-500'; if (val >= 3) return 'bg-yellow-500'; return 'bg-gray-400';
  };

  const getOddsColor = (odds, best) => {
    if (parseFloat(odds) === parseFloat(best)) return 'text-green-600 font-bold'; return 'text-gray-700';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white p-6">
      <div className="max-w-7xl mx-auto mb-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">Checkmate Solo</h1>
            <p className="text-gray-400 mt-1">Live odds aggregation & value detection</p>
          </div>
          <div className="flex items-center gap-4">
            {lastUpdate && <div className="text-sm text-gray-400 flex items-center gap-2"><Clock className="w-4 h-4" />Updated {lastUpdate.toLocaleTimeString()}</div>}
            <button onClick={() => fetchRaces()} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg flex items-center gap-2 transition-colors"><RefreshCw className="w-4 h-4" />Refresh Now</button>
            <button onClick={() => setIsLive(!isLive)} className={`px-6 py-2 rounded-lg flex items-center gap-2 transition-colors ${isLive ? 'bg-red-600 hover:bg-red-700' : 'bg-green-600 hover:bg-green-700'}`}>\n              {isLive ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}{isLive ? 'Stop Live' : 'Start Live'}\n            </button>
          </div>
        </div>
        <div className="bg-slate-800 rounded-lg p-4 flex items-center gap-6">
          <div className="flex items-center gap-3"><label className="text-sm text-gray-400">Min Value Score:</label><input type="number" step="0.5" value={minValueScore} onChange={(e) => setMinValueScore(parseFloat(e.target.value))} className="bg-slate-700 px-3 py-1 rounded w-20 text-white" /></div>
          <div className="flex items-center gap-3"><label className="text-sm text-gray-400">Auto-refresh (seconds):</label><select value={autoRefresh} onChange={(e) => setAutoRefresh(parseInt(e.target.value))} className="bg-slate-700 px-3 py-1 rounded text-white"><option value={10}>10s</option><option value={30}>30s</option><option value={60}>60s</option><option value={0}>Off</option></select></div>
        </div>
      </div>
      <div className="max-w-7xl mx-auto space-y-6">
        {races.length === 0 ? (
          <div className="bg-slate-800 rounded-lg p-12 text-center"><AlertCircle className="w-16 h-16 mx-auto mb-4 text-gray-600" /><p className="text-gray-400 text-lg">No races loaded. Click 'Start Live' to begin.</p></div>
        ) : (
          races.map((race) => {
            const topHorses = race.horses.filter(h => parseFloat(h.value_score) >= minValueScore);
            if (topHorses.length === 0) return null;
            return (
              <div key={race.id} className="bg-slate-800 rounded-lg overflow-hidden border border-slate-700">
                <div className="bg-gradient-to-r from-slate-700 to-slate-800 px-6 py-4 border-b border-slate-600">
                  <div className="flex items-center justify-between"><div><h3 className="text-xl font-bold text-white">{race.track}</h3><p className="text-gray-400">Race {race.race_number}</p></div><div className="text-right"><p className="text-sm text-gray-400">Post Time</p><p className="text-white font-semibold">{new Date(race.post_time).toLocaleTimeString()}</p></div></div>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full"><thead><tr className="bg-slate-700 text-left text-sm text-gray-400"><th className="px-6 py-3 w-12">#</th><th className="px-6 py-3">Horse</th><th className="px-6 py-3 text-center">Betfair</th><th className="px-6 py-3 text-center">PointsBet</th><th className="px-6 py-3 text-center">TVG</th><th className="px-6 py-3 text-center">Best Odds</th><th className="px-6 py-3 text-center">Value Score</th></tr></thead>
                    <tbody>{topHorses.map((horse, idx) => (<tr key={horse.number} className={`border-t border-slate-700 hover:bg-slate-700/50 ${idx === 0 ? 'bg-slate-700/30' : ''}`}><td className="px-6 py-4 font-bold text-gray-400">{horse.number}</td><td className="px-6 py-4"><span className="font-semibold text-white">{horse.name}</span></td><td className={`px-6 py-4 text-center ${getOddsColor(horse.odds.betfair, horse.odds.best)}`}>{horse.odds.betfair}</td><td className={`px-6 py-4 text-center ${getOddsColor(horse.odds.pointsbet, horse.odds.best)}`}>{horse.odds.pointsbet}</td><td className={`px-6 py-4 text-center ${getOddsColor(horse.odds.tvg, horse.odds.best)}`}>{horse.odds.tvg}</td><td className="px-6 py-4 text-center"><div className="inline-flex flex-col items-center"><span className="font-bold text-green-400 text-lg">{horse.odds.best}</span><span className="text-xs text-gray-500">{horse.odds.best_source}</span></div></td><td className="px-6 py-4 text-center"><span className={`inline-block px-3 py-1 rounded-full text-white font-semibold ${getValueColor(horse.value_score)}`}>{horse.value_score}%</span></td></tr>))}</tbody>
                  </table>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default CheckmateSolo;