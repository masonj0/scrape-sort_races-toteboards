'use client';
import { useState, useEffect, useCallback } from 'react';
import io, { Socket } from 'socket.io-client';
import { Race } from '../types/racing';

export function useRealTimeRaces() {
  const [races, setRaces] = useState<Race[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  const fetchInitialData = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:8080/api/races/qualified');
      const data = await response.json();
      if (data.success) setRaces(data.data);
    } catch (err) { console.error('Initial fetch failed:', err); }
  }, []);

  useEffect(() => {
    fetchInitialData();
    const socket = io('http://localhost:8080');
    socket.on('connect', () => setIsConnected(true));
    socket.on('disconnect', () => setIsConnected(false));
    socket.on('races:updated', (update: { payload: Race[] }) => {
        setRaces(update.payload.sort((a, b) => (b.checkmate_score || 0) - (a.checkmate_score || 0)));
    });
    return () => { socket.disconnect(); };
  }, [fetchInitialData]);

  return { races, isConnected };
}