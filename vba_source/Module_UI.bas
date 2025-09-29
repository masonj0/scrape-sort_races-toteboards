Option Explicit

' ==============================================================================
' == Checkmate V8 - Excel VBA User Interface Module
' ==============================================================================

Public Type RaceData
    RaceID As String
    TrackName As String
    RaceNumber As Integer
    CheckmateScore As Double
    RawJSON As String
End Type

Public Sub SetupWorkbookUI()
    ' Implementation as defined in the sanctioned proposal...
End Sub

Private Sub Workbook_Open()
    Call SetupWorkbookUI
End Sub