// desktop_app/Services/DatabaseService.cs
using System;
using System.Collections.Generic;
using System.Data.SQLite;
using System.IO;
using System.Threading.Tasks;
using desktop_app.Models;

namespace desktop_app.Services
{
    public class DatabaseService
    {
        private readonly string _connectionString;

        public DatabaseService()
        {
            // Construct a robust, absolute path to the shared database from the executable's location.
            string dbPath = Path.GetFullPath(Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "..", "..", "..", "shared_database", "races.db"));
            _connectionString = $"Data Source={dbPath};Version=3;";
        }

        public async Task<List<DisplayRace>> GetQualifiedRacesAsync()
        {
            var races = new List<DisplayRace>();
            using (var connection = new SQLiteConnection(_connectionString))
            {
                await connection.OpenAsync();
                var command = new SQLiteCommand(
                    "SELECT race_id, track_name, race_number, post_time, checkmate_score " +
                    "FROM live_races " +
                    "WHERE qualified = 1 AND post_time > datetime('now') " +
                    "ORDER BY checkmate_score DESC", connection);

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
                var command = new SQLiteCommand(
                    "SELECT adapter_name, status, last_run, races_found " +
                    "FROM adapter_status " +
                    "ORDER BY adapter_name", connection);

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