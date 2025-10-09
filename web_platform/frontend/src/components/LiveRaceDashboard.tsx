// web_platform/frontend/src/components/LiveRaceDashboard.tsx
'use client';

import React, { useState, useEffect } from 'react';
import { RaceCard } from './RaceCard';

// Type definitions matching backend AggregatedResponse model
interface Race {
  id: string;
  venue: string;
  race_number: number;
  start_time: string;
  runners: any[];
  source: string;
  qualification_score?: number;
}

interface SourceInfo {
  name: string;
  status: string;
  races_fetched: number;
  error_message?: string;
  fetch_duration: number;
}

interface FetchMetadata {
  fetch_time: string;
  sources_queried: string[];
  sources_successful: number;
  sources_failed?: number;
  failed_sources_list?: string[];
  total_races: number;
}

interface ApiResponse {
  date: string;
  races: Race[];
  sources: SourceInfo[];
  metadata: FetchMetadata;
}

export const LiveRaceDashboard: React.FC = () => {
  const [apiData, setApiData] = useState<ApiResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRaces = async () => {
      setLoading(true);
      setError(null);

      try {
        // Use environment variable for API key
        const apiKey = process.env.NEXT_PUBLIC_API_KEY;

        if (!apiKey) {
          throw new Error('API key not configured. Please set NEXT_PUBLIC_API_KEY in .env.local');
        }

        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/api/races`, {
          headers: {
            'X-API-Key': apiKey,
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          throw new Error(`API request failed with status ${response.status}`);
        }

        const data: ApiResponse = await response.json();
        setApiData(data);
      } catch (e) {
        const errorMessage = e instanceof Error ? e.message : 'An unknown error occurred';
        setError(errorMessage);
        console.error('Error fetching races:', e);
      } finally {
        setLoading(false);
      }
    };

    fetchRaces();

    // Optional: Refresh every 60 seconds
    const interval = setInterval(fetchRaces, 60000);
    return () => clearInterval(interval);
  }, []);

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold text-center mb-2 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
          Fortuna Faucet Command Deck
        </h1>
        <p className="text-center text-gray-400 mb-8">
          Real-time racing analysis powered by {apiData?.sources.length || 0} data sources
        </p>

        {/* Metadata Display */}
        {apiData?.metadata && (
          <div className="mb-8 p-4 bg-gray-800/50 border border-gray-700 rounded-lg">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold text-purple-400">
                  {apiData.metadata.total_races}
                </div>
                <div className="text-sm text-gray-400">Total Races</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-emerald-400">
                  {apiData.metadata.sources_successful}
                </div>
                <div className="text-sm text-gray-400">Sources Active</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-yellow-400">
                  {apiData.metadata.sources_queried.length}
                </div>
                <div className="text-sm text-gray-400">Sources Queried</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-blue-400">
                  {new Date(apiData.metadata.fetch_time).toLocaleTimeString()}
                </div>
                <div className="text-sm text-gray-400">Last Updated</div>
              </div>
            </div>

            {apiData.metadata.failed_sources_list && apiData.metadata.failed_sources_list.length > 0 && (
              <div className="mt-3 p-2 bg-red-500/10 border border-red-500/30 rounded text-sm text-red-400">
                Failed sources: {apiData.metadata.failed_sources_list.join(', ')}
              </div>
            )}
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="flex justify-center items-center py-20">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-purple-500"></div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="p-6 bg-red-500/10 border border-red-500/30 rounded-lg text-center">
            <p className="text-xl font-semibold text-red-400 mb-2">Error Loading Races</p>
            <p className="text-red-300">{error}</p>
            <p className="text-sm text-gray-400 mt-4">
              Make sure the backend is running at http://localhost:8000 and your .env.local file is configured correctly.
            </p>
          </div>
        )}

        {/* Races Grid */}
        {!loading && !error && apiData && (
          <>
            {apiData.races.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {apiData.races.map(race => (
                  <RaceCard key={race.id} race={race} />
                ))}
              </div>
            ) : (
              <div className="text-center py-20">
                <p className="text-xl text-gray-400">No races found for today.</p>
                <p className="text-sm text-gray-500 mt-2">
                  Data sources: {apiData.sources.map(s => s.name).join(', ')}
                </p>
              </div>
            )}
          </>
        )}
      </div>
    </main>
  );
};