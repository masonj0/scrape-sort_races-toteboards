using System;
using System.Collections.Generic;
using System.Data.SQLite;
using System.IO;
using System.Text.Json;
using System.Threading.Tasks;
using CheckmateDeck.Models;

namespace CheckmateDeck.Services
{
    public class DatabaseService : IDatabaseService
    {
        private readonly string _connectionString;

        public DatabaseService()
        {
            // A simple config loader. Can be replaced with a more robust library later.
            string configJson = File.ReadAllText("app_config.json");
            using (JsonDocument configDoc = JsonDocument.Parse(configJson))
            {
                string relativeDbPath = configDoc.RootElement.GetProperty("DatabasePath").GetString();
                string absoluteDbPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, relativeDbPath);
                _connectionString = $"Data Source={absoluteDbPath};Version=3;Read Only=True;";
            }
        }

        public async Task<List<DisplayRace>> GetQualifiedRacesAsync()
        {
            var races = new List<DisplayRace>();
            try
            {
                await using (var connection = new SQLiteConnection(_connectionString))
                {
                    await connection.OpenAsync();
                    var command = new SQLiteCommand("SELECT race_id, track_name, race_number, post_time, checkmate_score FROM qualified_races ORDER BY post_time ASC", connection);
                    await using (var reader = await command.ExecuteReaderAsync())
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
            }
            catch (Exception ex) // Catch SQLiteException or base Exception
            {
                // Replace with a proper logging mechanism
                Console.WriteLine($"[ERROR] Failed to get qualified races: {ex.Message}");
            }
            return races;
        }

        public async Task<List<AdapterStatusDisplay>> GetAdapterStatusesAsync()
        {
            var statuses = new List<AdapterStatusDisplay>();
            try
            {
                await using (var connection = new SQLiteConnection(_connectionString))
                {
                    await connection.OpenAsync();
                    var command = new SQLiteCommand("SELECT adapter_name, status, last_run, races_found FROM adapter_status ORDER BY last_run DESC", connection);
                    await using (var reader = await command.ExecuteReaderAsync())
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
            }
            catch (Exception ex)
            {
                // Replace with a proper logging mechanism
                Console.WriteLine($"[ERROR] Failed to get adapter statuses: {ex.Message}");
            }
            return statuses;
        }
    }
}