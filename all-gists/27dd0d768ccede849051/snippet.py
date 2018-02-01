"""
An example of using PyWin32 and the win32com library to interact
Microsoft Excel from Python. 

This can be used instead of Visual Basic for Applications (VBA)

(c) Michael Papasimeon
"""

import win32com.client
from win32com.client import constants

    # ExcelChart
    # Creates a Microsoft Excel Chart given a data range
    # and whole bunch of other parameters
class ExcelChart:
    def __init__(self, excel, workbook, chartname, afterSheet):
        self.chartname = chartname
        self.excel = excel
        self.workbook = workbook
        self.chartname = chartname
        self.afterSheet = afterSheet

    def SetTitle(self, chartTitle):
        self.chartTitle = chartTitle

    def SetType(self, chartType):
        self.chartType = chartType

    def SetSource(self, chartSource):
        self.chartSource = chartSource

    def SetPlotBy(self, plotBy):
        self.plotBy = plotBy

    def SetCategoryLabels(self, numCategoryLabels):
        self.numCategoryLabels = numCategoryLabels

    def SetSeriesLabels(self, numSeriesLabels):
        self.numSeriesLabels = numSeriesLabels

    def SetCategoryTitle(self, categoryTitle):
        self.categoryTitle = categoryTitle

    def SetValueTitle(self, valueTitle):
        self.valueTitle = valueTitle

    def CreateChart(self):
        self.chart = self.workbook.Charts.Add(After=self.afterSheet)
        self.chart.ChartWizard(Gallery=win32com.client.constants.xlColumn, \
                               CategoryLabels=1, \
                               SeriesLabels=1, \
                               CategoryTitle = self.categoryTitle, \
                               ValueTitle = self.valueTitle, \
                               PlotBy=self.plotBy, \
                               Title=self.chartTitle)
        self.chart.SetSourceData(self.chartSource, self.plotBy)
        self.chart.HasAxis = (constants.xlCategory, constants.xlPrimary)
        self.chart.Axes(constants.xlCategory).HasTitle = 1
        self.chart.Axes(constants.xlCategory).AxisTitle.Text = self.categoryTitle
        self.chart.Axes(constants.xlValue).HasTitle = 1
        self.chart.Axes(constants.xlValue).AxisTitle.Text = self.valueTitle
        self.chart.Axes(constants.xlValue).AxisTitle.Orientation = constants.xlUpward
        self.chart.PlotBy = self.plotBy 
        self.chart.Name = self.chartname
        self.chart.HasTitle = 1
        self.chart.ChartTitle.Text = self.chartTitle
        self.chart.HasDataTable = 0
        self.chart.ChartType = self.chartType 

    def SetLegendPosition(self, legendPosition):
        self.chart.Legend.Position = legendPosition

    def PlotByColumns(self):
        self.chart.PlotBy = constants.xlColumns

    def PlotByRows(self):
        self.chart.PlotBy = constants.xlRows

    def SetCategoryAxisRange(self, minValue, maxValue):
        self.chart.Axes(constants.xlCategory).MinimumScale = minValue
        self.chart.Axes(constants.xlCategory).MaximumScale = maxValue

    def SetValueAxisRange(self, minValue, maxValue):
        self.chart.Axes(constants.xlValue).MinimumScale = minValue
        self.chart.Axes(constants.xlValue).MaximumScale = maxValue

    def ApplyDataLabels(self, dataLabelType):
        self.chart.ApplyDataLabels(dataLabelType)

    def SetBorderLineStyle(self, lineStyle):
        self.chart.PlotArea.Border.LineStyle = lineStyle

    def SetInteriorStyle(self, interiorStyle):
        self.chart.PlotArea.Interior.Pattern = interiorStyle

    # ExcelWorksheet
    # Creates an Excel Worksheet
class ExcelWorksheet:
    def __init__(self, excel, workbook, sheetname):
        self.sheetname = sheetname
        self.excel = excel
        self.workbook = workbook
        self.worksheet = self.workbook.Worksheets.Add()
        self.worksheet.Name = sheetname
    def Activate(self):
        self.worksheet.Activate()
    def SetCell(self, row, col, value):
        self.worksheet.Cells(row,col).Value = value
    def GetCell(self, row, col):
        return self.worksheet.Cells(row,col).Value
    def SetFont(self, row, col, font, size):
        self.worksheet.Cells(row,col).Font.Name = font
        self.worksheet.Cells(row,col).Font.Size = size
    def GetFont(self, row, col):
        font = self.worksheet.Cells(row,col).Font.Name
        size = self.worksheet.Cells(row,col).Font.Size
        return (font, size)

    # ExcelWorkbook
    # Creates an Excel Workbook
class ExcelWorkbook:
    def __init__(self, excel, filename):
        self.filename = filename
        self.excel = excel
        self.workbook = self.excel.Workbooks.Add()
        self.worksheets = {}
    def AddWorksheet(self, name):
        worksheet = ExcelWorksheet(self.excel, self.workbook, name)
        self.worksheets[name] = worksheet
        return worksheet
    def AddChart(self, name, afterSheet):
        chart = ExcelChart(self.excel, self.workbook, name, afterSheet)
        self.worksheets[name] = chart
        return chart
    def Save(self):
        self.workbook.SaveAs(self.filename)
    def Close(self):      
        self.worksheets = {}
        self.workbook.Close()
    def SetAuthor(self, author):
        self.workbook.Author = author

	# ExcelApp
	# Encapsulates an Excel Application
class ExcelApp:
    def __init__(self):
        self.excel = win32com.client.Dispatch("Excel.Application")
        self.workbooks = []
        self.SetDefaultSheetNum(1)
    def Show(self):
        self.excel.Visible = 1
    def Hide(self):
        self.excel.Visible = 0
    def Quit(self):
        for wkb in self.workbooks:
            wkb.Close()
        self.excel.Quit()
    def SetDefaultSheetNum(self, numSheets):
        self.excel.SheetsInNewWorkbook = numSheets
    def AddWorkbook(self, filename):
        workbook = ExcelWorkbook(self.excel, filename)
        self.workbooks.append(workbook)
        return workbook
        
def Main():
    excel = ExcelApp()
    excel.Show()
    
    workbook = excel.AddWorkbook("c:\\temp\\games1.xls")
    
    games = workbook.AddWorksheet("Game Sales")
    accessories = workbook.AddWorksheet("Accessories")
    
    games.Activate()
    
    games.SetFont(1,1,"Arial",18)
    games.SetCell(1,1, "Excel Controlled from Python - Game Sales")
    
    months = ["January", "February", "March"]
    systems = ["Nintendo GameCube", "Sony Playstation 2", "Microsoft XBox"]
    for i in range(len(months)): games.SetCell(3, i+2, months[i])
    for j in range(len(systems)): games.SetCell(4 + j, 1, systems[j])
    
    for i in range(4,6+1):
        for j in range(2,4+1):
            games.SetCell(i,j, i*j)
            
    chart = workbook.AddChart("Gaming Sales Chart", games.worksheet)
    chart.SetTitle("Games Sold by Platform Type per Month")
    chart.SetSource(games.worksheet.Range("A3:D6"))
    chart.SetType(win32com.client.constants.xlColumn)
    chart.SetPlotBy(win32com.client.constants.xlRows)
    chart.SetCategoryTitle("Months")
    chart.SetValueTitle("Sales")
    chart.SetCategoryLabels(1)
    chart.SetSeriesLabels(1)
    chart.CreateChart()
    
    workbook.Save()
    
    excel.Quit()
    
if __name__ == '__main__':
    Main()
    
