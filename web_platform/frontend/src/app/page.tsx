'use client';
import React, { useState, useEffect } from 'react';
import { Activity, Settings, Minimize, Filter } from 'lucide-react';
import RaceCard from '../components/RaceCard'; // Assuming component is in a sub-folder
// Mock data and other components would be imported here in a real scenario

const FortunaDesktopMockup = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
        setLoading(true);
        try {
            const response = await fetch('/api/races/qualified/trifecta');
            if (!response.ok) throw new Error('Network response was not ok');
            const raceData = await response.json();
            setData({ races: raceData }); // Adapt to the structure needed
        } catch (error) {
            console.error("Fetch error:", error);
        } finally {
            setLoading(false);
        }
    }
    fetchData();
  }, []);

  if (loading || !data) {
    return <div className="min-h-screen bg-gray-900 flex items-center justify-center"><div className="animate-spin rounded-full h-16 w-16 border-b-2 border-purple-500\"></div></div>;
  }

  const qualifiedRaces = data.races.filter(r => r.qualification_score > 0);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
        <header className="border-b border-gray-700/50 bg-gray-900/50 backdrop-blur-xl sticky top-0 z-40 px-6 py-4">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center shadow-lg"><Activity className="w-6 h-6 text-white" /></div>
                    <div><h1 className="text-xl font-bold text-white\">Fortuna Faucet</h1></div>
                </div>
            </div>
        </header>
        <main className="p-6">
            <div className="grid grid-cols-2 gap-4">
              {qualifiedRaces.map(race => (
                <RaceCard key={race.id} race={race} onClick={() => alert(`Selected ${race.track} Race ${race.raceNumber}`)} />
              ))}
            </div>
        </main>
    </div>
  );
};

export default FortunaDesktopMockup;