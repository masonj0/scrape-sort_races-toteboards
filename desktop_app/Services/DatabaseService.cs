using System.Collections.Generic;
using System.Threading.Tasks;
using System.Data.SQLite;
using System.IO;
using System;
using CheckmateDeck.Models;

namespace CheckmateDeck.Services
{
    public class DatabaseService
    {
        private readonly string _connectionString;

        public DatabaseService()
        {
            string dbPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "..", "..", "..", "shared_database", "races.db");
            _connectionString = $"Data Source={dbPath};Version=3;Read Only=True;";
        }

        public async Task<List<DisplayRace>> GetQualifiedRacesAsync()
        {
            var races = new List<DisplayRace>();
            using (var connection = new SQLiteConnection(_connectionString))
            {
                await connection.OpenAsync();
                var command = new SQLiteCommand("""
                    SELECT race_id, track_name, race_number, post_time, checkmate_score
                    FROM live_races
                    WHERE qualified = 1 AND post_time > datetime('now')
                    ORDER BY checkmate_score DESC LIMIT 50
                """, connection);

                using (var reader = await command.ExecuteReaderAsync())
                {
                    while (await reader.ReadAsync())
                    {
                        races.Add(new DisplayRace
                        {
                            RaceId = reader.GetString(0),
                            TrackName = reader.GetString(1),
                            RaceNumber = reader.GetInt32(2),
                            PostTime = reader.GetDateTime(3),
                            CheckmateScore = reader.GetDouble(4)
                        });
                    }
                }
            }
            return races;
        }

        public async Task<List<AdapterStatusDisplay>> GetAdapterStatusesAsync()
        {
            var statuses = new List<AdapterStatusDisplay>();
             using (var connection = new SQLiteConnection(_connectionString))
            {
                await connection.OpenAsync();
                var command = new SQLiteCommand("SELECT adapter_name, status, last_run, races_found FROM adapter_status ORDER BY last_run DESC", connection);
                using (var reader = await command.ExecuteReaderAsync())
                {
                    while (await reader.ReadAsync())
                    {
                        statuses.Add(new AdapterStatusDisplay
                        {
                            AdapterName = reader.GetString(0),
                            Status = reader.GetString(1),
                            LastRun = reader.GetDateTime(2),
                            RacesFound = reader.GetInt32(3)
                        });
                    }
                }
            }
            return statuses;
        }
    }
}