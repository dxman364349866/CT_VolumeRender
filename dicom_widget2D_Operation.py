import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMenuBar, QSplitter, \
    QVBoxLayout, QHBoxLayout, QGroupBox, QStatusBar, QLabel, QComboBox, QScrollArea
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal
from List_Seeds import SeedButton


class segmentationOperation(QGroupBox):
    Signal_BoolParameters = pyqtSignal(bool)
    Signal_PenAndEraser = pyqtSignal(int)
    def __init__(self):
        super(segmentationOperation, self).__init__()
        self.setGeometry(0, 0, 512, 64)
        self.initUI()
    def initUI(self):
        self.addSeed = QPushButton('Add', self)
        self.addSeed.clicked.connect(self.addSeedevent)
        # self.removeSeed = QPushButton('Remove', self)
        # self.removeSeed.clicked.connect(self.removeSeedevent)

        #==============Define pen and eraser==================
        self.regionPen = QPushButton('pen', self)
        self.regionPen.clicked.connect(self.regionPenEvent)
        self.regionPenmod = False
        self.regionEraserMod = False
        self.regionEraser = QPushButton('eraser', self)
        self.regionEraser.clicked.connect(self.regionEraserEvent)

        #=====================================================

        self.show3DMOd = QComboBox(self)
        self.information = ['Voxel', 'Mesh']
        self.show3DMOd.addItems(self.information)
        self.show3DMOd.activated[int].connect(self.itemChoice)

        self.showButton = QPushButton('CreateMesh', self)

        self.seedOpertaionLayout = QHBoxLayout(self)
        self.seedOpertaionLayout.addWidget(self.addSeed)
        # self.seedOpertaionLayout.addWidget(self.removeSeed)
        self.seedOpertaionLayout.addWidget(self.regionPen)
        self.seedOpertaionLayout.addWidget(self.regionEraser)
        self.seedOpertaionLayout.addWidget(self.showButton)
        self.seedOpertaionLayout.addWidget(self.show3DMOd)

        self.setLayout(self.seedOpertaionLayout)

    def addSeedevent(self):
        self.Signal_BoolParameters.emit(True)
        pass

    def removeSeedevent(self):
        self.Signal_BoolParameters.emit(False)
        pass

    def regionPenEvent(self, event):
        if self.regionPenmod == False:
            self.regionPen.setStyleSheet('background-color: rgb(255, 255, 255)')
            self.Signal_PenAndEraser.emit(1)
            if self.regionEraserMod == True:
                self.regionEraser.setStyleSheet('background-color: None')
                self.regionEraserMod = False
            self.regionPenmod = True
        elif self.regionPenmod == True:
            self.Signal_PenAndEraser.emit(0)
            self.regionPen.setStyleSheet('background-color: None')
            self.regionPenmod = False
        else:
            print('Pen error')
        pass

    def regionEraserEvent(self, event):
        if self.regionEraserMod == False:
            self.regionEraser.setStyleSheet('background-color: rgb(255, 255, 255)')
            self.Signal_PenAndEraser.emit(2)
            if self.regionPenmod == True:
                self.regionPen.setStyleSheet('background-color: None')
                self.regionPenmod = False
            self.regionEraserMod = True
        elif self.regionEraserMod == True:
            self.Signal_PenAndEraser.emit(0)
            self.regionEraser.setStyleSheet('background-color: None')
            self.regionEraserMod = False
        else:
            print('Eraser error')
        pass

    def itemChoice(self, event):
        if event == 0:
            print('voxel mod')
        elif event == 1:
            print('mesh mod')

        pass

    pass

#=========================================================================
#                             DISPLAYAREA
#=========================================================================

