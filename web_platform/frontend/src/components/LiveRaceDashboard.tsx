// web_platform/frontend/src/components/LiveRaceDashboard.tsx
'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { RaceCard } from './RaceCard';

// --- Type Definitions ---
interface OddsData {
  win: number | null;
  source: string;
  last_updated: string;
}

interface Runner {
  number: number;
  name: string;
  scratched: boolean;
  selection_id?: number;
  odds: Record<string, OddsData>;
}

interface Race {
  id: string;
  venue: string;
  race_number: number;
  start_time: string;
  runners: Runner[];
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
  const [races, setRaces] = useState<Race[]>([]);
  const [criteria, setCriteria] = useState<AnalyzerCriteria | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  const [params, setParams] = useState(() => {
    if (typeof window === 'undefined') {
      return { max_field_size: 10, min_favorite_odds: 2.5, min_second_favorite_odds: 4.0 };
    }
    try {
      const savedParams = localStorage.getItem('analyzerParams');
      return savedParams ? JSON.parse(savedParams) : { max_field_size: 10, min_favorite_odds: 2.5, min_second_favorite_odds: 4.0 };
    } catch (error) {
      return { max_field_size: 10, min_favorite_odds: 2.5, min_second_favorite_odds: 4.0 };
    }
  });

  useEffect(() => {
    localStorage.setItem('analyzerParams', JSON.stringify(params));
  }, [params]);

  const fetchQualifiedRaces = useCallback(async (isInitialLoad = false) => {
    if (isInitialLoad) setLoading(true);
    setError(null);
    try {
      const apiKey = process.env.NEXT_PUBLIC_API_KEY;
      if (!apiKey) throw new Error('API key not configured.');

      const query = new URLSearchParams({
        max_field_size: params.max_field_size.toString(),
        min_favorite_odds: params.min_favorite_odds.toString(),
        min_second_favorite_odds: params.min_second_favorite_odds.toString(),
      }).toString();

      const response = await fetch(`/api/races/qualified/trifecta?${query}`, {
        headers: { 'X-API-Key': apiKey },
      });

      if (!response.ok) {
        throw new Error(`API request failed with status ${response.status}`);
      }

      const data: QualifiedRacesResponse = await response.json();
      setRaces(data.races || []);
      setCriteria(data.criteria);
      setLastUpdate(new Date());
    } catch (e) {
      setError(e instanceof Error ? e.message : 'An unknown error occurred');
    } finally {
      if (isInitialLoad) setLoading(false);
    }
  }, [params]);

  useEffect(() => {
    fetchQualifiedRaces(true); // Initial fetch with loading spinner
    const interval = setInterval(() => fetchQualifiedRaces(false), 30000); // Poll every 30 seconds
    return () => clearInterval(interval); // Cleanup on unmount
  }, [fetchQualifiedRaces]);

  const handleParamChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setParams(prev => ({ ...prev, [name]: parseFloat(value) }));
  };

  return (
    <main className="min-h-screen bg-gray-900 text-white p-8">
      <h1 className="text-4xl font-bold text-center mb-2">Fortuna Faucet Command Deck</h1>
      <p className="text-center text-gray-400 mb-8">
        {lastUpdate ? `Last updated: ${lastUpdate.toLocaleTimeString()}` : '...'}
      </p>

      <div className="mb-8 p-6 bg-gray-800/50 border border-gray-700 rounded-lg">
        <h2 className="text-2xl font-semibold mb-4 text-purple-400">Trifecta Analyzer Playground</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <label htmlFor="max_field_size" className="block text-sm font-medium text-gray-300">Max Field Size: <span className='font-bold text-white'>{params.max_field_size}</span></label>
            <input type="range" id="max_field_size" name="max_field_size" min="5" max="15" step="1" value={params.max_field_size} onChange={handleParamChange} className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer" />
          </div>
          <div>
            <label htmlFor="min_favorite_odds" className="block text-sm font-medium text-gray-300">Min Favorite Odds: <span className='font-bold text-white'>{params.min_favorite_odds.toFixed(1)}</span></label>
            <input type="range" id="min_favorite_odds" name="min_favorite_odds" min="1.5" max="5.0" step="0.1" value={params.min_favorite_odds} onChange={handleParamChange} className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer" />
          </div>
          <div>
            <label htmlFor="min_second_favorite_odds" className="block text-sm font-medium text-gray-300">Min 2nd Fav Odds: <span className='font-bold text-white'>{params.min_second_favorite_odds.toFixed(1)}</span></label>
            <input type="range" id="min_second_favorite_odds" name="min_second_favorite_odds" min="2.0" max="8.0" step="0.1" value={params.min_second_favorite_odds} onChange={handleParamChange} className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer" />
          </div>
        </div>
      </div>

      {loading && <p className="text-center text-xl">Searching for qualified races...</p>}
      {error && <p className="text-center text-xl text-red-500">Error: {error}</p>}

      {!loading && !error && (
        <>
          <div className='text-center mb-4 text-gray-400'>
            Found <span className='font-bold text-white'>{races.length}</span> qualified races with the current criteria.
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {races.map(race => (
              <RaceCard key={race.id} race={race} />
            ))}
          </div>
        </>
      )}
    </main>
  );
};