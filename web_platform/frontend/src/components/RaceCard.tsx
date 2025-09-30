// RaceCard.tsx - FINAL, DYNAMIC VERSION
'use client';
import React from 'react';
import { ScoreBadge } from './ScoreBadge';
import { TrifectaFactors } from './TrifectaFactors';
import { Race } from '../types/racing';

interface RaceCardProps {
  race: Race;
}

export function RaceCard({ race }: RaceCardProps) {
  const postTime = new Date(race.post_time).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <div className="border p-4 rounded-lg shadow-md bg-white hover:shadow-lg transition-shadow duration-200">
      <div className="flex justify-between items-start mb-2">
        <div>
          <h3 className="font-bold text-lg">{race.track_name} - Race {race.race_number}</h3>
          <p className="text-sm text-gray-600">Post Time: {postTime}</p>
        </div>
        <ScoreBadge score={race.checkmate_score} />
      </div>
      <TrifectaFactors factorsJson={race.trifecta_factors_json} />
    </div>
  );
}