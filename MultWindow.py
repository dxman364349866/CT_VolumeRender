import sys
import os
from PyQt5.QtWidgets import QMainWindow, QLayout, QApplication, QHBoxLayout, QFileDialog, QMenu, QPushButton, QAction
from PyQt5.QtGui import QIcon
from MultDicomWindowSecond import multDicomWindows

class TestMainWindow(QMainWindow):
    def __init__(self):
        super(TestMainWindow, self).__init__()
        width = 512
        height = 512
        self.setGeometry(30, 30, width, width)
        self.setWindowTitle('奥菲科医疗')
        self.setWindowIcon(QIcon('../Atomic_Icon/area.ico'))
        self.initUI()

    def initUI(self):
        self.dicomWindow = None
        self.mainMenu = self.menuBar()
        fileMenu = self.mainMenu.addMenu('文件')
        toolMenu = self.mainMenu.addMenu('工具')

        openButton = QAction(QIcon('../Atomic_Icon/Open.png'), 'Open', self)
        openButton.triggered.connect(self.openDirectoryDialog)

        closeButton = QAction(QIcon('../Atomic_Icon/Exit.png'), 'close', self)
        closeButton.triggered.connect(self.closeDicomView)

        operationButton = QAction(QIcon('../Atomic_Icon/SliderHandle.png'), 'OperationTool', self)
        operationButton.triggered.connect(self.openOparatioinTool)

        fileMenu.addAction(openButton)
        fileMenu.addAction(closeButton)
        toolMenu.addAction(operationButton)
        pass

    def openOparatioinTool(self):
        if self.dicomWindow != None:
            tmpVopacity = self.dicomWindow.volumView.vOpacity
            tmpVcolor = self.dicomWindow.volumView.vcolor
            tmpGopacity = self.dicomWindow.volumView.gOpacity
            self.dicomWindow.openOperationTool(tmpVopacity, tmpVcolor, tmpGopacity)
            print('---------openOparationTool----------')

        else:
            print('sorry dicomWindow is None')
        pass
    def closeDicomView(self):
        if self.dicomWindow != None:
            self.dicomWindow.close()
            self.dicomWindow.deleteLater()
            self.dicomWindow.setParent(None)
            self.dicomWindow = None
            self.layout().removeWidget(self.dicomWindow)
        else:
            print(self.dicomWindow)
            print('self.dicomWIndow is None')

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "打开文件", "",
                                                  "All Files (*);;(*.dcm)", options=options)
        if fileName:
            print(fileName)
        pass

    def openDirectoryDialog(self):
        Direct = str(QFileDialog.getExistingDirectory(self, 'Select Directory'))
        if Direct:
            self.viewDicomWindow(Direct)
            print(Direct)


    def viewDicomWindow(self, path):
        if self.dicomWindow == None:
            self.dicomWindow = multDicomWindows(path=path)
            tmpVOpacity = self.dicomWindow.volumView.vOpacity
            tmpGOpacity = self.dicomWindow.volumView.gOpacity
            tmpVColor = self.dicomWindow.volumView.vcolor

            self.setCentralWidget(self.dicomWindow)
        else:
            self.closeDicomView()
            self.dicomWindow = multDicomWindows(path=path)
            self.setCentralWidget(self.dicomWindow)
        print(self.dicomWindow)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = TestMainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
