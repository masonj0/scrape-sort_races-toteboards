// web_platform/frontend/src/components/LiveRaceDashboard.tsx
'use client';

import React, { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { RaceCard } from './RaceCard';

// --- Type Definitions ---
interface Race { id: string; venue: string; race_number: number; start_time: string; runners: any[]; source: string; qualification_score?: number; }
interface AnalyzerCriteria { max_field_size: number; min_favorite_odds: number; min_second_favorite_odds: number; }
interface QualifiedRacesResponse { criteria: AnalyzerCriteria; races: Race[]; }
interface AdapterStatus { adapter_name: string; status: string; }

// --- API Fetching Functions ---
const fetchQualifiedRaces = async (params: any): Promise<QualifiedRacesResponse> => {
  const apiKey = process.env.NEXT_PUBLIC_API_KEY;
  if (!apiKey) throw new Error('API key not configured.');
  const query = new URLSearchParams(params).toString();
  const response = await fetch(`/api/races/qualified/trifecta?${query}`, { headers: { 'X-API-Key': apiKey } });
  if (!response.ok) throw new Error(`API request failed with status ${response.status}`);
  return response.json();
};

const fetchAdapterStatuses = async (): Promise<AdapterStatus[]> => {
  const apiKey = process.env.NEXT_PUBLIC_API_KEY;
  if (!apiKey) throw new Error('API key not configured.');
  const response = await fetch(`/api/adapters/status`, { headers: { 'X-API-Key': apiKey } });
  if (!response.ok) throw new Error(`API request failed with status ${response.status}`);
  return response.json();
};

// --- Main Component ---
export const LiveRaceDashboard: React.FC = () => {
  const [params, setParams] = useState({ max_field_size: 10, min_favorite_odds: 2.5, min_second_favorite_odds: 4.0 });
  const [filterConfig, setFilterConfig] = useState({ minScore: 0, maxFieldSize: 999, sortBy: 'score' });

  // --- TanStack Query Hooks ---
  const { data: qualifiedData, error: racesError, isLoading: racesLoading } = useQuery<QualifiedRacesResponse>({
    queryKey: ['qualifiedRaces', params],
    queryFn: () => fetchQualifiedRaces(params),
    refetchInterval: 30000 // The Heartbeat
  });

  const { data: statuses, error: statusError } = useQuery<AdapterStatus[]>({
    queryKey: ['adapterStatuses'],
    queryFn: fetchAdapterStatuses,
    refetchInterval: 60000
  });

  const handleParamChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setParams(prev => ({ ...prev, [name]: parseFloat(value) }));
  };

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
            <span key={s.adapter_name} className={`px-2 py-1 text-xs font-bold rounded-full ${s.status === 'SUCCESS' || s.status === 'OK' ? 'bg-green-500/20 text-green-300' : 'bg-red-500/20 text-red-300'}`}>
              {s.adapter_name}
            </span>
          ))}
        </div>
      </div>

      {/* --- Analyst's Playground & Smart Filter --- */}
      {/* [Existing Playground and Filter UI code remains here] */}

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