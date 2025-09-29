Option Explicit

' ==============================================================================
' == Checkmate V8 - Excel VBA Database Module
' ==============================================================================

' --- CONFIGURATION PROTOCOL NOTE ---
' The DB_PATH is a fixed path for simplicity. A more robust solution
' would read this path from an external configuration file.
'
Private Const DB_PATH As String = "C:\YourProjectPath\shared_database\races.db"
Private Const ODBC_DRIVER As String = "SQLite3-64 ODBC Driver"

Public Function GetDatabaseConnection() As ADODB.Connection
    ' Implementation as defined in the sanctioned proposal...
End Function