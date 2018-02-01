# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 10:50:56 2013

@author: cmarshall
"""

import sip
sip.setapi('QString', 1)
sip.setapi('QVariant', 1)
 
import pandas as pd
from PyQt4 import QtCore, QtGui
 

class TableModel(QtCore.QAbstractTableModel): 
    def __init__(self, parent=None, *args): 
        super(TableModel, self).__init__()
        self.datatable = None

        
    def update(self, dataIn):
        print 'Updating Model'
        self.datatable = dataIn
        print 'Datatable : {0}'.format(self.datatable)
        
     
    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.datatable.index) 
        
    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self.datatable.columns.values) 
        
    def data(self, index, role=QtCore.Qt.DisplayRole):
        #print 'Data Call'
        #print index.column(), index.row()
        if role == QtCore.Qt.DisplayRole:
            i = index.row()
            j = index.column()
            #return QtCore.QVariant(str(self.datatable.iget_value(i, j)))
            return '{0}'.format(self.datatable.iget_value(i, j))
        else:
            return QtCore.QVariant()
    
    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled
            

class TableView(QtGui.QTableView):
    """
    A simple table to demonstrate the QComboBox delegate.
    """
    def __init__(self, *args, **kwargs):
        QtGui.QTableView.__init__(self, *args, **kwargs)
 
 
if __name__=="__main__":
    from sys import argv, exit
    
    class Widget(QtGui.QWidget):
        """
        A simple test widget to contain and own the model and table.
        """
        def __init__(self, parent=None):
            QtGui.QWidget.__init__(self, parent)
 
            l=QtGui.QVBoxLayout(self)
            cdf = self.get_data_frame()
            self._tm=TableModel(self)
            self._tm.update(cdf)
            self._tv=TableView(self)
            self._tv.setModel(self._tm)
            l.addWidget(self._tv)
            
        def get_data_frame(self):
            df = pd.DataFrame({'Name':['a','b','c','d'], 
            'First':[2.3,5.4,3.1,7.7], 'Last':[23.4,11.2,65.3,88.8], 'Class':[1,1,2,1], 'Valid':[True, True, True, False]})
            return df
 
    a=QtGui.QApplication(argv)
    w=Widget()
    w.show()
    w.raise_()
    exit(a.exec_())