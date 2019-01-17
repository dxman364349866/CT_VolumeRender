import sys
import math
import numpy as np
from Operation.dicom_data import DicomData
from PyQt5.QtWidgets import  QLabel, QApplication, QPushButton
from PyQt5.QtGui import QPixmap, QImage, QIcon, QColor, QPalette, qRgb
from PyQt5.QtCore import Qt, QRect

import SimpleITK

class dicom_2DLable(QLabel):
    def __init__(self, **kwargs):
        super(dicom_2DLable, self).__init__()
        self._data = kwargs.get('data', None)
        self._datas = kwargs.get('datas', None)
        self._low_hu = kwargs.get("low_hu", -1150)
        self._high_hu = kwargs.get("high_hu", 3250)
        self._color_table = kwargs.get("color_table", [qRgb(i, i, i) for i in range(256)])
        self._image = None

        self.viewPlane = 1

        self.initParameter()
        self.initUI()

    def initParameter(self):
        self.setGeometry(QRect(0, 0, 512, 512))
        self.operationMod = 1
        self.PosXY = [229, 309]
        self.lstSeeds = [(self.PosXY[0], self.PosXY[1])]
        self.LowAndUpper = [100, 500]
        self.idxSlice = 50

        pass

    def initUI(self):
        self.setGeometry(0, 0, 512, 512)

        self.operationModle()
        self.displayfacePlane()
        self.update_image()

        pass

    def operationModle(self):
        if self.operationMod == 0:
            self.mouseMoveEvent = self.imMousemoveEvent
            pass
        elif self.operationMod == 1:
            self.mouseMoveEvent = self.regionMousemoveEvent
            self.wheelEvent = self.regionWheelEvent
            pass
        pass

    def displayfacePlane(self):
        if self.viewPlane == 0:
            self.displayMainPlane()
            pass
        elif self.viewPlane == 1:
            self.displayTopPlane()
            pass
        elif self.viewPlane == 2:
            self.displayLeftPlane()
            pass
        pass

    def displayMainPlane(self):

        pass

    def displayTopPlane(self):
        datas = self._datas.copy()
        datas = np.rot90(datas, -1)
        self._data = datas[150]
        self.update_image()
        self.resize(512, 200)
        pass

    def displayLeftPlane(self):
        pass

    def regionWheelEvent(self,event):
        angle = event.angleDelta() / 8
        angleX = angle.x()
        angleY = angle.y()

        if angleY > 0:
            if self.LowAndUpper[0] < self.LowAndUpper[1] or\
                self.LowAndUpper[1] > self.LowAndUpper[0]:
                self.LowAndUpper[0] += 1
                self.LowAndUpper[1] -= 1
        elif angleY < 0:
            if self.LowAndUpper[0] < self.LowAndUpper[1] or\
                self.LowAndUpper[1] > self.LowAndUpper[0]:
                self.LowAndUpper[0] -= 1
                self.LowAndUpper[1] += 1
        self.drawGrowingArea()
        print(angleX, angleY)
        pass

    def imMousemoveEvent(self, event):
        print('imMouse')
        pass

    def regionMousemoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            xAxis = event.pos().x()
            yAxis = event.pos().y()

            # print(self.logicalDpiX())
            self.PosXY[0] = xAxis
            self.PosXY[1] = yAxis
            self.lstSeeds = [(self.PosXY[0], self.PosXY[1])]

            # print(xAxis, yAxis)

            self.drawGrowingArea()
        pass

    def drawGrowingArea(self):
        self.imgOriginal = SimpleITK.GetImageFromArray(self._datas[50])
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

        tmpArray = np.array(SimpleITK.GetArrayFromImage(tmpImage))
        self._data = tmpArray
        self.update_image()
        pass

    def update_image(self):
        if self._data is not None:
            raw_data = self._data#.get_slice(0, 0)
            shape = raw_data.shape
            tmpImage = None
            if len(shape) < 3:
                # data = (raw_data - self._low_hu) / self.window_width * 256
                data = raw_data
                data[data < 0] = 0
                data[data > 255] = 255
                data = data.astype(np.int8)
                tmpImage = QImage(data, shape[0], shape[1], QImage.Format_Indexed8)
                tmpImage.setColorTable(self._color_table)
            elif len(shape) == 3:
                # data = (raw_data - self._low_hu) / self.window_width * 256
                data = raw_data
                data = data.astype(np.int8)
                tmpImage = QImage(data, shape[0], shape[1], shape[0]*shape[2], QImage.Format_RGB888)
            self._image = tmpImage
        else:
            self._image = None
        self.update_pixmap()
        # self.resize(self.winSize[0], self.winSize[1])
        # print('UpdateImage')
        pass

    def update_pixmap(self):
        if self._image is not None:
            pixmap = QPixmap.fromImage(self._image)
            # self._pixmap = pixmap

            self.setPixmap(pixmap)
            # self.resize(pixmap.width(), pixmap.height())
            # self.resize(512, 512)
        else:
            self.setText("No image.")
        pass

    @property
    def window_width(self):
        """
        :rtype: float
        """
        return self._high_hu - self._low_hu




pathDicom = "D:/Dicomfile/MT_07/"
reader = SimpleITK.ImageSeriesReader()
filenamesDICOM = reader.GetGDCMSeriesFileNames(pathDicom)
reader.SetFileNames(filenamesDICOM)
imgOriginals = reader.Execute()
datas = np.array(SimpleITK.GetArrayFromImage(imgOriginals))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = dicom_2DLable(datas=datas, data= datas[50])
    win.show()
    sys.exit(app.exec_())

