// web_platform/frontend/src/components/LiveRaceDashboard.tsx
'use client';

import React, { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
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

const fetchAdapterStatuses = async (): Promise<AdapterStatus[]> => {
  const apiKey = process.env.NEXT_PUBLIC_API_KEY;
  if (!apiKey) throw new Error('API key not configured.');
  const response = await fetch(`/api/adapters/status`, { headers: { 'X-API-Key': apiKey } });
  if (!response.ok) throw new Error(`Adapter status API request failed: ${response.statusText}`);
  return response.json();
};

// --- Main Component ---
export const LiveRaceDashboard: React.FC = () => {
  const [filterConfig, setFilterConfig] = useState({ minScore: 0, maxFieldSize: 999, sortBy: 'score' });

  // --- TanStack Query Hooks ---
  const { data: qualifiedData, error: racesError, isLoading: racesLoading } = useQuery<QualifiedRacesResponse>({
    queryKey: ['qualifiedRaces'],
    queryFn: fetchQualifiedRaces,
    refetchInterval: 30000 // The Heartbeat
  });

  const { data: statuses, error: statusError } = useQuery<AdapterStatus[]>({
    queryKey: ['adapterStatuses'],
    queryFn: fetchAdapterStatuses,
    refetchInterval: 60000
  });

  const handleFilterChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFilterConfig(prev => ({ ...prev, [name]: name === 'sortBy' ? value : Number(value) }));
  };

  const filteredAndSortedRaces = useMemo(() => {
    let processedRaces = [...(qualifiedData?.races || [])];
    processedRaces = processedRaces.filter(race => (race.qualification_score || 0) >= filterConfig.minScore && race.runners.filter(r => !r.scratched).length <= filterConfig.maxFieldSize);
    processedRaces.sort((a, b) => {
      switch (filterConfig.sortBy) {
        case 'time': return new Date(a.start_time).getTime() - new Date(b.start_time).getTime();
        case 'venue': return a.venue.localeCompare(b.venue);
        default: return (b.qualification_score || 0) - (a.qualification_score || 0);
      }
    });
    return processedRaces;
  }, [qualifiedData, filterConfig]);

  const error = racesError || statusError;

  return (
    <main className="min-h-screen bg-gray-900 text-white p-8">
      <h1 className="text-4xl font-bold text-center mb-8">Fortuna Faucet Command Deck</h1>

      {/* --- Visual Health Panel --- */}
      <div className='mb-8 p-4 bg-gray-800/50 border border-gray-700 rounded-lg'>
        <h2 className='text-lg font-semibold text-gray-300 mb-3'>Adapter Status</h2>
        <div className='flex flex-wrap gap-2'>
          {statuses?.map(s => (
            <span key={s.adapter_name} className={`px-2 py-1 text-xs font-bold rounded-full ${s.status === 'SUCCESS' || s.status === 'OK' ? 'bg-green-500/20 text-green-300' : 'bg-red-500/20 text-red-300'}`}>\n              {s.adapter_name}\n            </span>
          )) ?? <span className='text-gray-500 text-sm'>Loading statuses...</span>}
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

      {racesLoading && <p className="text-center text-xl">Searching for qualified races...</p>}
      {error && <p className="text-center text-xl text-red-500">Error: {error.message}</p>}

      {!racesLoading && !error && (
        <>
          <div className='text-center mb-4 text-gray-400'>Displaying <span className='font-bold text-white'>{filteredAndSortedRaces.length}</span> of <span className='font-bold text-white'>{qualifiedData?.races.length || 0}</span> total qualified races.</div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredAndSortedRaces.map(race => <RaceCard key={race.id} race={race} />)}
          </div>
        </>
      )}
    </main>
  );
};