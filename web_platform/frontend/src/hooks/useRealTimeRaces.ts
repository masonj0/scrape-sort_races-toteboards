// web_platform/frontend/src/hooks/useRealTimeRaces.ts
'use client';
import { useState, useEffect } from 'react';
import { io, Socket } from 'socket.io-client';

// NEW: Define the structure for a single analysis factor
export interface FactorResult {
  points: number;
  ok: boolean;
  reason: string;
}

export interface QualifiedRace {
  race_id: string;
  track_name: string;
  race_number: number;
  post_time: string;
  checkmate_score: number;
  // NEW: Add the trifecta factors to the type definition
  trifecta_factors: Record<string, FactorResult>;
}

export const useRealTimeRaces = (apiUrl: string = 'ws://localhost:8080') => {
  const [races, setRaces] = useState<QualifiedRace[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const socket: Socket = io(apiUrl);

    socket.on('connect', () => setIsConnected(true));
    socket.on('disconnect', () => setIsConnected(false));

    socket.on('race_update', (updatedRaces: QualifiedRace[]) => {
      setRaces(updatedRaces.sort((a, b) => b.checkmate_score - a.checkmate_score));
    });

    return () => {
      socket.disconnect();
    };
  }, [apiUrl]);

  return { races, isConnected };
};