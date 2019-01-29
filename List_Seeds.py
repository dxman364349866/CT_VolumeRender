from PyQt5.QtWidgets import QWidget ,QPushButton, QHBoxLayout
from PyQt5.QtCore import pyqtSignal

class SeedButton(QWidget):
    deleteSignal = pyqtSignal(int)
    selectSignal = pyqtSignal(int)
    def __init__(self, **kwargs):
        super(SeedButton,self).__init__()
        self.setGeometry(0, 0, 256, 64)
        self.seedIndex = kwargs.get('Num', 0)
        self.initUI()
    def initUI(self):
        self.selectBtn = QPushButton('Select:' + str(self.seedIndex), self)
        self.selectBtn.clicked.connect(self.selectSeed)
        self.deleteBtn = QPushButton('Delete:' + str(self.seedIndex), self)
        self.deleteBtn.clicked.connect(self.deleteSeed)

        self.BtnLayout = QHBoxLayout(self)
        self.BtnLayout.addWidget(self.selectBtn)
        self.BtnLayout.addWidget(self.deleteBtn)
        self.setLayout(self.BtnLayout)

        pass
    def renameSeedButton(self):
        self.selectBtn.setText('Select' + str(self.seedIndex))
        self.deleteBtn.setText('Delete' + str(self.seedIndex))
        # print(self.seedIndex)
        pass

    def selectSeed(self, event):
        self.selectSignal.emit(self.seedIndex)
        pass

    def deleteSeed(self, event):
        self.deleteLater()
        self.deleteSignal.emit(self.seedIndex)
        pass