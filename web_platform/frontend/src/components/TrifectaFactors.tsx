'use client';
import React from 'react';
import { FactorResult } from '../hooks/useRealTimeRaces';

const factorNameMapping: Record<string, string> = {
    fieldSize: 'Field Size',
    favoriteOdds: 'Favorite Odds',
    secondFavoriteOdds: '2nd Favorite Odds'
};

export const TrifectaFactors: React.FC<{ factors: Record<string, FactorResult> }> = ({ factors }) => {
    if (!factors) return null;

    return (
        <div className="mt-4 pt-4 border-t border-slate-700/50 space-y-2">
            {Object.entries(factors).map(([key, factor]) => (
                <div key={key} className="flex justify-between items-center text-sm">
                    <div className="flex items-center space-x-2">
                        <span className={`w-2 h-2 rounded-full ${factor.ok ? 'bg-green-400' : 'bg-red-400'}`}></span>
                        <span className="text-slate-400">{factorNameMapping[key] || key}</span>
                    </div>
                    <span className="font-mono font-semibold text-white">
                        {factor.points > 0 ? '+' : ''}{factor.points.toFixed(0)}
                    </span>
                </div>
            ))}
        </div>
    );
};