// desktop_app/Models/DisplayRace.cs
using System.ComponentModel;
using System.Windows.Media;
using System;

public class DisplayRace : INotifyPropertyChanged
{
    public string RaceId { get; set; }
    public string TrackName { get; set; }
    public int RaceNumber { get; set; }
    public DateTime PostTime { get; set; }
    public double CheckmateScore { get; set; }

    // Example of a computed property for data binding
    public string DisplayTitle => $"{TrackName} - Race {RaceNumber}";
    public Brush ScoreColor => CheckmateScore >= 85 ? Brushes.Crimson : Brushes.Orange;

    public event PropertyChangedEventHandler PropertyChanged;

    // Helper method to raise the PropertyChanged event
    protected virtual void OnPropertyChanged(string propertyName)
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }
}