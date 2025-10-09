// web_platform/frontend/src/components/RaceCard.tsx
'use client';

import React from 'react';

// Type definitions matching the backend Race model
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

interface RaceCardProps {
  race: Race;
}

export const RaceCard: React.FC<RaceCardProps> = ({ race }) => {
  const raceTime = new Date(race.start_time).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit'
  });

  const activeRunners = race.runners.filter(r => !r.scratched);

  // Get best odds for each runner
  const runnersWithOdds = activeRunners.map(runner => {
    const odds = Object.values(runner.odds);
    const bestOdds = odds.length > 0
      ? Math.min(...odds.map(o => o.win || 999).filter(o => o < 999))
      : null;
    return { ...runner, bestOdds };
  }).filter(r => r.bestOdds !== null);

  return (
    <div className="border border-gray-700 rounded-lg p-4 bg-gray-800 shadow-lg hover:border-purple-500 transition-all">
      <div className="flex justify-between items-center mb-3">
        <h3 className="text-xl font-bold text-white">
          {race.venue} - R{race.race_number}
        </h3>
        <span className="text-lg font-semibold text-yellow-400">{raceTime}</span>
      </div>

      {race.qualification_score && (
        <div className="mb-3 inline-block px-3 py-1 bg-purple-500/20 rounded-full">
          <span className="text-sm font-semibold text-purple-400">
            Score: {race.qualification_score}
          </span>
        </div>
      )}

      <div className="text-sm text-gray-400 mb-3">
        ID: {race.id} | Source: {race.source}
      </div>

      <div>
        <h4 className="text-md font-semibold text-gray-300 mb-2">
          Runners ({activeRunners.length}):
        </h4>
        <div className="space-y-2 max-h-60 overflow-y-auto">
          {runnersWithOdds.map(runner => (
            <div
              key={runner.number}
              className="flex justify-between items-center p-2 bg-gray-900/50 rounded border border-gray-700/50"
            >
              <div className="flex items-center gap-2">
                <span className="w-8 h-8 rounded-full bg-purple-500/20 flex items-center justify-center font-bold text-sm text-purple-300">
                  {runner.number}
                </span>
                <span className="text-gray-200">{runner.name}</span>
              </div>
              {runner.bestOdds && (
                <span className="text-emerald-400 font-semibold">
                  {runner.bestOdds.toFixed(2)}
                </span>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};