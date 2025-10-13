// web_platform/frontend/src/utils/exportManager.ts
import { saveAs } from 'file-saver';
import * as XLSX from 'xlsx';

export class ExportManager {
  static exportToExcel(races: any[], filename: string = 'fortuna_races') {
    const workbook = XLSX.utils.book_new();

    const summaryData = [
      ['Total Qualified Races', races.length],
      ['Generated At', new Date().toLocaleString()]
    ];
    const summarySheet = XLSX.utils.aoa_to_sheet(summaryData);
    XLSX.utils.book_append_sheet(workbook, summarySheet, 'Summary');

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

    XLSX.writeFile(workbook, `${filename}_${Date.now()}.xlsx`);
  }
}
