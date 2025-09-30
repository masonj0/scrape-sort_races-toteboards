Option Explicit

' ==============================================================================
' == Checkmate V8 - Excel VBA Database Module
' == This module now reads the database path from the CHECKMATE_DB_PATH
' == environment variable, establishing a single source of truth.
' ==============================================================================

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