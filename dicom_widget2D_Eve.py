import sys
import SimpleITK
from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout, QMdiSubWindow, QHBoxLayout, \
    QVBoxLayout, QSplitter, QPushButton, QGroupBox, QLayoutItem, QWidgetItem
from PyQt5.QtGui import QPalette
from PyQt5.QtCore import Qt

from dicom_WidgetAndArea import dicomImage2DdisplayWidget
from dicom_widget2D_Operation import dicom2D_OperationWin
from functools import partial
from List_Seeds import SeedButton


class dicom_widgetEve(QWidget):
    # sendBackInfor = pyqtSignal(int)
    def __init__(self, **kwargs):
        super(dicom_widgetEve, self).__init__()
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
        # print(Spacing)
        # print(datas.shape)

        tmpPalete = QPalette()
        tmpPalete.setColor(QPalette.Background, Qt.black)
        self.setPalette(tmpPalete)

        self.GLayout = QGridLayout(self)
        self.dicom2D = dicomImage2DdisplayWidget(face=0, datas=datas, spacing=Spacing)
        self.GLayout.addWidget(self.dicom2D)
        self.setLayout(self.GLayout)

        self.OperationWin = dicom2D_OperationWin()
        self.OperationWin.show()
        self.OperationWin.sendSeedSignal.connect(self.showSeedsList)
        self.OperationWin.sendSeedSelectSignal.connect(self.selectSeedInList)
        self.OperationWin.sendSeedRegionViewSignal.connect(self.seedRegionView)

        # self.dicom2D.addSeedsSignal.connect(self.addSeedList)

        # self.splitter = QSplitter(self)
        # self.splitter.setOrientation(Qt.Horizontal)

        # self.otherWidget = QWidget(self)
        # self.otherWidget.setGeometry(0, 0, 512, 512)
        # self.otherWidget.tmpLayout = QVBoxLayout(self.otherWidget)
        # self.otherWidget.setLayout(self.otherWidget.tmpLayout)

        # self.splitter.addWidget(self.dicom2D)
        # self.splitter.addWidget(self.otherWidget)

        # self.GLayout.addWidget(self.splitter)
        # self.setLayout(self.GLayout)
        # self.seedList = []

        # self.seedListNum = 0

        pass

    # def addSeedList(self, event):
    #
    #     TmpSeedButton = SeedButton(Num=self.otherWidget.tmpLayout.count())
    #     TmpSeedButton.deleteSignal.connect(self.seedDeleteFunction)
    #     self.otherWidget.tmpLayout.addWidget(TmpSeedButton)
    #     # self.seedList.append(TmpSeedButton)
    #
    #     pass

    # def sortSeedList(self, num):
    #     print(self.otherWidget.tmpLayout.count())
    #     for i in range(num, self.otherWidget.tmpLayout.count()):
    #         item = self.otherWidget.tmpLayout.itemAt(i)
    #         TmpW = item.widget()
    #         TmpW.seedIndex = i -1
    #         TmpW.renameSeedButton()
    #     pass

    # def seedDeleteFunction(self, event):
    #     self.sortSeedList(event)
    #     pass


    # def seedSelectFunction(self, event):
        # text = self.sender().text()
        # text, num = text.split(':')
        # self.dicom2D.getSeedEvent(int(num))
        # pass

    def showSeedsList(self, list):
        # print('Hello:' + str(list))
        self.dicom2D.setSeedsColor(list)
        pass

    def selectSeedInList(self, num):
        # print('select num is : ', num)
        self.dicom2D.selectSeedinList(num)
        pass

    def seedRegionView(self, event):
        self.dicom2D.viewSeedinList(event)
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