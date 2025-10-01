Option Explicit
Public Type RaceData
    RaceID As String
    TrackName As String
    RaceNumber As Integer
    CheckmateScore As Double
    RawJSON As String
End Type
Public Sub SetupWorkbookUI()
    Dim ws As Worksheet, btn As Button
    Set ws = Sheets("Dashboard"): ws.Cells.Clear
    ws.Range("A1").Value = "Checkmate Live Racing Dashboard": ws.Range("A1").Font.Size = 16: ws.Range("A1").Font.Bold = True
    ws.Range("A3").Value = "Database Status:": ws.Range("B3").Value = "Not Connected"
    Set btn = ws.Buttons.Add(100, 60, 120, 30): btn.Text = "Connect & Load Races": btn.OnAction = "LoadRacesFromDB"
    Set btn = ws.Buttons.Add(250, 60, 120, 30): btn.Text = "Auto-Refresh (30s)": btn.OnAction = "StartAutoRefresh"
    ws.Range("A6:E6").Value = Array("Race ID", "Track", "Race #", "Checkmate Score", "Actions"): ws.Range("A6:E6").Font.Bold = True
    ws.Columns.AutoFit
End Sub
Public Sub LoadRacesFromDB()
    Dim ws As Worksheet, races As Collection, race As RaceData, row As Long
    Set ws = Sheets("Dashboard"): Set races = FetchLiveRaces
    If races Is Nothing Or races.Count = 0 Then
        MsgBox "No live qualified races found.", vbExclamation: ws.Range("B3").Value = "Connected - No Data": Exit Sub
    End If
    ws.Range("B3").Value = "Connected - " & races.Count & " Races Found"
    ws.Range("A7:E" & ws.Rows.Count).ClearContents: row = 7
    For Each race In races
        ws.Cells(row, 1) = race.RaceID: ws.Cells(row, 2) = race.TrackName
        ws.Cells(row, 3) = race.RaceNumber: ws.Cells(row, 4) = race.CheckmateScore
        ws.Hyperlinks.Add Anchor:=ws.Cells(row, 5), Address:="", SubAddress:="'" & ws.Name & "'!A" & row, TextToDisplay:="View Details"
        row = row + 1
    Next
    ws.Columns.AutoFit: Call CreateScoreChart
End Sub
Public Sub Worksheet_FollowHyperlink(ByVal Target As Hyperlink)
    Dim raceID As String, detailsSheet As Worksheet
    Set detailsSheet = ThisWorkbook.Sheets("RaceDetails")
    raceID = detailsSheet.Cells(Target.Range.row, 1).Value
    detailsSheet.Cells.Clear: detailsSheet.Range("A1").Value = "Details for Race ID:": detailsSheet.Range("B1").Value = raceID
    detailsSheet.Range("A3").Value = "(Full JSON data would be displayed here.)": detailsSheet.Activate
End Sub
Public Sub StartAutoRefresh()
    Application.OnTime Now + TimeValue("00:00:30"), "LoadRacesFromDB", Schedule:=True
    MsgBox "Auto-refresh enabled.", vbInformation
End Sub
Private Sub Workbook_Open()
    Call SetupWorkbookUI
End Sub