// desktop_app/Services/DatabaseService.cs
using System.Collections.Generic;
using System.Threading.Tasks;
using desktop_app.Models;
using System;

public class DatabaseService
{
    public async Task<List<DisplayRace>> GetQualifiedRacesAsync()
    {
        // Return mock data for now
        await Task.Delay(100); // Simulate async database call
        return new List<DisplayRace>
        {
            new DisplayRace { RaceId = "mock1", TrackName = "Santa Anita", RaceNumber = 3, PostTime = DateTime.Now.AddMinutes(30), CheckmateScore = 92.1 },
            new DisplayRace { RaceId = "mock2", TrackName = "Belmont Park", RaceNumber = 7, PostTime = DateTime.Now.AddMinutes(45), CheckmateScore = 88.5 },
            new DisplayRace { RaceId = "mock3", TrackName = "Churchill Downs", RaceNumber = 4, PostTime = DateTime.Now.AddMinutes(55), CheckmateScore = 76.3 },
        };
    }
}