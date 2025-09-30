// LiveRaceDashboard.tsx - FINAL, DYNAMIC VERSION
'use client';
import React from 'react';
import { useRealTimeRaces } from '../hooks/useRealTimeRaces';
import { RaceCard } from './RaceCard';
import { Race } from '../types/racing';

export function LiveRaceDashboard() {
  const { races, isConnected } = useRealTimeRaces();

  return (
    <div className="p-4 md:p-6 bg-gray-100 min-h-screen">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-3xl font-bold text-gray-800">Live Race Dashboard</h1>
          <div className="text-sm font-medium">
            Status: {isConnected ?
              <span className="text-green-600">● Connected</span> :
              <span className="text-red-600">● Disconnected</span>}
          </div>
        </div>

        {!isConnected && (
          <div className="text-center p-8 bg-white rounded-lg shadow-md">
            <p className="text-gray-600">Connecting to the live data feed...</p>
          </div>
        )}

        {isConnected && races.length === 0 && (
          <div className="text-center p-8 bg-white rounded-lg shadow-md">
            <p className="text-gray-600">Connected. Waiting for the first set of qualified race data...</p>
            <p className="text-xs text-gray-400 mt-2">This may take a moment. Ensure the Python service is running.</p>
          </div>
        )}

        {isConnected && races.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {(races as Race[]).map((race) => (
              <RaceCard key={race.race_id} race={race} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}