// web_platform/api_gateway/src/server.ts
// Production-grade implementation of the API Gateway and WebSocket server.

import express from 'express';
import { createServer } from 'http';
import { Server as SocketServer } from 'socket.io';
import sqlite3 from 'sqlite3';
import { open, Database } from 'sqlite';
import cors from 'cors';
import path from 'path';

const app = express();
const httpServer = createServer(app);
const io = new SocketServer(httpServer, {
  cors: { origin: "*", methods: ["GET", "POST"] }
});

// --- Database Connection ---
let db: Database;

async function initializeDatabase() {
  const dbPath = path.resolve(__dirname, '..', '..', '..', 'shared_database', 'races.db');
  console.log(`Attempting to connect to database at: ${dbPath}`);
  db = await open({
    filename: dbPath,
    driver: sqlite3.Database,
    mode: sqlite3.OPEN_READONLY // Open in read-only mode to prevent locking issues
  });
  console.log('Database connection successful.');
}

app.use(cors());

// --- REST API Endpoints ---

app.get('/api/races/qualified', async (req, res) => {
  try {
    const races = await db.all(`
      SELECT race_id, track_name, race_number, post_time,
             checkmate_score, trifecta_factors_json, updated_at
      FROM live_races
      WHERE qualified = 1 AND post_time > datetime('now')
      ORDER BY checkmate_score DESC, post_time ASC
    `);
    res.json(races.map(r => ({ ...r, trifecta_factors: JSON.parse(r.trifecta_factors_json || '{}') })));
  } catch (error) {
    console.error('API Error /api/races/qualified:', error);
    res.status(500).json({ error: 'Failed to fetch qualified races' });
  }
});

app.get('/api/adapters/status', async (req, res) => {
  try {
    const statuses = await db.all(`SELECT * FROM adapter_status ORDER BY last_run DESC`);
    res.json(statuses);
  } catch (error) {
    console.error('API Error /api/adapters/status:', error);
    res.status(500).json({ error: 'Failed to fetch adapter statuses' });
  }
});

// --- Real-time Database Polling for WebSocket ---

async function pollForUpdates() {
    try {
        const lastEvent = await db.get('SELECT event_id, timestamp FROM events ORDER BY event_id DESC LIMIT 1');
        let lastEventId = lastEvent ? lastEvent.event_id : 0;

        setInterval(async () => {
            const newEvent = await db.get('SELECT event_id FROM events WHERE event_id > ? ORDER BY event_id DESC LIMIT 1', lastEventId);
            if (newEvent) {
                console.log(`New event detected (ID: ${newEvent.event_id}). Broadcasting updates.`);
                const updatedRaces = await db.all(`SELECT * FROM live_races WHERE qualified = 1 AND post_time > datetime('now') ORDER BY checkmate_score DESC`);
                io.emit('race_update', updatedRaces.map(r => ({ ...r, trifecta_factors: JSON.parse(r.trifecta_factors_json || '{}') })));
                lastEventId = newEvent.event_id;
            }
        }, 2000); // Poll every 2 seconds
    } catch (error) {
        console.error('Database polling failed:', error);
    }
}

// --- Server Startup ---

async function startServer() {
  await initializeDatabase();

  io.on('connection', (socket) => {
    console.log(`Client connected: ${socket.id}`);
    socket.on('disconnect', () => {
      console.log(`Client disconnected: ${socket.id}`);
    });
  });

  await pollForUpdates();

  const PORT = process.env.PORT || 8080;
  httpServer.listen(PORT, () => {
    console.log(`Checkmate API Gateway running on http://localhost:${PORT}`);
  });
}

startServer().catch(error => {
    console.error("Failed to start server:", error);
    process.exit(1);
});