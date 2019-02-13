from PyQt5.QtWidgets import QWidget ,QPushButton, QHBoxLayout
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPalette, QColor
import random

class SeedButton(QWidget):
    deleteSignal = pyqtSignal(int)
    selectSignal = pyqtSignal(int)
    def __init__(self, **kwargs):
        super(SeedButton,self).__init__()
        self.setGeometry(0, 0, 256, 64)
        self.seedIndex = kwargs.get('Num', 0)
        self.seedName = kwargs.get('Name', 'Select')
        self.regionColor = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
        self.selectBtmIsSelect = False

        self.initUI()
    def initUI(self):
        self.colorBtn = QPushButton(self)
        self.colorBtn.setStyleSheet('background-color: rgb(' + str(self.regionColor[0]) + ',' + str(self.regionColor[1]) + ',' + str(self.regionColor[2]) + ')')
        self.selectBtn = QPushButton(self.seedName + str(self.seedIndex), self)
        self.selectBtn.clicked.connect(self.selectSeed)
        self.deleteBtn = QPushButton('Delete:' + str(self.seedIndex), self)
        self.deleteBtn.clicked.connect(self.deleteSeed)

        self.BtnLayout = QHBoxLayout(self)
        self.BtnLayout.addWidget(self.colorBtn)
        self.BtnLayout.addWidget(self.selectBtn)
        self.BtnLayout.addWidget(self.deleteBtn)
        self.setLayout(self.BtnLayout)

        pass
    def renameSeedButton(self):
        self.selectBtn.setText(self.seedName + str(self.seedIndex))
        self.deleteBtn.setText('Delete' + str(self.seedIndex))
        pass

    def selectSeed(self, event):
        self.selectSignal.emit(self.seedIndex)
        if self.selectBtmIsSelect == False:
           self.setSelectButonColor()

        elif self.selectBtmIsSelect == True:
            self.setSelectButonDefaultcolor()
        pass

    def deleteSeed(self, event):
        self.deleteLater()
        self.deleteSignal.emit(self.seedIndex)
        pass

    def setSelectButonDefaultcolor(self):
        self.selectBtn.setStyleSheet('backgound-color: None')
        self.selectBtmIsSelect = False
        pass

    def setSelectButonColor(self):
        self.selectBtn.setStyleSheet("background-color: rgb(255, 255, 255)")
        self.selectBtmIsSelect = True
        pass