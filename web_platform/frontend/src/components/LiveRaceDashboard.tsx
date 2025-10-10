// web_platform/frontend/src/components/LiveRaceDashboard.tsx
'use client';

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { RaceCard } from './RaceCard';

// --- Type Definitions ---
import type { Race } from '@/types/racing'; // Correct type import

interface QualifiedRacesResponse {
  races: Race[];
}

// --- Helper Functions from UI Bible ---
const getNextRaceCountdown = (races: Race[]): string => {
  const now = new Date().getTime();
  const upcomingRaces = races
    .map(race => new Date(race.start_time).getTime())
    .filter(time => time > now);

  if (upcomingRaces.length === 0) return '--:--';

  const nextRaceTime = Math.min(...upcomingRaces);
  const diff = nextRaceTime - now;
  const minutes = Math.floor((diff / 1000) / 60);
  const seconds = Math.floor((diff / 1000) % 60);

  return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
};

const getAverageFieldSize = (races: Race[]): string => {
  if (races.length === 0) return '0';
  const totalRunners = races.reduce((sum, race) => sum + race.runners.filter(r => !r.scratched).length, 0);
  return (totalRunners / races.length).toFixed(1);
};

// --- Main Component ---
export const LiveRaceDashboard: React.FC = () => {
  const [allRaces, setAllRaces] = useState<Race[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [countdown, setCountdown] = useState('--:--');

  const [filterConfig, setFilterConfig] = useState({ minScore: 0, maxFieldSize: 999, sortBy: 'score' });

  const fetchQualifiedRaces = useCallback(async (isInitialLoad = false) => {
    if (isInitialLoad) setLoading(true);
    setError(null);
    try {
      const apiKey = process.env.NEXT_PUBLIC_API_KEY;
      if (!apiKey) throw new Error('API key not configured.');
      const response = await fetch(`/api/races/qualified/trifecta`, { headers: { 'X-API-Key': apiKey } });
      if (!response.ok) throw new Error(`API request failed with status ${response.status}`);
      const data: QualifiedRacesResponse = await response.json();
      setAllRaces(data.races || []);
      setLastUpdate(new Date());
    } catch (e) {
      setError(e instanceof Error ? e.message : 'An unknown error occurred');
    } finally {
      if (isInitialLoad) setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchQualifiedRaces(true);
    const dataInterval = setInterval(() => fetchQualifiedRaces(false), 30000);
    const countdownInterval = setInterval(() => {
      setCountdown(getNextRaceCountdown(allRaces));
    }, 1000);
    return () => {
      clearInterval(dataInterval);
      clearInterval(countdownInterval);
    };
  }, [fetchQualifiedRaces, allRaces]);

  const handleFilterChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFilterConfig(prev => ({ ...prev, [name]: name === 'sortBy' ? value : Number(value) }));
  };

  const filteredAndSortedRaces = useMemo(() => {
    let processedRaces = [...allRaces];
    processedRaces = processedRaces.filter(race => (race.qualification_score || 0) >= filterConfig.minScore && race.runners.filter(r => !r.scratched).length <= filterConfig.maxFieldSize);
    processedRaces.sort((a, b) => {
      switch (filterConfig.sortBy) {
        case 'time': return new Date(a.start_time).getTime() - new Date(b.start_time).getTime();
        case 'venue': return a.venue.localeCompare(b.venue);
        default: return (b.qualification_score || 0) - (a.qualification_score || 0);
      }
    });
    return processedRaces;
  }, [allRaces, filterConfig]);

  return (
    <main className="min-h-screen bg-gray-900 text-white p-8">
      <h1 className="text-4xl font-bold text-center mb-2">Fortuna Faucet Command Deck</h1>
      <p className="text-center text-gray-400 mb-8">{lastUpdate ? `Last updated: ${lastUpdate.toLocaleTimeString()}` : '...'}</p>

      {/* --- Dashboard Statistics Panel --- */}
      <div className="stats-grid grid grid-cols-4 gap-4 mb-6">
        <div className="stat-card bg-gradient-to-br from-purple-500/10 to-purple-600/10 border border-purple-500/20 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2"><span className='text-purple-400'>📊</span><span className="text-2xl font-bold text-white">{filteredAndSortedRaces.length}</span></div>
          <div className="text-sm text-gray-400">Qualified Races</div>
        </div>
        <div className="stat-card bg-gradient-to-br from-emerald-500/10 to-emerald-600/10 border border-emerald-500/20 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2"><span className='text-emerald-400'>🏆</span><span className="text-2xl font-bold text-white">{filteredAndSortedRaces.filter(r => r.qualification_score && r.qualification_score >= 80).length}</span></div>
          <div className="text-sm text-gray-400">Premium Targets</div>
        </div>
        <div className="stat-card bg-gradient-to-br from-blue-500/10 to-blue-600/10 border border-blue-500/20 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2"><span className='text-blue-400'>⏱️</span><span className="text-2xl font-bold text-white">{countdown}</span></div>
          <div className="text-sm text-gray-400">Next Race</div>
        </div>
        <div className="stat-card bg-gradient-to-br from-yellow-500/10 to-yellow-600/10 border border-yellow-500/20 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2"><span className='text-yellow-400'>🎯</span><span className="text-2xl font-bold text-white">{getAverageFieldSize(filteredAndSortedRaces)}</span></div>
          <div className="text-sm text-gray-400">Avg Field Size</div>
        </div>
      </div>

      {/* --- Smart Filtering & Sorting System --- */}
      <div className="filter-panel bg-gray-800/90 backdrop-blur-sm p-4 rounded-xl border border-gray-700 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4"><span className="font-semibold">Smart Filters</span></div>
          <div className="flex gap-6">
            <div className="flex items-center gap-3"><label className="text-sm text-gray-400">Min Score:</label><input type="range" name="minScore" min="0" max="100" value={filterConfig.minScore} onChange={handleFilterChange} className="w-32" /><span className="text-sm font-semibold w-12">{filterConfig.minScore}%</span></div>
            <div className="flex items-center gap-3"><label className="text-sm text-gray-400">Max Field:</label><select name="maxFieldSize" value={filterConfig.maxFieldSize} onChange={handleFilterChange} className="bg-gray-700 border border-gray-600 rounded px-3 py-1 text-white"><option value="8">8 runners</option><option value="10">10 runners</option><option value="12">12 runners</option><option value="999">Any size</option></select></div>
            <div className="flex items-center gap-3"><label className="text-sm text-gray-400">Sort by:</label><select name="sortBy" value={filterConfig.sortBy} onChange={handleFilterChange} className="bg-gray-700 border border-gray-600 rounded px-3 py-1 text-white"><option value="score">Qualification Score</option><option value="time">Post Time</option><option value="venue">Track Name</option></select></div>
          </div>
        </div>
      </div>

      {loading && <p className="text-center text-xl">Searching for qualified races...</p>}
      {error && <p className="text-center text-xl text-red-500">Error: {error}</p>}

      {!loading && !error && (
        <>
          <div className='text-center mb-4 text-gray-400'>Displaying <span className='font-bold text-white'>{filteredAndSortedRaces.length}</span> of <span className='font-bold text-white'>{allRaces.length}</span> total qualified races.</div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredAndSortedRaces.map(race => <RaceCard key={race.id} race={race} />)}
          </div>
        </>
      )}
    </main>
  );
};