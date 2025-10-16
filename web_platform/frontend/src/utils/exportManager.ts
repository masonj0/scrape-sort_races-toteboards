// web_platform/frontend/src/utils/exportManager.ts
import { saveAs } from 'file-saver';
import * as XLSX from 'xlsx';

// Define a more specific type for the race data we expect
interface RaceToExport {
  venue: string;
  race_number: number;
  start_time: string;
  qualification_score?: number;
  runners: { scratched: boolean }[];
  source: string;
}

export class ExportManager {
  static exportToExcel(races: RaceToExport[], filename: string = 'fortuna_races') {
    const workbook = XLSX.utils.book_new();

    // --- Summary Sheet ---
    const summaryData = [
      ['Total Qualified Races', races.length],
      ['Report Generated At', new Date().toLocaleString()]
    ];
    const summarySheet = XLSX.utils.aoa_to_sheet(summaryData);
    XLSX.utils.book_append_sheet(workbook, summarySheet, 'Summary');

    // --- Race Data Sheet ---
    const raceData = races.map(race => ({
      'Venue': race.venue,
      'Race Number': race.race_number,
      'Post Time': new Date(race.start_time).toLocaleString(),
      'Qualification Score': race.qualification_score || 0,
      'Field Size': race.runners.filter(r => !r.scratched).length,
      'Source': race.source
    }));
    const raceSheet = XLSX.utils.json_to_sheet(raceData);
    XLSX.utils.book_append_sheet(workbook, raceSheet, 'Races');

    // --- Save the file ---
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    XLSX.writeFile(workbook, `${filename}_${timestamp}.xlsx`);
  }
}