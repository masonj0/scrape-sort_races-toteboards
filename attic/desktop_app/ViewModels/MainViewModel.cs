using System;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Linq;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Threading;
using CheckmateDeck.Models;
using CheckmateDeck.Services;

namespace CheckmateDeck.ViewModels
{
    public class MainViewModel : INotifyPropertyChanged
    {
        private readonly IDatabaseService _dbService; // Program to the interface
        private readonly DispatcherTimer _timer;

        public ObservableCollection<DisplayRace> QualifiedRaces { get; set; }
        public ObservableCollection<AdapterStatusDisplay> AdapterStatuses { get; set; }

        // Inject the dependency via the constructor
        public MainViewModel(IDatabaseService dbService)
        {
            _dbService = dbService; // No more "new DatabaseService()"
            QualifiedRaces = new ObservableCollection<DisplayRace>();
            AdapterStatuses = new ObservableCollection<AdapterStatusDisplay>();
            _timer = new DispatcherTimer
            {
                Interval = TimeSpan.FromSeconds(15)
            };
            _timer.Tick += async (sender, e) => await RefreshDataAsync();
            _timer.Start();
            Task.Run(async () => await RefreshDataAsync());
        }

        private async Task RefreshDataAsync()
        {
            var races = await _dbService.GetQualifiedRacesAsync();
            var statuses = await _dbService.GetAdapterStatusesAsync();

            // Ensure UI updates happen on the main dispatcher thread
            Application.Current.Dispatcher.Invoke(() =>
            {
                // --- Granular Update for Races ---
                var racesToRemove = QualifiedRaces.Where(qr => !races.Any(r => r.RaceId == qr.RaceId)).ToList();
                foreach (var race in racesToRemove) QualifiedRaces.Remove(race);

                foreach (var race in races)
                {
                    var existingRace = QualifiedRaces.FirstOrDefault(r => r.RaceId == race.RaceId);
                    if (existingRace != null)
                    {
                        // Update properties on existing object for a seamless refresh
                        existingRace.CheckmateScore = race.CheckmateScore;
                    }
                    else
                    {
                        QualifiedRaces.Add(race);
                    }
                }

                // --- Simple Replace for Statuses (often less performance-critical) ---
                AdapterStatuses.Clear();
                foreach (var status in statuses) AdapterStatuses.Add(status);
            });
        }

        public event PropertyChangedEventHandler? PropertyChanged;
    }
}