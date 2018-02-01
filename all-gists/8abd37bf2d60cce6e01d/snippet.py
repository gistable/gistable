from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from itertools import count, islice

class Threaded(QObject):
    result=pyqtSignal(int)

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)

    @pyqtSlot()
    def start(self): print("Thread started")

    @pyqtSlot(int)
    def calculatePrime(self, n):
        primes=(n for n in count(2) if all(n % d for d in range(2, n)))
        self.result.emit(list(islice(primes, 0, n))[-1])

class GUI(QWidget):
    requestPrime=pyqtSignal(int)

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)

        self._thread=QThread()
        self._threaded=Threaded(result=self.displayPrime)
        self.requestPrime.connect(self._threaded.calculatePrime)
        self._thread.started.connect(self._threaded.start)
        self._threaded.moveToThread(self._thread)
        qApp.aboutToQuit.connect(self._thread.quit)
        self._thread.start()

        l=QVBoxLayout(self)
        self._iterationLE=QLineEdit(self, placeholderText="Iteration (n)")
        l.addWidget(self._iterationLE)
        self._requestBtn=QPushButton(
            "Calculate Prime", self, clicked=self.primeRequested)
        l.addWidget(self._requestBtn)
        self._busy=QProgressBar(self)
        l.addWidget(self._busy)
        self._resultLbl=QLabel("Result:", self)
        l.addWidget(self._resultLbl)

    @pyqtSlot()
    def primeRequested(self):
        try: n=int(self._iterationLE.text())
        except: return
        self.requestPrime.emit(n)
        self._busy.setRange(0,0)
        self._iterationLE.setEnabled(False)
        self._requestBtn.setEnabled(False)

    @pyqtSlot(int)
    def displayPrime(self, prime):
        self._resultLbl.setText("Result: {}".format(prime))
        self._busy.setRange(0,100)
        self._iterationLE.setEnabled(True)
        self._requestBtn.setEnabled(True)

if __name__=="__main__":
    from sys import exit, argv

    a=QApplication(argv)
    g=GUI()
    g.show()
    exit(a.exec_())