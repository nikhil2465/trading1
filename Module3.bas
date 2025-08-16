Attribute VB_Name = "Module3"
Sub CA_Dayanand_Bongale_Mobile_6362985767()
    Rows("1:1").Delete Shift:=xlUp
    Columns("A:A").Delete Shift:=xlToLeft
    Columns("D:J").Delete Shift:=xlToLeft
    Columns("E:K").Delete Shift:=xlToLeft

    Dim rng As Range
    Dim col As Range

    Set rng = Union(Range("A:A"), Range("B:B"), Range("C:C"), Range("E:E"), Range("F:F"), Range("G:G"))
   
    ' Format all values to decimal 0.00 format
    Set rng = ActiveSheet.UsedRange ' Adjust this if you want to limit the range
    rng.NumberFormat = "0.00"
   
        ' Remove commas from the values
    rng.Replace What:=",", Replacement:="", LookAt:=xlPart, SearchOrder:=xlByRows, MatchCase:=False, SearchFormat:=False, ReplaceFormat:=False


    For Each col In rng.Columns
        col.FormatConditions.AddTop10
        With col.FormatConditions(1)
            .SetFirstPriority
            .TopBottom = xlTop10Top
            .Rank = 3
            .Percent = False
        End With
        With col.FormatConditions(1).Interior
            .PatternColorIndex = xlAutomatic
            .Color = 13551615
            .TintAndShade = 0
        End With
        col.FormatConditions(1).StopIfTrue = False
    Next col

    Range("A:A").Copy
    Range("A:A").PasteSpecial Paste:=xlPasteFormats
    Application.CutCopyMode = False

    Range("B:B").Copy
    Range("B:B").PasteSpecial Paste:=xlPasteFormats
    Application.CutCopyMode = False

    Range("C:C").Copy
    Range("C:C").PasteSpecial Paste:=xlPasteFormats
    Application.CutCopyMode = False

    Range("E:E").Copy
    Range("E:E").PasteSpecial Paste:=xlPasteFormats
    Application.CutCopyMode = False

    Range("F:F").Copy
    Range("F:F").PasteSpecial Paste:=xlPasteFormats
    Application.CutCopyMode = False

    Range("G:G").Copy
    Range("G:G").PasteSpecial Paste:=xlPasteFormats
    Application.CutCopyMode = False

    Range("H1").Value = "PCR OI"
    Range("I1").Value = "PCR Volume"
    Range("J1").Value = "PCR Change in OI"
    Range("M1").Value = "CPR OI"
    Range("N1").Value = "CPR Vol"
    Range("O1").Value = "CPR Sum"
    Range("P1").Value = "Resistance"

    Range("H2").FormulaR1C1 = "=RC[-1]/RC[-7]"
    Range("I2").FormulaR1C1 = "=RC[-4]/RC[-6]"
   Range("J2").FormulaR1C1 = "=RC[-4]/RC[-8]"
