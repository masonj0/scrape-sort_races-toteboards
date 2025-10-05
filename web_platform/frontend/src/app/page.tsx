'use client';

import { useState, useEffect } from 'react';

// --- Type Definitions (Corrected to match API) ---
interface OddsData {
  win?: number;
  source: string;
  last_updated: string;
}

interface Runner {
  name: string;
  number: number;
  scratched: boolean;
  odds: { [source: string]: OddsData };
}

interface Race {
  id: string; // Corrected from race_id
  venue: string;
  race_number: number;
  start_time: string;
  runners: Runner[];
}

// --- Helper Function ---
function getBestWinOdds(runner: Runner): number | null {
    if (!runner.odds) return null;
    const validOdds = Object.values(runner.odds)
                            .map(o => o.win)
                            .filter((o): o is number => o !== undefined && o !== null);
    return validOdds.length > 0 ? Math.min(...validOdds) : null;
}


// --- API Fetching Hook ---
function useQualifiedRaces() {
  const [races, setRaces] = useState<Race[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchRaces() {
      setLoading(true);
      try {
        // NOTE: The API endpoint requires a valid API Key in the header.
        // This example assumes the Next.js proxy is configured to add it.
        const response = await fetch('/api/races/qualified');
        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`HTTP error! status: ${response.status}, details: ${errorText}`);
        }
        const data: Race[] = await response.json();
        setRaces(data);
        setError(null);
      } catch (e: any) {
        setError(e.message);
        console.error("Failed to fetch qualified races:", e);
      } finally {
        setLoading(false);
      }
    }

    fetchRaces();
    const intervalId = setInterval(fetchRaces, 60000); // Refresh every 60 seconds

    return () => clearInterval(intervalId); // Cleanup on unmount
  }, []);

  return { races, loading, error };
}

// --- UI Components ---
function RaceCard({ race }: { race: Race }) {
  return (
    <div className="bg-gray-800 rounded-lg shadow-lg p-4 mb-4">
      <div className="flex justify-between items-center mb-2">
        <h3 className="text-xl font-bold text-cyan-400">{race.venue} - Race {race.race_number}</h3>
        <span className="text-sm text-gray-400">{new Date(race.start_time).toLocaleTimeString()}</span>
      </div>
      <table className="w-full text-left text-sm">
        <thead>
          <tr className="border-b border-gray-600">
            <th className="py-1">#</th>
            <th className="py-1">Runner</th>
            <th className="text-right py-1">Win Odds</th>
          </tr>
        </thead>
        <tbody>
          {race.runners.map((runner) => {
            const bestOdds = getBestWinOdds(runner);
            return (
              <tr key={runner.number} className={`border-b border-gray-700 last:border-b-0 ${runner.scratched ? 'text-gray-500 line-through' : ''}`}>
                <td className="py-1">{runner.number}</td>
                <td className="py-1">{runner.name}</td>
                <td className="text-right font-mono py-1">{bestOdds ? bestOdds.toFixed(2) : 'N/A'}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

// --- Main Page Component ---
export default function Home() {
  const { races, loading, error } = useQualifiedRaces();

  return (
    <main className="flex min-h-screen flex-col items-center justify-start p-12 bg-gray-900 text-white">
      <div className="z-10 w-full max-w-5xl items-center justify-between font-mono text-sm lg:flex mb-8">
        <p className="text-2xl font-bold text-white">Fortuna Faucet: Qualified Races</p>
        <div className="fixed bottom-0 left-0 flex h-48 w-full items-end justify-center bg-gradient-to-t from-white via-white dark:from-black dark:via-black lg:static lg:h-auto lg:w-auto lg:bg-none">
          <p>Status: {loading ? 'Refreshing...' : error ? 'Error' : 'Live'}</p>
        </div>
      </div>

      <div className="w-full max-w-5xl">
        {error && (
          <div className="bg-red-900 border border-red-500 text-red-200 px-4 py-3 rounded-md mb-4">
            <strong className="font-bold\">Fetch Error:</strong>
            <span className="block sm:inline ml-2">{error}</span>
          </div>
        )}

        {races.length > 0 ? (
          races.map((race) => <RaceCard key={race.id} race={race} />) // Corrected key to race.id
        ) : (
          !loading && <p className="text-center text-gray-400\">No qualified races found at this time.</p>
        )}
      </div>
    </main>
  );
}