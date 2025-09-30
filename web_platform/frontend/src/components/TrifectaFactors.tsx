// TrifectaFactors.tsx - FINAL, DYNAMIC VERSION
'use client';
import React from 'react';

interface TrifectaFactorsProps {
  factorsJson: string | null;
}

export function TrifectaFactors({ factorsJson }: TrifectaFactorsProps) {
  if (!factorsJson) {
    return <div className="text-sm text-gray-500">No analysis factors available.</div>;
  }

  try {
    const factors = JSON.parse(factorsJson);
    const positiveFactors = Object.entries(factors).filter(([key, value]: [string, any]) => value.ok);

    if (positiveFactors.length === 0) {
      return <div className="text-sm text-gray-500">No positive factors identified.</div>;
    }

    return (
      <div className="mt-2 text-xs">
        <h4 className="font-semibold mb-1">Key Factors:</h4>
        <ul className="list-disc list-inside space-y-1">
          {positiveFactors.map(([key, value]: [string, any]) => (
            <li key={key} className="text-gray-700">
              <span className="font-medium text-green-600">✓</span> {value.reason} ({value.points > 0 ? `+${value.points}` : value.points} pts)
            </li>
          ))}
        </ul>
      </div>
    );
  } catch (error) {
    console.error("Failed to parse trifecta factors:", error);
    return <div className="text-sm text-red-500">Error displaying analysis factors.</div>;
  }
}