class segmentationDisplay(QGroupBox):
    seedColorsSignal = pyqtSignal(list)
    seedSelectSignal = pyqtSignal(int)
    seedRegionViewSignal = pyqtSignal(list)

    def __init__(self):
        super(segmentationDisplay, self).__init__()
        self.setGeometry(0, 0, 512, 512)
        self.seedBttonbefornum = 0
        self.regionSeedinfor = []
        self.listSeeds = []

        self.initUI()
    def initUI(self):
        self.seedStatus = QStatusBar()

        visable = QLabel('visable  ')
        statusButton = QLabel('  color  ')
        colorStatus = QLabel('  select  ')
        nameStatus = QLabel('   remove   ')

        self.seedStatus.addWidget(visable)
        self.seedStatus.addWidget(statusButton)
        self.seedStatus.addWidget(colorStatus)
        self.seedStatus.addWidget(nameStatus)

        self.seedListBar = QVBoxLayout()
        self.seedListBar.setAlignment(Qt.AlignTop)

        self.topFiller = QWidget()
        self.topFiller.setLayout(self.seedListBar)
        self.topFiller.setMinimumSize(250, 2000)

        self.scrollArea = QScrollArea(self)
        self.scrollArea.setGeometry(0, 0, 512, 512)
        self.scrollArea.setWidget(self.topFiller)
        self.scrollArea.setWidgetResizable(True)



        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.addWidget(self.seedStatus)
        self.splitter.addWidget(self.scrollArea)

        self.showSeedArea = QVBoxLayout()
        self.showSeedArea.addWidget(self.splitter)

        self.setLayout(self.showSeedArea)

    def addSeedwidget(self):
        seedBtn = SeedButton(Num=self.seedListBar.layout().count(), Name='RegionArea:')
        seedBtn.selectSignal.connect(self.selectSeedButton)
        seedBtn.deleteSignal.connect(self.removeSeedButton)
        seedBtn.viewRegionsignal.connect(self.viewRegionArea)

        seedInform = [seedBtn.regionColor, (0, 0)]
        self.seedListBar.insertWidget(self.seedListBar.count()-1, seedBtn)

        self.seedListBar.addWidget(seedBtn)
        self.regionSeedinfor.append(seedInform)

        self.seedColorsSignal.emit(self.regionSeedinfor)

        pass

    def selectSeedButton(self, event):
        for i in range(0, self.seedListBar.layout().count()):
            if i == event:
                continue
            else:
                # print(self.seedListBar.itemAt(i))
                seedBtn = self.seedListBar.itemAt(i).widget()
                seedBtn.setSelectButonDefaultcolor()
                # print(i)

        self.seedSelectSignal.emit(event)

        pass

    def removeSeedButton(self, event):
        # print(event)
        for num in range(event, self.seedListBar.layout().count()):
            item = self.seedListBar.itemAt(num)
            TmpW = item.widget()
            TmpW.seedIndex = num - 1
            TmpW.renameSeedButton()
            pass


        self.regionSeedinfor.remove(self.regionSeedinfor[event])
        self.seedColorsSignal.emit(self.regionSeedinfor)

        pass

    def viewRegionArea(self, event):
        self.seedRegionViewSignal.emit(event)
        pass
    pass


#=================================================================
#                    this is main windows
#=================================================================

class dicom2D_OperationWin(QWidget):
    sendSeedSignal = pyqtSignal(list)
    sendSeedSelectSignal = pyqtSignal(int)
    sendSeedRegionViewSignal = pyqtSignal(list)
    sendDrawModSignal = pyqtSignal(int)
    def __init__(self):
        super(dicom2D_OperationWin, self).__init__()
        self.setWindowTitle('SeedOperationWindow')
        self.initUI()

    def initUI(self):
        self.setGeometry(0, 0, 512, 900)
        self.splitter = QSplitter(Qt.Vertical)
        self.vBox = QVBoxLayout(self)

        self.segmentOpration = segmentationOperation()
        self.segmentOpration.Signal_BoolParameters.connect(self.gotSignal)
        self.segmentOpration.Signal_PenAndEraser.connect(self.drawSignal)

        self.segmentDisplay = segmentationDisplay()
        self.segmentDisplay.seedColorsSignal.connect(self.seedSeedInforList)
        self.segmentDisplay.seedSelectSignal.connect(self.seedSeedSelect)
        self.segmentDisplay.seedRegionViewSignal.connect(self.seedRegionView)

        self.splitter.addWidget(self.segmentOpration)
        self.splitter.addWidget(self.segmentDisplay)

        self.vBox.addWidget(self.splitter)
        self.setLayout(self.vBox)

        pass

    def seedSeedInforList(self, list):
        # print(list)
        self.sendSeedSignal.emit(list)
        pass

    def seedSeedSelect(self, num):
        self.sendSeedSelectSignal.emit(num)
        pass

    def seedRegionView(self, event):
        self.sendSeedRegionViewSignal.emit(event)
        pass

    def gotSignal(self, event):
        if event == True:
            self.addSeedsignal()
        elif event == False:
            self.removeSeedsignal()
        else:
            print('the segmentDisplay signal error')
        pass

    def drawSignal(self, event):
        if event == 1:
            self.sendDrawModSignal.emit(1)
        elif event == 2:
            self.sendDrawModSignal.emit(2)
        elif event == 0:
            self.sendDrawModSignal.emit(0)
        else:
            print('drawSignal function error.....')
        pass

    def addSeedsignal(self):
        # print('Add')
        self.segmentDisplay.addSeedwidget()
        pass

    def removeSeedsignal(self):
        print('Remove')
        pass

    # def keyPressEvent(self, QKeyEvent):
    #     print('hello')
    #     pass



if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = dicom2D_OperationWin()
    win.show()
    sys.exit(app.exec_())