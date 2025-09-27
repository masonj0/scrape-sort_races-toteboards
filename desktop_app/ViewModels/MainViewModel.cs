// desktop_app/ViewModels/MainViewModel.cs
using System;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Threading;
using desktop_app.Models;
using desktop_app.Services;

namespace desktop_app.ViewModels
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

            // Initial data load
            RefreshDataAsync();

            // Set up a timer to refresh data every 15 seconds
            _refreshTimer = new DispatcherTimer();
            _refreshTimer.Interval = TimeSpan.FromSeconds(15);
            _refreshTimer.Tick += async (s, e) => await RefreshDataAsync();
            _refreshTimer.Start();
        }

        private async Task RefreshDataAsync()
        {
            try
            {
                var races = await _dbService.GetQualifiedRacesAsync();
                var statuses = await _dbService.GetAdapterStatusesAsync();

                Application.Current.Dispatcher.Invoke(() =>
                {
                    // Smart update for races
                    QualifiedRaces.Clear(); // Simple clear/add for now
                    foreach (var race in races) QualifiedRaces.Add(race);

                    // Smart update for statuses
                    AdapterStatuses.Clear();
                    foreach (var status in statuses) AdapterStatuses.Add(status);
                });
            }
            catch (Exception ex)
            {
                // In a real app, you'd log this to a file or service
                MessageBox.Show($"Failed to refresh data: {ex.Message}", "Database Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        public event PropertyChangedEventHandler PropertyChanged;

        protected virtual void OnPropertyChanged(string propertyName)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }
    }
}