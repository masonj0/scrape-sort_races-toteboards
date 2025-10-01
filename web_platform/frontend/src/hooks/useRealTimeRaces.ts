import { useState, useEffect } from 'react';
import { io, Socket } from 'socket.io-client';
import { Race } from '../types/racing';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

export function useRealTimeRaces() {
  const [races, setRaces] = useState<Race[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const socket: Socket = io(API_URL);

    socket.on('connect', () => setIsConnected(true));
    socket.on('disconnect', () => setIsConnected(false));

    socket.on('races_update', (data: { races: Race[] }) => {
      if (data && Array.isArray(data.races)) {
        setRaces(data.races);
      }
    });

    // Cleanup on component unmount
    return () => {
      socket.disconnect();
    };
  }, []);

  return { races, isConnected };
}