import sys
import SimpleITK
from PyQt5.QtWidgets import  QWidget, QApplication, QGridLayout, QMdiSubWindow, QHBoxLayout, \
    QVBoxLayout, QSplitter, QPushButton
from PyQt5.QtGui import QPalette
from PyQt5.QtCore import Qt

from dicom_WidgetAndArea import dicomImage2DdisplayWidget
from functools import partial


class dicom_widgetEve(QWidget):
    def __init__(self, **kwargs):
        super(dicom_widgetEve,self).__init__()
        self.setGeometry(50, 50, 512, 512)
        self.setWindowTitle('Dicom2DEve')
        self.initUI()

    def initUI(self):
        #==============================TmpTestsParameter==================================
        pathDicom = "D:/Dicomfile/SavedSE3/"
        idxSlice = 50
        reader = SimpleITK.ImageSeriesReader()
        filenamesDICOM = reader.GetGDCMSeriesFileNames(pathDicom)

        reader.SetFileNames(filenamesDICOM)
        imgOriginals = reader.Execute()
        datas = SimpleITK.GetArrayFromImage(imgOriginals)
        Spacing = imgOriginals.GetSpacing()
        #=================================================================================
        print(Spacing)
        print(datas.shape)
        tmpPalete = QPalette()
        tmpPalete.setColor(QPalette.Background, Qt.black)
        self.setPalette(tmpPalete)

        self.GLayout = QGridLayout(self)
        self.dicom2D = dicomImage2DdisplayWidget(face=0, datas=datas, spacing=Spacing)
        # self.GLayout.addWidget(self.dicom2D)
        # self.setLayout(self.GLayout)
        self.dicom2D.addSeedsSignal.connect(self.addSeedList)

        self.splitter = QSplitter(self)
        self.splitter.setOrientation(Qt.Horizontal)

        self.otherWidget = QWidget(self)
        self.otherWidget.setGeometry( 0, 0, 512, 512)
        self.otherWidget.tmpLayout = QVBoxLayout(self.otherWidget)
        self.otherWidget.setLayout(self.otherWidget.tmpLayout)

        self.splitter.addWidget(self.dicom2D)
        self.splitter.addWidget(self.otherWidget)

        self.GLayout.addWidget(self.splitter)
        self.setLayout(self.GLayout)

        self.testNum = 0

        pass

    def addSeedList(self, event):
        tmpButton = QPushButton('ID:' + str(self.testNum), self.otherWidget)
        tmpButton.clicked.connect(partial( self.mybuttonClicked, str(self.testNum)))
        self.otherWidget.tmpLayout.addWidget(tmpButton)
        self.testNum += 1

        pass

    def mybuttonClicked(self, event):
        print('helloButton')
        print(self.sender().text())
        print(self.sender().text())
        pass

    def resizeEvent(self, QResizeEvent):
        # print('\n'.join(dir(QResizeEvent)))
        self.dicom2D.getResizeEvent(QResizeEvent.size().width(), QResizeEvent.size().height())
        pass





if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = dicom_widgetEve()
    win.show()
    sys.exit(app.exec_())