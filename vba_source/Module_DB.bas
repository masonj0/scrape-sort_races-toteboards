Option Explicit

' ==============================================================================
' == Checkmate V8 - Excel VBA Database Module (COMPLETE)
' ==============================================================================

Private Const ODBC_DRIVER As String = "SQLite3 ODBC Driver"

' Data structure for race information
Public Type RaceData
    RaceID As String
    TrackName As String
    RaceNumber As Integer
    CheckmateScore As Double
End Type

' --- GetDatabaseConnection function ---
' Reads the database path from the CHECKMATE_DB_PATH environment variable.
Public Function GetDatabaseConnection() As ADODB.Connection
    On Error GoTo ErrorHandler

    Dim dbPath As String
    dbPath = Environ("CHECKMATE_DB_PATH")

    If dbPath = "" Then
        MsgBox "CRITICAL ERROR: The CHECKMATE_DB_PATH environment variable is not set." & vbCrLf & vbCrLf & _
               "Please ensure the .env file is configured and the Python service has been run at least once.", vbCritical, "Configuration Error"
        Set GetDatabaseConnection = Nothing
        Exit Function
    End If

    Dim conn As ADODB.Connection
    Set conn = New ADODB.Connection

    Dim connStr As String
    connStr = "Driver={SQLite3 ODBC Driver};Database=" & dbPath & ";SyncPragma=NORMAL;"

    conn.Open connStr
    Set GetDatabaseConnection = conn
    Exit Function

ErrorHandler:
    MsgBox "Failed to connect to database: " & Err.Description, vbCritical, "Database Connection Failed"
    Set GetDatabaseConnection = Nothing
End Function

' --- COMPLETE IMPLEMENTATION ---
' Fetch live qualified races from the database view
Public Function FetchLiveRaces() As Collection
    On Error GoTo ErrorHandler

    Dim conn As ADODB.Connection
    Set conn = GetDatabaseConnection()
    If conn Is Nothing Then Exit Function

    Dim rs As ADODB.Recordset
    Set rs = New ADODB.Recordset

    Dim races As Collection
    Set races = New Collection

    Dim sql As String
    sql = "SELECT race_id, track_name, race_number, checkmate_score FROM qualified_races"

    rs.Open sql, conn, adOpenStatic, adLockReadOnly

    While Not rs.EOF
        Dim race As RaceData
        race.RaceID = rs.Fields("race_id").Value
        race.TrackName = rs.Fields("track_name").Value
        race.RaceNumber = rs.Fields("race_number").Value
        race.CheckmateScore = rs.Fields("checkmate_score").Value
        races.Add race
        rs.MoveNext
    Wend

    Set FetchLiveRaces = races

ExitFunction:
    If Not rs Is Nothing Then rs.Close
    If Not conn Is Nothing Then conn.Close
    Exit Function

ErrorHandler:
    MsgBox "Failed to fetch live races: " & Err.Description, vbCritical
    Set FetchLiveRaces = Nothing
    GoTo ExitFunction
End Function

' --- COMPLETE IMPLEMENTATION ---
' Update a race's score or notes in the database
Public Sub UpdateRaceInDatabase(raceID As String, newScore As Double)
    On Error GoTo ErrorHandler

    Dim conn As ADODB.Connection
    Set conn = GetDatabaseConnection()
    If conn Is Nothing Then Exit Sub

    Dim cmd As ADODB.Command
    Set cmd = New ADODB.Command
    cmd.ActiveConnection = conn
    cmd.CommandText = "UPDATE live_races SET checkmate_score = ? WHERE race_id = ?"

    cmd.Parameters.Append cmd.CreateParameter("@score", adDouble, adParamInput, , newScore)
    cmd.Parameters.Append cmd.CreateParameter("@id", adVarChar, adParamInput, 100, raceID)

    cmd.Execute

    conn.Close
    MsgBox "Race " & raceID & " updated successfully!", vbInformation

ExitSub:
    Exit Sub

ErrorHandler:
    MsgBox "Failed to update race: " & Err.Description, vbCritical
    If Not conn Is Nothing Then conn.Close
End Sub