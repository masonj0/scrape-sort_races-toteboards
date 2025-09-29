using System.Windows;
using CheckmateDeck.Services;
using CheckmateDeck.ViewModels;

namespace CheckmateDeck.Views
{
    public partial class MainWindow : Window
    {
        public MainWindow()
        {
            InitializeComponent();
            IDatabaseService databaseService = new DatabaseService();
            DataContext = new MainViewModel(databaseService);
        }
    }
}