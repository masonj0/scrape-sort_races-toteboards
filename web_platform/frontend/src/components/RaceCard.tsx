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
  jockey?: string;
  trainer?: string;
}

interface Race {
  id: string;
  venue: string;
  race_number: number;
  start_time: string;
  runners: Runner[];
  source: string;
  qualification_score?: number;
  distance?: string;
  surface?: string;
}

interface RaceCardProps {
  race: Race;
}

// Helper function from the UI Bible
function formatTimeUntilPost(startTime: string): string {
  const now = new Date();
  const post = new Date(startTime);
  const diff = post.getTime() - now.getTime();

  if (diff < 0) return 'Post Time Passed';

  const hours = Math.floor(diff / (1000 * 60 * 60));
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

  return `${hours}h ${minutes}m`;
}

export const RaceCard: React.FC<RaceCardProps> = ({ race }) => {
  const activeRunners = race.runners.filter(r => !r.scratched);
  activeRunners.sort((a, b) => a.number - b.number);

  const getUniqueSourcesCount = (runners: Runner[]): number => {
    const sources = new Set();
    runners.forEach(runner => {
      if (runner.odds) {
        Object.keys(runner.odds).forEach(source => sources.add(source));
      }
    });
    return sources.size;
  };

  const getBestOdds = (runner: Runner): { odds: number, source: string } | null => {
    if (!runner.odds) return null;
    const validOdds = Object.values(runner.odds).filter(o => o.win && o.win < 999);
    if (validOdds.length === 0) return null;
    const best = validOdds.reduce((min, o) => o.win! < min.win! ? o : min);
    return { odds: best.win!, source: best.source };
  };

  return (
    <div className={`race-card-enhanced border rounded-lg p-4 bg-gray-800 shadow-lg hover:border-purple-500 transition-all ${race.qualification_score && race.qualification_score >= 80 ? 'card-premium' : 'border-gray-700'}`}>
      {/* Header with Smart Status Indicators */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div>
            <h2 className="text-2xl font-bold text-white">{race.venue}</h2>
            <div className="flex gap-2 text-sm text-gray-400">
              <span>Race {race.race_number}</span>
              <span>•</span>
              <span>{formatTimeUntilPost(race.start_time)}</span>
            </div>
          </div>
        </div>

        {race.qualification_score && (
          <div className={`px-4 py-2 rounded-full text-center ${
            race.qualification_score >= 80 ? 'bg-red-500/20 text-red-400 border border-red-500/30' :
            race.qualification_score >= 60 ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30' :
            'bg-green-500/20 text-green-400 border border-green-500/30'
          }`}>
            <div className="font-bold text-lg">{race.qualification_score.toFixed(0)}%</div>
            <div className="text-xs">Score</div>
          </div>
        )}
      </div>

      {/* Race Conditions Grid */}
      <div className="grid grid-cols-4 gap-2 mb-4 p-3 bg-gray-800/50 rounded-lg">
        <div className="text-center">
          <div className="text-xs text-gray-400">Distance</div>
          <div className="text-sm font-semibold text-white">{race.distance || 'N/A'}</div>
        </div>
        <div className="text-center">
          <div className="text-xs text-gray-400">Surface</div>
          <div className="text-sm font-semibold text-white">{race.surface || 'Dirt'}</div>
        </div>
        <div className="text-center">
          <div className="text-xs text-gray-400">Field</div>
          <div className="text-sm font-semibold text-white">{activeRunners.length}</div>
        </div>
        <div className="text-center">
          <div className="text-xs text-gray-400">Sources</div>
          <div className="text-sm font-semibold text-white">{getUniqueSourcesCount(race.runners)}</div>
        </div>
      </div>

      {/* Interactive Runner Rows */}
      <div className="runners-table space-y-2">
        {activeRunners.map((runner, idx) => {
          const bestOddsInfo = getBestOdds(runner);
          return (
            <div key={runner.number} className="runner-row group hover:bg-purple-500/10 transition-all rounded-md p-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4 flex-1">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold transition-all group-hover:scale-110 text-gray-900 shadow-lg ${idx === 0 ? 'bg-gradient-to-br from-yellow-400 to-yellow-600 shadow-yellow-500/50' : idx === 1 ? 'bg-gradient-to-br from-gray-300 to-gray-500 shadow-gray-400/50' : idx === 2 ? 'bg-gradient-to-br from-orange-400 to-orange-600 shadow-orange-500/50' : 'bg-gray-700 text-gray-300'}`}>
                    {runner.number}
                  </div>
                  <div className="flex flex-col">
                    <span className="font-bold text-white text-lg">{runner.name}</span>
                    <div className="flex gap-3 text-sm text-gray-400">
                      {runner.jockey && <span>J: {runner.jockey}</span>}
                      {runner.trainer && <span>T: {runner.trainer}</span>}
                    </div>
                  </div>
                </div>
                {bestOddsInfo && (
                  <div className="text-right">
                    <div className="text-2xl font-bold text-emerald-400">{bestOddsInfo.odds.toFixed(2)}</div>
                    <div className="text-xs text-gray-500">via {bestOddsInfo.source}</div>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};