using System;
using System.ComponentModel;
using System.Windows.Media;

namespace CheckmateDeck.Models
{
    public class DisplayRace : INotifyPropertyChanged
    {
        public string RaceId { get; set; }
        public string TrackName { get; set; }
        public int RaceNumber { get; set; }
        public DateTime PostTime { get; set; }
        public double CheckmateScore { get; set; }

        public string DisplayTitle => $"{TrackName} - Race {RaceNumber}";
        public Brush ScoreColor => CheckmateScore >= 85 ? Brushes.Gold : Brushes.SkyBlue;

        public event PropertyChangedEventHandler? PropertyChanged;
    }
}