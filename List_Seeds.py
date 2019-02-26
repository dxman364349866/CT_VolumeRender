from PyQt5.QtWidgets import QWidget ,QPushButton, QHBoxLayout
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPalette, QColor, QIcon
import random

class SeedButton(QWidget):
    deleteSignal = pyqtSignal(int)
    selectSignal = pyqtSignal(int)
    viewRegionsignal = pyqtSignal(list)
    def __init__(self, **kwargs):
        super(SeedButton, self).__init__()
        self.setGeometry(0, 0, 256, 64)
        self.seedIndex = kwargs.get('Num', 0)
        self.seedName = kwargs.get('Name', 'Select')
        self.regionColor = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
        self.selectBtmIsSelect = False
        self.isEyeopen = False

        self.seedValue = (0, 0)

        self.initUI()
    def initUI(self):
        self.eyeBtn = QPushButton(self)
        self.eyeBtn.setGeometry(0, 0, 32, 32)
        self.eyeBtn.setIcon(QIcon('../Atomic_Icon/closeEye.png'))
        self.eyeBtn.clicked.connect(self.eyeViewEvent)


        # self.colorBtn = QPushButton(self)
        # self.colorBtn.setStyleSheet('background-color: rgb(' + str(self.regionColor[0]) + ',' + str(self.regionColor[1]) + ',' + str(self.regionColor[2]) + ')')
        self.selectBtn = QPushButton(self.seedName + str(self.seedIndex), self)
        self.selectBtn.clicked.connect(self.selectSeed)


        self.deleteBtn = QPushButton('Delete:' + str(self.seedIndex), self)
        self.deleteBtn.clicked.connect(self.deleteSeed)

        self.BtnLayout = QHBoxLayout(self)
        self.BtnLayout.addWidget(self.eyeBtn)
        self.BtnLayout.addWidget(self.selectBtn)
        # self.BtnLayout.addWidget(self.drawModBtn)
        # self.BtnLayout.addWidget(self.eraserBtn)
        self.BtnLayout.addWidget(self.deleteBtn)
        self.BtnLayout.setAlignment(Qt.AlignLeft)
        self.setLayout(self.BtnLayout)
        pass

    def eyeViewEvent(self):
        if self.isEyeopen == False:
            self.eyeBtn.setIcon(QIcon('../Atomic_Icon/openEye.png'))
            self.isEyeopen = True
            viewInfor = [True, self.seedIndex]
            self.viewRegionsignal.emit(viewInfor)
        elif self.isEyeopen == True:
            self.eyeBtn.setIcon(QIcon('../Atomic_Icon/closeEye.png'))
            self.isEyeopen = False
            viewInfor = [False, self.seedIndex]
            self.viewRegionsignal.emit(viewInfor)
        pass

    def renameSeedButton(self):
        self.selectBtn.setText(self.seedName + str(self.seedIndex))
        self.deleteBtn.setText('Delete' + str(self.seedIndex))
        pass

    def selectSeed(self, event):
        if self.selectBtmIsSelect == False:
           self.setSelectButonColor()
           self.selectSignal.emit(self.seedIndex)
        elif self.selectBtmIsSelect == True:
            self.setSelectButonDefaultcolor()

        pass

    # def drawMod(self):
    #     if self.selectBtmIsSelect == True:
    #         self.drawAnderaserSingnal.emit(1)
    #     else:
    #         self.drawAnderaserSingnal.emit(0)
    #     pass
    #
    # def eraserMod(self):
    #     if self.selectBtmIsSelect == True:
    #         self.drawAnderaserSingnal.emit(2)
    #     else:
    #         self.drawAnderaserSingnal.emit(0)
    #     pass

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