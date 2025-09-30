import sqlite3 from 'sqlite3';
import { open, Database } from 'sqlite';
import path from 'path';

export class DatabaseService {
  private db: Database | null = null;

  private async getDb(): Promise<Database> {
    if (!this.db) {
      // This path assumes the service is run from the project root.
      const dbPath = process.env.CHECKMATE_DB_PATH || path.join(__dirname, '../../../../shared_database/races.db');
      this.db = await open({
        filename: dbPath,
        driver: sqlite3.Database
      });
    }
    return this.db;
  }

  async getQualifiedRaces(): Promise<any[]> {
    const db = await this.getDb();
    return db.all(`SELECT * FROM qualified_races`);
  }
}