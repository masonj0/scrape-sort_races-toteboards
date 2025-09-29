using System;
using System.ComponentModel;
using System.Runtime.CompilerServices;
using System.Windows.Media;

namespace CheckmateDeck.Models
{
    public class AdapterStatusDisplay : INotifyPropertyChanged
    {
        private string _adapterName;
        public string AdapterName
        {
            get => _adapterName;
            set { _adapterName = value; OnPropertyChanged(); }
        }

        private string _status;
        public string Status
        {
            get => _status;
            set
            {
                if (_status != value)
                {
                    _status = value;
                    OnPropertyChanged();
                    OnPropertyChanged(nameof(StatusColor));
                }
            }
        }

        private DateTime _lastRun;
        public DateTime LastRun
        {
            get => _lastRun;
            set
            {
                if (_lastRun != value)
                {
                    _lastRun = value;
                    OnPropertyChanged();
                    OnPropertyChanged(nameof(LastRunFormatted));
                }
            }
        }

        private int _racesFound;
        public int RacesFound
        {
            get => _racesFound;
            set { _racesFound = value; OnPropertyChanged(); }
        }

        public Brush StatusColor => Status == "OK" ? Brushes.LimeGreen : Brushes.Crimson;
        public string LastRunFormatted => LastRun.ToString("HH:mm:ss");

        public event PropertyChangedEventHandler? PropertyChanged;

        protected virtual void OnPropertyChanged([CallerMemberName] string propertyName = null)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }
    }
}