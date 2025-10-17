'use client';

import { useState } from 'react';

// Mock data for demonstration purposes
const mockRaces = [
  { venue: 'Aqueduct', race_number: 3, start_time: new Date(), qualification_score: 92 },
  { venue: 'Santa Anita', race_number: 5, start_time: new Date(), qualification_score: 88 },
  { venue: 'Gulfstream', race_number: 7, start_time: new Date(), qualification_score: 85 },
  { venue: 'Oaklawn', race_number: 1, start_time: new Date(), qualification_score: 81 },
];

const formatTime = (date) => {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

const SimpleModeDashboard = () => {
  return (
    <div className="w-full max-w-6xl mx-auto p-4 md:p-8">
      <h1 className="text-3xl font-bold text-gray-100 mb-2">Today's Top Race Opportunities</h1>
      <p className="text-lg text-gray-400 mb-8">Click a race below to see details. High scores indicate a stronger match.</p>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {mockRaces.map((race, index) => (
          <div key={index} className="bg-gray-800 border border-gray-700 rounded-lg p-6 flex flex-col justify-between hover:border-green-400 transition-all duration-200">
            <div>
                <h3 className="text-xl font-bold text-white">{race.venue} - Race {race.race_number}</h3>
                <p className="text-gray-400 mb-4">Post Time: {formatTime(race.start_time)}</p>
            </div>
            <div className='text-center mb-4'>
                <p className="text-5xl font-bold text-green-400">{race.qualification_score}%</p>
                <p className="text-gray-400">Match Score</p>
            </div>
            <button className="w-full bg-green-500 text-black font-bold py-3 rounded-lg hover:bg-green-400 transition-colors">View Details</button>
          </div>
        ))}
      </div>
    </div>
  );
};

const AdvancedModeDashboard = () => {
    // This component would contain the original, complex data grid and filtering options.
    return (
        <div className='text-white p-8'>
            <h1 className='text-2xl font-bold'>Advanced Analytics Dashboard</h1>
            <p className='text-gray-400 mt-4'>Full data tables, filters, and expert tools would be rendered here.</p>
        </div>
    );
}

export default function Home() {
  const [isSimpleMode, setIsSimpleMode] = useState(true);

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-4 md:p-12 bg-gray-900">
        <div className='w-full absolute top-4 right-4 flex justify-end'>
            <button
                onClick={() => setIsSimpleMode(!isSimpleMode)}
                className='bg-gray-700 text-white font-semibold py-2 px-4 rounded-lg hover:bg-gray-600 transition-colors'
            >
                {isSimpleMode ? 'Switch to Advanced Mode' : 'Switch to Simple Mode'}
            </button>
        </div>

        {isSimpleMode ? <SimpleModeDashboard /> : <AdvancedModeDashboard />}
    </main>
  );
}