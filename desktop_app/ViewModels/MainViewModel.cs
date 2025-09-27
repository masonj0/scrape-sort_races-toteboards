// desktop_app/ViewModels/MainViewModel.cs
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Threading.Tasks;
using System.Windows;
using desktop_app.Models;
using desktop_app.Services;

public class MainViewModel : INotifyPropertyChanged
{
    private readonly DatabaseService _dbService;
    public ObservableCollection<DisplayRace> QualifiedRaces { get; set; }

    public MainViewModel()
    {
        _dbService = new DatabaseService();
        QualifiedRaces = new ObservableCollection<DisplayRace>();
        // Load data when the ViewModel is created
        LoadDataAsync();
    }

    private async Task LoadDataAsync()
    {
        var races = await _dbService.GetQualifiedRacesAsync();
        Application.Current.Dispatcher.Invoke(() =>
        {
            QualifiedRaces.Clear();
            foreach (var race in races)
            {
                QualifiedRaces.Add(race);
            }
        });
    }

    public event PropertyChangedEventHandler PropertyChanged;

    // Helper method to raise the PropertyChanged event
    protected virtual void OnPropertyChanged(string propertyName)
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }
}