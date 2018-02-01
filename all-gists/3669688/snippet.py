#!/usr/bin/env python

import wx
from wx import EVT_CLOSE
import wx.grid as gridlib

EVEN_ROW_COLOUR = '#CCE6FF'
GRID_LINE_COLOUR = '#ccc'

class PandasTable(wx.Frame):
    def __init__(self, parent, title, df):
        super(PandasTable, self).__init__(parent, title=title)
        panel = wx.Panel(self, -1)
        self.data = df
        grid = self.create_grid(panel, self.data)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(grid, 1, wx.ALL|wx.EXPAND)
        panel.SetSizer(sizer)

        # Bind Close Event
        EVT_CLOSE(self, self.exit)
        self.Center()
        self.Show()

    def exit(self, event):
        self.Destroy()

    def create_grid(self, panel, data):
        table = DataTable(data)
        grid = DataGrid(panel)
        grid.CreateGrid(len(data), len(data.columns))
        grid.SetTable(table)
        grid.AutoSize()
        grid.AutoSizeColumns(True)
        return grid

class DataTable(gridlib.PyGridTableBase):
    def __init__(self, data=None):
        gridlib.PyGridTableBase.__init__(self)
        self.headerRows = 0
        self.data = data

    def GetNumberRows(self):
        return len(self.data)

    def GetNumberCols(self):
        return len(self.data.columns) + 1

    def GetValue(self, row, col):
        if col == 0:
            return self.data.index[row]
        return self.data.ix[row, col-1]

    def SetValue(self, row, col, value):
        pass

    def GetColLabelValue(self, col):
        if col == 0:
            return 'Index' if self.data.index.name is None else self.data.index.name
        return self.data.columns[col-1]

    def GetTypeName(self, row, col):
        return gridlib.GRID_VALUE_STRING

    def GetAttr(self, row, col, prop):
        attr = gridlib.GridCellAttr()
        if row % 2 == 1:
            attr.SetBackgroundColour(EVEN_ROW_COLOUR)
        return attr

class DataGrid(gridlib.Grid):
    def __init__(self, parent, size=wx.Size(1000, 500)):
        self.parent = parent
        gridlib.Grid.__init__(self, self.parent, -1)
        self.SetGridLineColour(GRID_LINE_COLOUR)
        self.SetRowLabelSize(0)
        self.SetColLabelSize(30)
        self.table = DataTable()

def display(df):
    app = wx.App()
    frame = PandasTable(None, 'test', df)
    app.MainLoop()

def main():
    import pandas as pd
    import numpy as np
    df = pd.DataFrame({'a' : np.random.randn(10000), 'b' : np.random.randn(10000), 'c' : np.random.randn(10000)})
    display(df)

if __name__ == '__main__':
    main()
