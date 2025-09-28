'use client';
import React from 'react';

const getScoreStyling = (score: number) => {
  if (score >= 90) return { bg: 'bg-yellow-400/10', text: 'text-yellow-300', border: 'border-yellow-400' };
  if (score >= 80) return { bg: 'bg-orange-500/10', text: 'text-orange-400', border: 'border-orange-500' };
  return { bg: 'bg-sky-500/10', text: 'text-sky-400', border: 'border-sky-500' };
};

export const ScoreBadge: React.FC<{ score: number }> = ({ score }) => {
  const { bg, text } = getScoreStyling(score);
  return (
    <div className={`text-right ${text}`}>
      <p className="text-3xl font-bold">{score.toFixed(1)}</p>
      <p className="text-xs font-medium tracking-wider uppercase\">Score</p>
    </div>
  );
};