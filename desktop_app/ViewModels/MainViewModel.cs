using System.ComponentModel;

namespace CheckmateDeck.ViewModels
{
    public class MainViewModel : INotifyPropertyChanged
    {
        private string _statusText = "Command Deck Initializing...";
        public string StatusText
        {
            get => _statusText;
            set
            {
                _statusText = value;
                OnPropertyChanged(nameof(StatusText));
            }
        }

        public MainViewModel()
        {
            StatusText = "Command Deck Online.";
        }

        public event PropertyChangedEventHandler? PropertyChanged;
        protected virtual void OnPropertyChanged(string propertyName)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }
    }
}