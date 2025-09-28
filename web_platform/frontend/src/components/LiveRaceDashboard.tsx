'use client';
import React from 'react';
import { AnimatePresence } from 'framer-motion';
import { useRealTimeRaces } from '../hooks/useRealTimeRaces';
import { RaceCard } from './RaceCard';

export const LiveRaceDashboard: React.FC = () => {
  const { races, isConnected } = useRealTimeRaces();

  return (
    <div className="min-h-screen bg-slate-900 text-white font-sans">
      <header className="bg-slate-800/70 backdrop-blur-md sticky top-0 z-50 border-b border-slate-700 p-4 shadow-lg">
        <div className="flex justify-between items-center max-w-7xl mx-auto">
          <h1 className="text-2xl font-bold tracking-tighter">Checkmate Live</h1>
          <div className="flex items-center space-x-3">
            <div className={`w-3 h-3 rounded-full transition-colors ${isConnected ? 'bg-green-400 animate-pulse' : 'bg-red-500'}`}></div>
            <span className="text-sm font-medium text-slate-300">{isConnected ? 'LIVE' : 'CONNECTING...'}</span>
          </div>
        </div>
      </header>

      <main className="p-4 md:p-6 max-w-7xl mx-auto">
        <AnimatePresence>
          {races.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {races.map((race) => (
                <RaceCard key={race.race_id} race={race} />
              ))}
            </div>
          ) : (
            <div className="text-center mt-24 text-slate-500">
              <p className="text-3xl font-semibold">Awaiting Data...</p>
              <p className="mt-2\">No qualified races found. The system is actively monitoring all sources.</p>
            </div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
};