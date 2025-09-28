// src/app/page.tsx
'use client';
import { useRealTimeRaces, Race, FactorResult } from '../hooks/useRealTimeRaces';
import { motion, AnimatePresence } from 'framer-motion';

const RaceCard: React.FC<{ race: Race }> = ({ race }) => {
  const factors: Record<string, FactorResult> = JSON.parse(race.trifecta_factors_json || '{}');
  return (
    <motion.div layout initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className='bg-gray-800 p-4 rounded-lg'>
      <h3 className='text-lg font-bold'>{race.track_name} R{race.race_number}</h3>
      <p>Score: {race.checkmate_score?.toFixed(1)}</p>
    </motion.div>
  );
};

export default function HomePage() {
  const { races, isConnected } = useRealTimeRaces();
  return (
    <div className='bg-gray-900 min-h-screen text-white p-4'>
      <header className='flex justify-between items-center mb-4'>
        <h1 className='text-2xl font-bold'>Checkmate Live</h1>
        <p>{isConnected ? '🟢 LIVE' : '🔴 DISCONNECTED'}</p>
      </header>
      <AnimatePresence>
        <div className='grid grid-cols-1 md:grid-cols-3 gap-4'>
            {races.map(race => <RaceCard key={race.race_id} race={race} />)}
        </div>
      </AnimatePresence>
    </div>
  );
}