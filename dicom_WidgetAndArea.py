import sys
import SimpleITK
import numpy as np
from PyQt5.QtWidgets import QWidget,QLabel, QApplication, QGridLayout
from PyQt5.QtGui import QPixmap, QImage, QIcon,qRgb
from PyQt5.QtCore import Qt

class DicomAndSegmentWidget(QWidget):
    def __init__(self):
        super(DicomAndSegmentWidget, self).__init__()
        self.setGeometry(50, 50, 512, 512)
        self.setWindowIcon(QIcon('../Atomic_Icon/area.ico'))
        self.setWindowTitle('ITK_Test')
        self.initUI()

    def initUI(self):
        self.GLayout = QGridLayout()
        self.ImLable = QLabel(self)
        self.GLayout.addWidget(self.ImLable)
        self.setLayout(self.GLayout)

        self.initDicomWindow()
        pass

    def initDicomWindow(self):
        pathDicom = "D:/Dicomfile/MT_07/"
        self.idxSlice = 50
        self.reader = SimpleITK.ImageSeriesReader()
        filenamesDICOM = self.reader.GetGDCMSeriesFileNames(pathDicom)

        self.reader.SetFileNames(filenamesDICOM)
        self.imgOriginals = self.reader.Execute()
        self.imgOriginal = self.imgOriginals[:, :, self.idxSlice]
        self._color_table = [qRgb(i, i, i) for i in range(64)]
        self.datas = SimpleITK.GetArrayFromImage(self.imgOriginals)
        self.datas = np.stack(self.datas, axis=1)
        self.resize(self.datas.shape[0], self.datas.shape[1])


        self.PosXY = [150, 75]
        self.lstSeeds = [(self.PosXY[0], self.PosXY[1])]
        self.LowAndUpper = [100, 300]
        self._axis = 0

        # self.showDicomPixMap()
        self.drawSliceArea()
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
                                                                       majorityThreshold=1,
                                                                       backgroundValue=0,
                                                                       foregroundValue=1)

        tmpImage = SimpleITK.LabelOverlay(self.imgOriginal, SimpleITK.LabelContour(self.imgWhiteMatterNoHoles))
        MyNarray = SimpleITK.GetArrayFromImage(tmpImage)

        height = MyNarray.shape[0]
        width = MyNarray.shape[1]
        changne = MyNarray.shape[2]
        MyNarray = MyNarray.astype(np.int8)

        ImaImag = QImage(MyNarray, width, height, width*changne, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(ImaImag)

        self.ImLable.setPixmap(pixmap)
        self.ImLable.mouseMoveEvent = self.labelMouseMoveEvent

        pass

    def labelMouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            xAxis = event.pos().x()
            yAxis = event.pos().y()
            self.PosXY[0] = xAxis
            self.PosXY[1] = yAxis
            self.lstSeeds = [(self.PosXY[0], self.PosXY[1])]
            self.drawSliceArea()
            # print(xAxis, yAxis)
        pass

    def wheelEvent(self, event):
        angle = event.angleDelta() / 8
        angleX = angle.x()
        angleY = angle.y()
        if angleY > 0:
            self.idxSlice += 1
        elif angleY < 0:
            self.idxSlice -= 1

        # self.imgOriginal = self.imgOriginals[:, :, self.idxSlice]

        # self.showDicomPixMap()
        self.drawSliceArea()

        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = DicomAndSegmentWidget()
    win.show()
    sys.exit(app.exec_())