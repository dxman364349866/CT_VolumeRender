import sys
import SimpleITK
import numpy as np
from dicom_data import DicomData
from PyQt5.QtWidgets import QWidget, QLabel, QApplication, QGridLayout, QHBoxLayout, QVBoxLayout
from PyQt5.QtGui import QPixmap, QImage, QIcon, qRgb, QPalette, QColor
from PyQt5.QtCore import Qt


class ITKTestThird(QWidget):
    def __init__(self, **kwargs):
        super(ITKTestThird, self).__init__()
        self.setGeometry(50, 50, 512, 512)
        self.setWindowIcon(QIcon('../Atomic_Icon/area.ico'))
        self.setWindowTitle('ITK_Test')
        self._face = kwargs.get('face', 0)
        self._datas = kwargs.get('datas', 0)
        self._Spacing = kwargs.get('spacing', None)

        self.initUI()

    def initUI(self):
        self.viewLayout = None
        self.ImLable = QLabel(self)

        self.topLable = QLabel(self)
        self.downLable = QLabel(self)
        self.ImLable.resize(self.width(), self.height())

        self.initDicomWindow()
        pass

    def initDicomWindow(self):
        # pathDicom = "D:/Dicomfile/MT_07/"
        # self.idxSlice = 50
        # self.reader = SimpleITK.ImageSeriesReader()
        # filenamesDICOM = self.reader.GetGDCMSeriesFileNames(pathDicom)

        # self.reader.SetFileNames(filenamesDICOM)
        # self.imgOriginals = self.reader.Execute()
        # self.imgOriginal = self.imgOriginals[:, :, self.idxSlice]
        self._color_table = [qRgb(i, i, i) for i in range(64)]
        self.datas = self._datas
        # self.datas = SimpleITK.GetArrayFromImage(self.imgOriginals)

        #============================ChangeFaceSize=============================

        self.xSpacing, self.ySpacing, self.zSpacing = self._Spacing

        self.initViewWindow()

        self.PosXY = [150, 75]
        self.lstSeeds = [(self.PosXY[0], self.PosXY[1])]
        self.LowAndUpper = [100, 300]
        self._axis = 0
        self.idxSlice = 50
        # self.showDicomPixMap()
        self.drawSliceArea()
        self.show()
        pass

    def initViewWindow(self):

        if self._face == 0:
            self.viewLayout = QGridLayout(self)
            self.viewLayout.addWidget(self.ImLable)
            self.ImLable.setAlignment(Qt.AlignCenter)
            self.topfaceView()
        elif self._face == 1:
            self.leftfaceView()

        elif self._face == 2:
            self.viewLayout = QGridLayout(self)
            self.viewLayout.addWidget(self.ImLable)
            self.ImLable.setAlignment(Qt.AlignCenter)
            self.setLayout(self.viewLayout)
            self.frontfaceView()
        pass

    def topfaceView(self):
        self.faceWindowH = self.faceWindowV = 512
        tmpPalete = QPalette()
        tmpPalete.setColor(QPalette.Background, QColor(0, 0, 0))
        self.setPalette(tmpPalete)
        pass

    def leftfaceView(self):
        self.datas = np.rot90(self.datas, -1)
        self.datas = np.rot90(self.datas,  axes=(0, 2))
        width = self.datas.shape[0]
        height = self.datas.shape[1]
        depth = self.datas.shape[2]
        self.faceWindowH = max(width, height, depth)
        self.faceWindowV = self.faceWindowH * self.zSpacing


        tmpPalete = QPalette()
        tmpPalete.setColor(QPalette.Background, QColor(0, 0, 0))
        self.setPalette(tmpPalete)


        pass


    def frontfaceView(self):

        self.datas = np.rot90(self.datas, -1)

        tmpPalete = QPalette()
        tmpPalete.setColor(QPalette.Background, QColor(0, 0, 0))
        self.setPalette(tmpPalete)

        self.faceWindowH = 512
        self.faceWindowV = self.faceWindowH * self.zSpacing
        pass

    def showDicomPixMap(self):
        # aa = SimpleITK.GetImageFromArray(self.datas[15])
        # MyNarray = SimpleITK.GetArrayFromImage(self.imgOriginal)
        MyNarray = self.datas[15]
        height = MyNarray.shape[0]
        width = MyNarray.shape[1]
        bytesPerline = 3 * width
        MyNarray = MyNarray.astype(np.int8)

        ImaImag = QImage(MyNarray, width, width, QImage.Format_Grayscale8)
        ImaImag.setColorTable(self._color_table)
        pixmap = QPixmap.fromImage(ImaImag)

        # paletter = QPalette(self)
        pixmap = pixmap.scaled(self.faceWindowH, self.faceWindowV)


        self.ImLable.setPixmap(pixmap)

        pass

    def drawSliceArea(self):
        self.imgOriginal = SimpleITK.GetImageFromArray(self.datas[self.idxSlice])
        self.imgWhiteMatter = SimpleITK.ConnectedThreshold(image1=self.imgOriginal,
                                                           seedList=self.lstSeeds,
                                                           lower=self.LowAndUpper[0],
                                                           upper=self.LowAndUpper[1],
                                                           replaceValue=1,
                                                           )
        self.imgWhiteMatterNoHoles = SimpleITK.VotingBinaryHoleFilling(image1=self.imgWhiteMatter,
                                                                       radius=[2] * 3,
                                                                       majorityThreshold=50,
                                                                       backgroundValue=0,
                                                                       foregroundValue=1)

        tmpImage = SimpleITK.LabelOverlay(self.imgOriginal, SimpleITK.LabelContour(self.imgWhiteMatterNoHoles))
        # tmpImage = SimpleITK.LabelOverlay(self.imgOriginal, self.imgWhiteMatterNoHoles)
        # tmpImage = SimpleITK.LabelOverlay(self.imgOriginal, self.imgWhiteMatterNoHoles)

        MyNarray = SimpleITK.GetArrayFromImage(tmpImage)




        height = MyNarray.shape[0]
        width = MyNarray.shape[1]
        changne = MyNarray.shape[2]
        MyNarray = MyNarray.astype(np.int8)

        ImaImag = QImage(MyNarray, width, height, width*changne, QImage.Format_RGB888)

        pixmap = QPixmap.fromImage(ImaImag)
        pixmap = pixmap.scaled(self.faceWindowH, self.faceWindowV)



        self.ImLable.setPixmap(pixmap)
        self.ImLable.mouseMoveEvent = self.labelMouseMoveEvent

        # self.replaceViewPosition()
        # print(self.ImLable.size())
        pass

    def labelMouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            xAxis = event.pos().x()
            yAxis = event.pos().y()
            self.PosXY[0] = xAxis
            self.PosXY[1] = yAxis
            self.lstSeeds = [(self.PosXY[0], self.PosXY[1])]
            self.drawSliceArea()
            print(xAxis, yAxis)
        pass

    def getResizeEvent(self, sizeX, sizeY):
        self.resize(sizeX, sizeY)
        pass

    def resizeEvent(self, QResizeEvent):
        # self.resize(self.width(), self.width())
        self.ImLable.move(self.width()/2 - self.ImLable.width()/2, self.height()/2 - self.ImLable.width()/2)
        print(self.ImLable.pos())
        pass

    def wheelEvent(self, event):
        angle = event.angleDelta() / 8
        angleX = angle.x()
        angleY = angle.y()
        if angleY > 0:
            self.idxSlice += 1
        elif angleY < 0:
            self.idxSlice -= 1

        self.drawSliceArea()

        pass


pathDicom = "D:/Dicomfile/MT_07/"
idxSlice = 50
reader = SimpleITK.ImageSeriesReader()
filenamesDICOM = reader.GetGDCMSeriesFileNames(pathDicom)

reader.SetFileNames(filenamesDICOM)
imgOriginals = reader.Execute()
datas = SimpleITK.GetArrayFromImage(imgOriginals)
Spacing = imgOriginals.GetSpacing()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = ITKTestThird(face=1, datas= datas, spacing=Spacing)
    sys.exit(app.exec_())