'use client';
import React from 'react';
import { motion } from 'framer-motion';
import { QualifiedRace } from '../hooks/useRealTimeRaces';
import { ScoreBadge } from './ScoreBadge';

const getScoreColorClass = (score: number) => {
  if (score >= 90) return 'border-l-yellow-400';
  if (score >= 80) return 'border-l-orange-500';
  return 'border-l-sky-500';
};

export const RaceCard: React.FC<{ race: QualifiedRace }> = ({ race }) => {
  return (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      transition={{ duration: 0.35, type: 'spring' }}
      className={`rounded-lg border-l-4 ${getScoreColorClass(race.checkmate_score)} bg-slate-800/50 p-5 shadow-xl backdrop-blur-sm`}
    >
      <div className="flex justify-between items-start">
        <div>
          <h3 className="text-xl font-semibold text-white">{race.track_name} R{race.race_number}</h3>
          <p className="text-slate-400">Post: {new Date(race.post_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</p>
        </div>
        <ScoreBadge score={race.checkmate_score} />
      </div>
      {/* Future TrifectaFactors component will go here */}
    </motion.div>
  );
};