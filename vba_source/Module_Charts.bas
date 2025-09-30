Option Explicit
Public Sub CreateScoreChart()
    Dim ws As Worksheet, chartObj As ChartObject, dataSource As Range, lastRow As Long
    Set ws = ThisWorkbook.Sheets("Dashboard")
    On Error Resume Next
    ws.ChartObjects("ScoreDistributionChart").Delete
    On Error GoTo 0
    lastRow = ws.Cells(ws.Rows.Count, 4).End(xlUp).row
    If lastRow < 7 Then Exit Sub
    Set dataSource = ws.Range("D7:D" & lastRow)
    Set chartObj = ws.ChartObjects.Add(Left:=ws.Range("G7").Left, Top:=ws.Range("G7").Top, Width:=450, Height:=250)
    chartObj.Name = "ScoreDistributionChart"
    With chartObj.Chart
        .ChartType = xlColumnClustered: .SetSourceData Source:=dataSource
        .HasTitle = True: .ChartTitle.Text = "Checkmate Score Distribution"
        .HasLegend = False: .Axes(xlCategory).HasTitle = True
        .Axes(xlCategory).AxisTitle.Text = "Races": .Axes(xlValue).HasTitle = True
        .Axes(xlValue).AxisTitle.Text = "Checkmate Score"
    End With
End Sub