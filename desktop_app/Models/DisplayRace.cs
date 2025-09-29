using System;
using System.ComponentModel;
using System.Runtime.CompilerServices;
using System.Windows.Media;

namespace CheckmateDeck.Models
{
    public class DisplayRace : INotifyPropertyChanged
    {
        private string _raceId;
        public string RaceId
        {
            get => _raceId;
            set { _raceId = value; OnPropertyChanged(); }
        }

        private string _trackName;
        public string TrackName
        {
            get => _trackName;
            set { _trackName = value; OnPropertyChanged(); OnPropertyChanged(nameof(DisplayTitle)); }
        }

        private int _raceNumber;
        public int RaceNumber
        {
            get => _raceNumber;
            set { _raceNumber = value; OnPropertyChanged(); OnPropertyChanged(nameof(DisplayTitle)); }
        }

        private DateTime _postTime;
        public DateTime PostTime
        {
            get => _postTime;
            set { _postTime = value; OnPropertyChanged(); }
        }

        private double _checkmateScore;
        public double CheckmateScore
        {
            get => _checkmateScore;
            set
            {
                if (_checkmateScore != value)
                {
                    _checkmateScore = value;
                    OnPropertyChanged();
                    OnPropertyChanged(nameof(ScoreColor));
                }
            }
        }

        public string DisplayTitle => $"{TrackName} - Race {RaceNumber}";
        public Brush ScoreColor => CheckmateScore >= 85 ? Brushes.Gold : Brushes.SkyBlue;

        public event PropertyChangedEventHandler? PropertyChanged;

        protected virtual void OnPropertyChanged([CallerMemberName] string propertyName = null)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }
    }
}