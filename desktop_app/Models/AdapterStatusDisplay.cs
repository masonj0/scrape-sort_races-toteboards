using System;
using System.ComponentModel;
using System.Windows.Media;

namespace CheckmateDeck.Models
{
    public class AdapterStatusDisplay : INotifyPropertyChanged
    {
        public string AdapterName { get; set; }
        public string Status { get; set; }
        public DateTime LastRun { get; set; }
        public int RacesFound { get; set; }

        public Brush StatusColor => Status == "OK" ? Brushes.LimeGreen : Brushes.Crimson;
        public string LastRunFormatted => LastRun.ToString("HH:mm:ss");

        public event PropertyChangedEventHandler? PropertyChanged;
    }
}