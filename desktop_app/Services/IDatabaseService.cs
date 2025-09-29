using System.Collections.Generic;
using System.Threading.Tasks;
using CheckmateDeck.Models;

public interface IDatabaseService
{
    Task<List<DisplayRace>> GetQualifiedRacesAsync();
    Task<List<AdapterStatusDisplay>> GetAdapterStatusesAsync();
}