// web_platform/frontend/src/components/LiveRaceDashboard.tsx
'use client';

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { RaceCard } from './RaceCard';

// --- Type Definitions ---
interface Race {
  id: string;
  venue: string;
  race_number: number;
  start_time: string;
  runners: { number: number; name: string; scratched: boolean; odds: any }[];
  source: string;
  qualification_score?: number;
}

interface AnalyzerCriteria {
  max_field_size: number;
  min_favorite_odds: number;
  min_second_favorite_odds: number;
}

interface QualifiedRacesResponse {
  criteria: AnalyzerCriteria;
  races: Race[];
}

// --- Main Component ---
export const LiveRaceDashboard: React.FC = () => {
  const [allRaces, setAllRaces] = useState<Race[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  const [filterConfig, setFilterConfig] = useState({ minScore: 0, maxFieldSize: 999, sortBy: 'score' });

  const fetchQualifiedRaces = useCallback(async (isInitialLoad = false) => {
    if (isInitialLoad) setLoading(true);
    setError(null);
    try {
      const apiKey = process.env.NEXT_PUBLIC_API_KEY;
      if (!apiKey) throw new Error('API key not configured.');

      // We fetch all qualified races and filter on the client-side for a faster UX
      const response = await fetch(`/api/races/qualified/trifecta`, {
        headers: { 'X-API-Key': apiKey },
      });

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
    const interval = setInterval(() => fetchQualifiedRaces(false), 30000);
    return () => clearInterval(interval);
  }, [fetchQualifiedRaces]);

  const handleFilterChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFilterConfig(prev => ({ ...prev, [name]: name === 'sortBy' ? value : Number(value) }));
  };

  const filteredAndSortedRaces = useMemo(() => {
    let processedRaces = [...allRaces];

    // Apply filters
    processedRaces = processedRaces.filter(race => {
      const score = race.qualification_score || 0;
      const fieldSize = race.runners.filter(r => !r.scratched).length;
      return score >= filterConfig.minScore && fieldSize <= filterConfig.maxFieldSize;
    });

    // Apply sorting
    processedRaces.sort((a, b) => {
      switch (filterConfig.sortBy) {
        case 'time':
          return new Date(a.start_time).getTime() - new Date(b.start_time).getTime();
        case 'venue':
          return a.venue.localeCompare(b.venue);
        case 'score':
        default:
          return (b.qualification_score || 0) - (a.qualification_score || 0);
      }
    });

    return processedRaces;
  }, [allRaces, filterConfig]);

  return (
    <main className="min-h-screen bg-gray-900 text-white p-8">
      <h1 className="text-4xl font-bold text-center mb-2">Fortuna Faucet Command Deck</h1>
      <p className="text-center text-gray-400 mb-8">
        {lastUpdate ? `Last updated: ${lastUpdate.toLocaleTimeString()}` : '...'}
      </p>

      {/* --- Smart Filtering & Sorting System --- */}
      <div className="filter-panel bg-gray-800/90 backdrop-blur-sm p-4 rounded-xl border border-gray-700 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <span className="font-semibold">Smart Filters</span>
          </div>
          <div className="flex gap-6">
            <div className="flex items-center gap-3">
              <label className="text-sm text-gray-400">Min Score:</label>
              <input type="range" name="minScore" min="0" max="100" value={filterConfig.minScore} onChange={handleFilterChange} className="w-32" />
              <span className="text-sm font-semibold w-12">{filterConfig.minScore}%</span>
            </div>
            <div className="flex items-center gap-3">
              <label className="text-sm text-gray-400">Max Field:</label>
              <select name="maxFieldSize" value={filterConfig.maxFieldSize} onChange={handleFilterChange} className="bg-gray-700 border border-gray-600 rounded px-3 py-1 text-white">
                <option value="8">8 runners</option>
                <option value="10">10 runners</option>
                <option value="12">12 runners</option>
                <option value="999">Any size</option>
              </select>
            </div>
            <div className="flex items-center gap-3">
              <label className="text-sm text-gray-400">Sort by:</label>
              <select name="sortBy" value={filterConfig.sortBy} onChange={handleFilterChange} className="bg-gray-700 border border-gray-600 rounded px-3 py-1 text-white">
                <option value="score">Qualification Score</option>
                <option value="time">Post Time</option>
                <option value="venue">Track Name</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {loading && <p className="text-center text-xl">Searching for qualified races...</p>}
      {error && <p className="text-center text-xl text-red-500">Error: {error}</p>}

      {!loading && !error && (
        <>
          <div className='text-center mb-4 text-gray-400'>
            Displaying <span className='font-bold text-white'>{filteredAndSortedRaces.length}</span> of <span className='font-bold text-white'>{allRaces.length}</span> total qualified races.
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredAndSortedRaces.map(race => (
              <RaceCard key={race.id} race={race} />
            ))}
          </div>
        </>
      )}
    </main>
  );
};