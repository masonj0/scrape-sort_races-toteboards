'use client';
import { Trophy, Clock, TrendingUp, ChevronRight } from 'lucide-react';

const RaceCard = ({ race, onClick }) => {
  const activeRunners = race.runners.filter(r => !r.scratched);
  const sortedRunners = [...activeRunners].sort((a, b) => a.bestOdds - b.bestOdds);
  const topRunners = sortedRunners.slice(0, 3);

  return (
    <div onClick={onClick} className="bg-gradient-to-br from-gray-800/90 to-gray-900/90 border border-gray-700/50 rounded-lg p-4 hover:border-purple-500/50 transition-all cursor-pointer group">
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h3 className="text-base font-bold text-white mb-1 group-hover:text-purple-400 transition-colors">{race.track} - Race {race.raceNumber}</h3>
          <div className="flex gap-2 text-xs text-gray-400"><span>{race.distance}</span><span>•</span><span>{race.surface}</span><span>•</span><span>{activeRunners.length} runners</span></div>
        </div>
        {race.qualified && (
          <div className="flex items-center gap-1.5 bg-purple-500/20 px-2.5 py-1 rounded-full">
            <TrendingUp className="w-3.5 h-3.5 text-purple-400" />
            <span className="text-xs font-semibold text-purple-400">{race.qualificationScore}% Match</span>
          </div>
        )}
      </div>
      <div className="space-y-2">
        <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Top Contenders</h4>
        {topRunners.map((runner, idx) => (
          <div key={runner.number} className="flex items-center justify-between bg-gray-900/50 rounded-md p-2.5 border border-gray-700/50">
            <div className="flex items-center gap-2.5">
              <div className={`w-7 h-7 rounded-full flex items-center justify-center font-bold text-xs ${idx === 0 ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30' : ''} ${idx === 1 ? 'bg-gray-500/20 text-gray-300 border border-gray-500/30' : ''} ${idx === 2 ? 'bg-orange-500/20 text-orange-400 border border-orange-500/30' : ''}`}>{runner.number}</div>
              <div className="flex flex-col"><span className="text-white font-medium text-sm">{runner.name}</span><span className="text-xs text-gray-500">{runner.jockey}</span></div>
            </div>
            <div className="text-right"><div className="text-base font-bold text-emerald-400">{runner.bestOdds.toFixed(2)}</div><div className="text-xs text-gray-500\">best odds</div></div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RaceCard;