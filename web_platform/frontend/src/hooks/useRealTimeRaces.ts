// web_platform/frontend/src/hooks/useRealTimeRaces.ts
'use client';

import { useState, useEffect } from 'react';
import { io, Socket } from 'socket.io-client';

const API_URL = 'http://localhost:8080';

export interface QualifiedRace {
  race_id: string;
  track_name: string;
  race_number: number;
  post_time: string; // ISO string format
  checkmate_score: number;
  trifecta_factors_json: string;
  updated_at: string;
}

export const useRealTimeRaces = () => {
  const [races, setRaces] = useState<QualifiedRace[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // 1. Fetch initial data via REST API
    const fetchInitialData = async () => {
      try {
        const response = await fetch(`${API_URL}/api/races/qualified`);
        if (response.ok) {
          const initialRaces = await response.json();
          setRaces(initialRaces);
        } else {
          console.error('Failed to fetch initial race data');
        }
      } catch (error) {
        console.error('Error fetching initial data:', error);
      }
    };

    fetchInitialData();

    // 2. Connect to WebSocket for real-time updates
    const socket: Socket = io(API_URL);

    socket.on('connect', () => {
      console.log('Socket.IO connected successfully.');
      setIsConnected(true);
    });

    socket.on('disconnect', () => {
      console.log('Socket.IO disconnected.');
      setIsConnected(false);
    });

    socket.on('race_update', (updatedRaces: QualifiedRace[]) => {
      console.log('Received race_update event with', updatedRaces.length, 'races.');
      setRaces(updatedRaces);
    });

    // 3. Cleanup on component unmount
    return () => {
      console.log('Disconnecting Socket.IO...');
      socket.disconnect();
    };
  }, []); // Empty dependency array ensures this runs only once on mount

  return { races, isConnected };
};