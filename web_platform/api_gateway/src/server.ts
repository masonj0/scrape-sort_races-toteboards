// server.ts - Complete API Gateway with Database Integration and WebSocket

import express from 'express';
import { createServer } from 'http';
import { Server as SocketServer } from 'socket.io';
import cors from 'cors';
import sqlite3 from 'sqlite3';
import { open, Database } from 'sqlite';
import path from 'path';

// Types
interface Race {
  race_id: string;
  track_name: string;
  race_number: number | null;
  post_time: string | null;
  checkmate_score: number;
  qualified: boolean;
  trifecta_factors_json: string | null;
  raw_data_json: string | null;
  updated_at: string;
}

interface AdapterStatus {
  adapter_name: string;
  status: string;
  last_run: string;
  races_found: number;
  execution_time_ms: number;
  error_message: string | null;
}

// Database Service
class DatabaseService {
  private db: Database | null = null;
  private dbPath: string;

  constructor() {
    this.dbPath = process.env.CHECKMATE_DB_PATH || path.join(__dirname, '..', '..', '..', 'shared_database', 'races.db');
  }

  async connect(): Promise<void> {
    try {
      this.db = await open({
        filename: this.dbPath,
        driver: sqlite3.Database
      });
      console.log(`[INFO] Connected to database: ${this.dbPath}`);
    } catch (error) {
      console.error('[ERROR] Failed to connect to database:', error);
      throw error;
    }
  }

  async getQualifiedRaces(): Promise<Race[]> {
    if (!this.db) throw new Error('Database not connected');
    try {
      const races = await this.db.all<Race[]>(`
        SELECT race_id, track_name, race_number, post_time,
               checkmate_score, qualified, trifecta_factors_json,
               raw_data_json, updated_at
        FROM live_races
        WHERE qualified = 1
        ORDER BY checkmate_score DESC, post_time ASC
      `);
      return races;
    } catch (error) {
      console.error('[ERROR] Failed to fetch qualified races:', error);
      return [];
    }
  }

  async getAllRaces(): Promise<Race[]> {
    if (!this.db) throw new Error('Database not connected');
    try {
      const races = await this.db.all<Race[]>(`
        SELECT race_id, track_name, race_number, post_time,
               checkmate_score, qualified, trifecta_factors_json,
               raw_data_json, updated_at
        FROM live_races
        ORDER BY post_time ASC
      `);
      return races;
    } catch (error) {
      console.error('[ERROR] Failed to fetch all races:', error);
      return [];
    }
  }

  async getAdapterStatuses(): Promise<AdapterStatus[]> {
    if (!this.db) throw new Error('Database not connected');
    try {
      const statuses = await this.db.all<AdapterStatus[]>(`
        SELECT adapter_name, status, last_run, races_found,
               execution_time_ms, error_message
        FROM adapter_status
        ORDER BY last_run DESC
      `);
      return statuses;
    } catch (error) {
      console.error('[ERROR] Failed to fetch adapter statuses:', error);
      return [];
    }
  }

  async getRaceById(raceId: string): Promise<Race | null> {
    if (!this.db) throw new Error('Database not connected');
    try {
      const race = await this.db.get<Race>(`
        SELECT race_id, track_name, race_number, post_time,
               checkmate_score, qualified, trifecta_factors_json,
               raw_data_json, updated_at
        FROM live_races
        WHERE race_id = ?
      `, raceId);
      return race || null;
    } catch (error) {
      console.error('[ERROR] Failed to fetch race by ID:', error);
      return null;
    }
  }
}

// Initialize Express and Socket.IO
const app = express();
const httpServer = createServer(app);
const io = new SocketServer(httpServer, {
  cors: { origin: "*" }
});

app.use(cors());
app.use(express.json());

const dbService = new DatabaseService();

// API Endpoints
app.get('/api/status', (req, res) => {
  res.json({
    status: 'online',
    timestamp: new Date().toISOString(),
    service: 'Checkmate API Gateway'
  });
});

app.get('/api/races', async (req, res) => {
  try {
    const races = await dbService.getAllRaces();
    res.json({ success: true, count: races.length, races });
  } catch (error) {
    res.status(500).json({ success: false, error: 'Failed to fetch races' });
  }
});

app.get('/api/races/qualified', async (req, res) => {
  try {
    const races = await dbService.getQualifiedRaces();
    res.json({ success: true, count: races.length, races });
  } catch (error) {
    res.status(500).json({ success: false, error: 'Failed to fetch qualified races' });
  }
});

app.get('/api/races/:raceId', async (req, res) => {
  try {
    const race = await dbService.getRaceById(req.params.raceId);
    if (race) {
      res.json({ success: true, race });
    } else {
      res.status(404).json({ success: false, error: 'Race not found' });
    }
  } catch (error) {
    res.status(500).json({ success: false, error: 'Failed to fetch race' });
  }
});

app.get('/api/adapters/status', async (req, res) => {
  try {
    const statuses = await dbService.getAdapterStatuses();
    res.json({ success: true, count: statuses.length, adapters: statuses });
  } catch (error) {
    res.status(500).json({ success: false, error: 'Failed to fetch adapter statuses' });
  }
});

// WebSocket Connection Handling
io.on('connection', (socket) => {
  console.log(`[WebSocket] Client connected: ${socket.id}`);

  dbService.getQualifiedRaces().then(races => {
    socket.emit('races_update', { races });
  });

  dbService.getAdapterStatuses().then(statuses => {
    socket.emit('adapters_update', { adapters: statuses });
  });

  socket.on('disconnect', () => {
    console.log(`[WebSocket] Client disconnected: ${socket.id}`);
  });

  socket.on('request_update', async () => {
    const races = await dbService.getQualifiedRaces();
    const statuses = await dbService.getAdapterStatuses();
    socket.emit('races_update', { races });
    socket.emit('adapters_update', { adapters: statuses });
  });
});

// Broadcast updates to all clients periodically
async function broadcastUpdates() {
  try {
    const races = await dbService.getQualifiedRaces();
    const statuses = await dbService.getAdapterStatuses();

    io.emit('races_update', { races });
    io.emit('adapters_update', { adapters: statuses });
  } catch (error) {
    console.error('[ERROR] Failed to broadcast updates:', error);
  }
}

// Start Server
const PORT = process.env.PORT || 8080;

async function startServer() {
  try {
    await dbService.connect();

    httpServer.listen(PORT, () => {
      console.log('='.repeat(70));
      console.log(`  Checkmate API Gateway`);
      console.log(`  Running on port ${PORT}`);
      console.log(`  Database: ${dbService['dbPath']}`);
      console.log('='.repeat(70));
    });

    setInterval(broadcastUpdates, 15000);

  } catch (error) {
    console.error('[FATAL] Failed to start server:', error);
    process.exit(1);
  }
}

// Graceful shutdown
process.on('SIGINT', async () => {
  console.log('\n[INFO] Shutting down gracefully...');
  httpServer.close();
  process.exit(0);
});

process.on('SIGTERM', async () => {
  console.log('\n[INFO] Shutting down gracefully...');
  httpServer.close();
  process.exit(0);
});

startServer();