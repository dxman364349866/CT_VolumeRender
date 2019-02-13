import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMenuBar, QSplitter, \
    QVBoxLayout, QHBoxLayout, QGroupBox, QStatusBar, QLabel, QComboBox
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal
from List_Seeds import SeedButton


class segmentationOperation(QGroupBox):
    Signal_NoParameters = pyqtSignal(bool)
    def __init__(self):
        super(segmentationOperation, self).__init__()
        self.setGeometry(0, 0, 512, 64)
        self.initUI()
    def initUI(self):
        self.addSeed = QPushButton('Add', self)
        self.addSeed.clicked.connect(self.addSeedevent)
        self.removeSeed = QPushButton('Remove', self)
        self.removeSeed.clicked.connect(self.removeSeedevent)

        self.show3DMOd = QComboBox(self)
        self.information = ['Voxel', 'Mesh']
        self.show3DMOd.addItems(self.information)
        self.show3DMOd.activated[int].connect(self.itemChoice)

        self.showButton = QPushButton('CreateMesh', self)

        self.seedOpertaionLayout = QHBoxLayout(self)
        self.seedOpertaionLayout.addWidget(self.addSeed)
        self.seedOpertaionLayout.addWidget(self.removeSeed)
        self.seedOpertaionLayout.addWidget(self.showButton)
        self.seedOpertaionLayout.addWidget(self.show3DMOd)

        self.setLayout(self.seedOpertaionLayout)

    def addSeedevent(self):
        self.Signal_NoParameters.emit(True)
        pass

    def removeSeedevent(self):
        self.Signal_NoParameters.emit(False)
        pass

    def itemChoice(self, event):
        if event == 0:
            print('voxel mod')
        elif event == 1:
            print('mesh mod')

        pass

    pass

class segmentationDisplay(QGroupBox):
    seedColorsSignal = pyqtSignal(list)
    def __init__(self):
        super(segmentationDisplay, self).__init__()
        self.setGeometry(0, 0, 512, 512)
        self.seedBttonbefornum = 0
        self.regionSeedColors = []

        self.initUI()
    def initUI(self):
        self.seedStatus = QStatusBar()
        self.statusButton = QLabel('  color  ')
        self.colorStatus = QLabel('  select  ')
        self.nameStatus = QLabel('   remove   ')

        self.seedStatus.addWidget(self.statusButton)
        self.seedStatus.addWidget(self.colorStatus)
        self.seedStatus.addWidget(self.nameStatus)

        self.subGBox = QGroupBox()
        self.seedListBar = QVBoxLayout()

        self.subGBox.setLayout(self.seedListBar)
        self.subGBox.setGeometry(0, 0, 512, 512)

        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.addWidget(self.seedStatus)
        self.splitter.addWidget(self.subGBox)

        self.showSeedArea = QVBoxLayout()
        self.showSeedArea.addWidget(self.splitter)

        self.setLayout(self.showSeedArea)

    def addSeedwidget(self):
        seedBtn = SeedButton(Num=self.seedListBar.layout().count(), Name='RegionArea ')


        print(len(self.regionSeedColors))
        seedBtn.selectSignal.connect(self.selectSeedButton)
        seedBtn.deleteSignal.connect(self.removeSeedButton)
        self.seedListBar.addWidget(seedBtn)

        self.regionSeedColors.append(seedBtn.regionColor)
        self.seedColorsSignal.emit(self.regionSeedColors)

        pass

    def selectSeedButton(self, event):
        for i in range(0, self.seedListBar.layout().count()):
            if i == event:
                continue
            else:
                print(self.seedListBar.itemAt(i))
                seedBtn = self.seedListBar.itemAt(i).widget()
                seedBtn.setSelectButonDefaultcolor()
                print(i)

        # if self.seedListBar.layout().count() > 1:
        #     self.seedListBar.itemAt(self.seedBttonbefornum).widget().setSelectButonDefaultcolor()
        #     self.seedBttonbefornum = event
        # else:
        #     print('sorry the seedListBar length is to short')

        pass

    def removeSeedButton(self, event):
        print(event)
        for num in range(event, self.seedListBar.layout().count()):
            item = self.seedListBar.itemAt(num)
            TmpW = item.widget()
            TmpW.seedIndex = num - 1
            TmpW.renameSeedButton()
            pass


        self.regionSeedColors.remove(self.regionSeedColors[event])
        self.seedColorsSignal.emit(self.regionSeedColors)

        pass


    pass

class dicom2D_OperationWin(QWidget):
    sendSeedSignal = pyqtSignal(list)
    def __init__(self):
        super(dicom2D_OperationWin, self).__init__()
        self.setWindowTitle('SeedOperationWindow')
        self.initUI()

    def initUI(self):
        self.setGeometry(0, 0, 512, 900)
        self.splitter = QSplitter(Qt.Vertical)
        self.vBox = QVBoxLayout(self)

        self.segmentOpration = segmentationOperation()
        self.segmentOpration.Signal_NoParameters.connect(self.gotSignal)

        self.segmentDisplay = segmentationDisplay()
        self.segmentDisplay.seedColorsSignal.connect(self.gotColorSignal)

        self.splitter.addWidget(self.segmentOpration)
        self.splitter.addWidget(self.segmentDisplay)

        self.vBox.addWidget(self.splitter)
        self.setLayout(self.vBox)

        pass

    def gotColorSignal(self, list):
        # print(list)
        self.sendSeedSignal.emit(list)
        pass

    def gotSignal(self, event):
        if event == True:
            self.addSeedsignal()
        elif event == False:
            self.removeSeedsignal()
        else:
            print('the segmentDisplay signal error')
        pass


    def addSeedsignal(self):
        print('Add')
        self.segmentDisplay.addSeedwidget()
        pass

    def removeSeedsignal(self):
        print('Remove')
        pass



if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = dicom2D_OperationWin()
    win.show()
    sys.exit(app.exec_())