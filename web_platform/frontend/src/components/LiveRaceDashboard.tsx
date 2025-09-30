'use client';
import React from 'react';
import { useRealTimeRaces } from '../hooks/useRealTimeRaces';

export function LiveRaceDashboard() {
  const { races, isConnected } = useRealTimeRaces();

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Live Race Dashboard</h1>
      <div className="mb-4">
        Connection Status: {isConnected ? <span className="text-green-500">Connected</span> : <span className="text-red-500">Disconnected</span>}
      </div>

      {!isConnected && <p>Connecting to the live data feed...</p>}

      {isConnected && races.length === 0 && (
        <p>Connected, waiting for race data...</p>
      )}

      {isConnected && races.length > 0 && (
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white">
            <thead>
              <tr>
                <th className="py-2 px-4 border-b">Track</th>
                <th className="py-2 px-4 border-b">Race #</th>
                <th className="py-2 px-4 border-b">Post Time</th>
                <th className="py-2 px-4 border-b">Score</th>
              </tr>
            </thead>
            <tbody>
              {races.map((race) => (
                <tr key={race.race_id}>
                  <td className="py-2 px-4 border-b">{race.track_name}</td>
                  <td className="py-2 px-4 border-b">{race.race_number}</td>
                  <td className="py-2 px-4 border-b">{new Date(race.post_time).toLocaleTimeString()}</td>
                  <td className="py-2 px-4 border-b font-bold">{race.checkmate_score.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}