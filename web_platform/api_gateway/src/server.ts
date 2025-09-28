// server.ts - Production-ready API Gateway
import express, { Request, Response, NextFunction } from 'express';
import { createServer } from 'http';
import { Server as SocketServer } from 'socket.io';
import cors from 'cors';
import sqlite3 from 'sqlite3';
import { open, Database } from 'sqlite';
import rateLimit from 'express-rate-limit';
import helmet from 'helmet';
import path from 'path';

class CheckmateAPIGateway {
  private app = express();
  private httpServer = createServer(this.app);
  private io = new SocketServer(this.httpServer, {
    cors: { origin: "http://localhost:3000" }
  });
  private db: Database | null = null;

  constructor(private dbPath: string) {
    this.setupMiddleware();
    this.setupRoutes();
    this.setupWebSocket();
    this.initDatabase();
  }

  private setupMiddleware() {
    this.app.use(helmet());
    const limiter = rateLimit({ windowMs: 15 * 60 * 1000, max: 100 });
    this.app.use('/api/', limiter);
    this.app.use(cors({ origin: "http://localhost:3000" }));
    this.app.use(express.json());
  }

  private async initDatabase() {
    try {
      this.db = await open({ filename: this.dbPath, driver: sqlite3.Database, mode: sqlite3.OPEN_READONLY });
      console.log('✅ Database connection established');
      this.startChangePolling();
    } catch (error) {
      console.error('❌ Database connection failed:', error);
      process.exit(1);
    }
  }

  private setupRoutes() {
    this.app.get('/api/races/qualified', this.handleGetQualifiedRaces.bind(this));
    this.app.use(this.errorHandler.bind(this));
  }

  private async handleGetQualifiedRaces(req: Request, res: Response, next: NextFunction) {
    try {
      if (!this.db) throw new Error('Database not initialized');
      const races = await this.db.all(`
        SELECT * FROM live_races WHERE qualified = 1 ORDER BY checkmate_score DESC, post_time ASC LIMIT 50
      `);
      res.json({ success: true, data: races, timestamp: new Date().toISOString() });
    } catch (error) { next(error); }
  }

  private setupWebSocket() {
    this.io.on('connection', (socket) => {
      console.log(`🔌 Client connected: ${socket.id}`);
      socket.on('disconnect', () => { console.log(`🔌 Client disconnected: ${socket.id}`); });
    });
  }

  private startChangePolling() {
    let lastEventId = 0;
    setInterval(async () => {
      if (!this.db) return;
      try {
        const newEvent = await this.db.get('SELECT event_id FROM events WHERE event_id > ? ORDER BY event_id DESC LIMIT 1', lastEventId);
        if (newEvent) {
          console.log(`New event detected (ID: ${newEvent.event_id}). Broadcasting updates.`);
          const updatedRaces = await this.db.all(`SELECT * FROM live_races WHERE qualified = 1 ORDER BY checkmate_score DESC`);
          this.io.emit('races:updated', { payload: updatedRaces });
          lastEventId = newEvent.event_id;
        }
      } catch (error) { console.error('Polling error:', error); }
    }, 5000);
  }

  private errorHandler(error: Error, req: Request, res: Response, next: NextFunction) {
    console.error('API Error:', error);
    res.status(500).json({ success: false, error: error.message || 'Internal server error', timestamp: new Date().toISOString() });
  }

  public start(port: number) {
    this.httpServer.listen(port, () => { console.log(`🚀 API Gateway running on port ${port}`); });
  }
}

const dbPath = path.resolve(__dirname, '..', '..', 'shared_database', 'races.db');
const gateway = new CheckmateAPIGateway(dbPath);
gateway.start(parseInt(process.env.PORT || '8080'));