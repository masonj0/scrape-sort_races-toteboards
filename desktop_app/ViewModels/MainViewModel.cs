using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Threading;
using System;
using CheckmateDeck.Models;
using CheckmateDeck.Services;

namespace CheckmateDeck.ViewModels
{
    public class MainViewModel : INotifyPropertyChanged
    {
        private readonly DatabaseService _dbService;
        private readonly DispatcherTimer _refreshTimer;

        public ObservableCollection<DisplayRace> QualifiedRaces { get; set; }
        public ObservableCollection<AdapterStatusDisplay> AdapterStatuses { get; set; }

        public MainViewModel()
        {
            _dbService = new DatabaseService();
            QualifiedRaces = new ObservableCollection<DisplayRace>();
            AdapterStatuses = new ObservableCollection<AdapterStatusDisplay>();

            Task.Run(() => RefreshDataAsync());

            _refreshTimer = new DispatcherTimer();
            _refreshTimer.Interval = TimeSpan.FromSeconds(15);
            _refreshTimer.Tick += async (s, e) => await RefreshDataAsync();
            _refreshTimer.Start();
        }

        private async Task RefreshDataAsync()
        {
            var races = await _dbService.GetQualifiedRacesAsync();
            var statuses = await _dbService.GetAdapterStatusesAsync();

            Application.Current.Dispatcher.Invoke(() =>
            {
                QualifiedRaces.Clear();
                foreach (var race in races) QualifiedRaces.Add(race);

                AdapterStatuses.Clear();
                foreach (var status in statuses) AdapterStatuses.Add(status);
            });
        }

        public event PropertyChangedEventHandler? PropertyChanged;
    }
}