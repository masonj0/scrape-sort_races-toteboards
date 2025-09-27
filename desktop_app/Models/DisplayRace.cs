// desktop_app/Models/DisplayRace.cs
using System;
using System.ComponentModel;
using System.Windows.Media;

namespace desktop_app.Models
{
    public class DisplayRace : INotifyPropertyChanged
    {
        public string RaceId { get; set; }
        public string TrackName { get; set; }
        public int RaceNumber { get; set; }
        public DateTime PostTime { get; set; }
        public double CheckmateScore { get; set; }

        public string DisplayTitle => $"{TrackName} - Race {RaceNumber}";
        public string PostTimeCountdown => (PostTime - DateTime.Now).TotalMinutes > 0 ? $"{(int)(PostTime - DateTime.Now).TotalMinutes}m to post" : "At Post";
        public Brush ScoreGradient => CheckmateScore >= 90 ? Brushes.Gold : CheckmateScore >= 80 ? Brushes.OrangeRed : Brushes.DodgerBlue;

        public event PropertyChangedEventHandler PropertyChanged;
    }
}