Range("M2").FormulaR1C1 = "=RC[-12]/RC[-6]" ' A2 / G2
Range("N2").FormulaR1C1 = "=RC[-11]/RC[-9]"  ' C2 / E2
Range("O2").FormulaR1C1 = "=RC[-1]+RC[-2]"  ' M2 / N2

 
    Dim lastRow As Long
    lastRow = Range("A" & Rows.Count).End(xlUp).Row

    Range("H2").AutoFill Destination:=Range("H2:H" & lastRow)
    Range("I2").AutoFill Destination:=Range("I2:I" & lastRow)
   Range("J2").AutoFill Destination:=Range("J2:J" & lastRow)
    Range("M2").AutoFill Destination:=Range("M2:M" & lastRow)
    Range("N2").AutoFill Destination:=Range("N2:N" & lastRow)
    Range("O2").AutoFill Destination:=Range("O2:O" & lastRow)

    ' Range("H14").NumberFormat = "0.00"

    Range("H2:J" & lastRow).Copy
    Range("H2:J" & lastRow).PasteSpecial Paste:=xlPasteFormats
    Application.CutCopyMode = False

    Columns("B:B").EntireColumn.AutoFit
    Columns("C:C").ColumnWidth = 8.55
    Columns("F:F").EntireColumn.AutoFit
    Columns("I:I").EntireColumn.AutoFit
    Columns("J:J").EntireColumn.AutoFit
    Columns("P:P").EntireColumn.AutoFit

    With ActiveWindow
        .SplitColumn = 0
        .SplitRow = 1
    End With
    ActiveWindow.FreezePanes = True

    Range("H2:J" & lastRow).NumberFormat = "0.00"

    ' Add conditional formatting to highlight negative values in column J
    ' Range("J2:J" & lastRow).FormatConditions.Add(Type:=xlCellValue, Operator:=xlLess, Formula1:="0").Font.Color = RGB(255, 0, 0)
     ' Range("J3").Select
   
    Range("D1").Value = "Strike Price"
    Range("D:D").Interior.Color = RGB(255, 255, 0)
   
    ' Replace #VALUE! with "illiquid"
    On Error Resume Next
    Range("A:O").SpecialCells(xlCellTypeFormulas, xlErrors).Value = "illiquid"
    On Error GoTo 0
   
    ' Center align all values in the worksheet
    Cells.VerticalAlignment = xlCenter
    Cells.HorizontalAlignment = xlCenter
   
    ' Highlight values greater than 1 in column H with green color
    Dim rngH As Range
    Dim rngCell As Range
    Set rngH = Range("H2:H" & lastRow)
    For Each rngCell In rngH
        If rngCell.Value > 1 Then
            rngCell.Interior.Color = RGB(0, 255, 0)
        End If
    Next rngCell
   
' Sum values row-wise in columns H, I, and J and display the sum in a new column
Dim analysisColumn As Range
Dim i As Long

' Define the destination column for the sum values
Set analysisColumn = Range("K2:K" & lastRow)

' Perform the sum calculation row-wise
' For i = 2 To lastRow
  '  analysisColumn.Cells(i - 1).Value = WorksheetFunction.Sum(Range("H" & i & ":J" & i))
'Next i

' Perform the sum calculation row-wise for columns H to I (excluding column J)
For i = 2 To lastRow
    analysisColumn.Cells(i - 1).Value = WorksheetFunction.Sum(Range("H" & i & ":I" & i))
Next i


' Set the header for the analysis column
Range("K1").Value = "PCR Sum"

' Add a new column for the conditions
Dim supportColumn As Range

' Define the range for the support column
Set supportColumn = Range("L2:L" & lastRow)

' Apply conditions based on the values in column K
Dim rowIndex As Long
For rowIndex = 2 To lastRow
    Dim valueK As Double
    valueK = analysisColumn.Cells(rowIndex - 1).Value
   
    If valueK > 8 Then
        supportColumn.Cells(rowIndex - 1).Value = "Very Good Support"
    ElseIf valueK > 5 Then
        supportColumn.Cells(rowIndex - 1).Value = "Good Support"
    ElseIf valueK > 3 Then
        supportColumn.Cells(rowIndex - 1).Value = "Support"
    End If
Next rowIndex

' Apply conditions based on the values in column O and update column P
For rowIndex = 2 To lastRow
    Dim valueO As Variant
    valueO = Range("O" & rowIndex).Value
   
    If IsNumeric(valueO) Then
        If valueO > 6 Then
            Range("P" & rowIndex).Value = "Very Good Resistance"
        ElseIf valueO > 3 Then
            Range("P" & rowIndex).Value = "Resistance"
        Else
            Range("P" & rowIndex).Value = "" ' Clear the value if no condition is met
        End If
    End If
Next rowIndex



' Set the header for the support column
Range("L1").Value = "PCR Support"


' Auto-fit the width of the support column
supportColumn.EntireColumn.AutoFit


' Highlight values greater than 1 (excluding "illiquid") in column I with green color
Dim rngI As Range
Set rngI = Range("I2:I" & lastRow)

For Each rngCell In rngI
    If rngCell.Value > 1 And UCase(rngCell.Value) <> "ILLIQUID" Then
        rngCell.Interior.Color = RGB(0, 255, 0)
    End If
Next rngCell

  ' Hide columns B, F, and J
    Columns("B:B").Hidden = True
    Columns("F:F").Hidden = True
    Columns("J:J").Hidden = True

End Sub
