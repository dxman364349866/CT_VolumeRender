from __future__ import division

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QLabel,QHBoxLayout
from PyQt5.QtCore import QPoint, Qt, pyqtSignal
from PyQt5.QtGui import QPen, QPainter, QColor
# import dicom_data as dicom_data
import SimpleITK
import numpy as np
import math

class DicomWidget(QLabel):
    """Widget for displaying DICOM data.
    """
    Drawsignle = QtCore.pyqtSignal(list)
    Targetsignle = QtCore.pyqtSignal(list)

    def __init__(self, parent=None, **kwargs):
        # Qt initialization
        super(DicomWidget, self).__init__(parent)

        # self._zoom_level = kwargs.get("zoom_level", 0)
        self._data = kwargs.get("data", None)
        # self._scaled_image = None
        self._low_hu = kwargs.get("low_hu", -1150)
        self._high_hu = kwargs.get("high_hu", 3250)
        # self._plane = kwargs.get("plane", dicom_data.AXIAL)
        self._regionGrowing = kwargs.get('region_growing', 0)
        self._plane = 0

        self._slice = kwargs.get("slice", 0)
        self._color_table = kwargs.get("color_table", [QtGui.qRgb(i, i, i) for i in range(256)])
        self._paxis = kwargs.get('axis', 0)
        self._image = None
        self._pixmap = None
#=============================================================================================

        self.pixmaps = None
        self.winSize = [512, 512]

        self.volumeShape = self._data.shape
        self.pos = None

        self.pen1 = QPen(Qt.blue, 1)
        self.pen2 = QPen(Qt.green, 1)
        self.distancLine = QPen(Qt.white, 1)
#=============================== region growing variable ==================================================
        self.regionPos = [0, 0]
        self.lstSeeds = [(self.regionPos[0], self.regionPos[1])]
        self.LowAndUpper = [100, 300]
#================================================================================================
        self.hLayout = QHBoxLayout(self)

        self.setScaledContents(True)
        self.drawCoord = [512, 512]
        self.drawCoord2 = [512, 512]

        self.TmpRect = QtCore.QRect(0, 0, 512, 512)
        self.choiceNum = 0

    #==============================确定是否决定这个选区================================
        self.decideRegion = False
    #=================================================================================

        self.setLayout(self.hLayout)

        self.decideOperation()
        # self.update_image()

    def decideOperation(self):
        if self._regionGrowing == 0:
            self.update_image()
        elif self._regionGrowing == 1:
            self.updata_regeionGrowing()
        pass

    def choiceNumber(self, number):
        if number >= 0 and number < self.pixmaps.shape[0]-1:
            self.choiceNum = number
            self._data = np.stack(self.pixmaps[self.choiceNum], axis=self._paxis)
            self.update_image()
        pass


    def wheelEvent(self, event):
        up_down = QPoint(event.angleDelta())

#===============================Normal operation============================================
        if self._regionGrowing == False:
            if up_down.y() < 0 and self.choiceNum > 0:
                self.choiceNum -= 1
                self._data  = np.stack(self.pixmaps[self.choiceNum], axis= self._paxis)

            elif up_down.y() > 0 and self.choiceNum < self.pixmaps.shape[0]-1:
                self.choiceNum += 1
                self._data = np.stack(self.pixmaps[self.choiceNum], axis= self._paxis)

            self.update_image()
#===========================================================================================

#=================================regionGrowing operation===================================
        elif self._regionGrowing == True:
            if up_down.y() < 0:
                self.LowAndUpper[0] += 1
                self.LowAndUpper[1] -= 1
            elif up_down.y() > 0:
                self.LowAndUpper[0] -= 1
                self.LowAndUpper[1] += 1
            print(self.LowAndUpper)

            self.updata_regeionGrowing()
#===========================================================================================
        pass


    def updata_regeionGrowing(self):
        if self._data is None:
            print('the data is None')
            return
        if self._data is not None:
            self.imgOriginal = self._data
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

            tmpImage = None
            if self.isChoiceRegion == False:
                tmpImage = SimpleITK.LabelOverlay(self.imgOriginal, SimpleITK.LabelContour(self.imgWhiteMatterNoHoles))
            elif self.isChoiceRegion == True:
                tmpImage = SimpleITK.LabelOverlay(self.imgOriginal, self.imgWhiteMatterNoHoles)

            tmpNarray = SimpleITK.GetArrayFromImage(tmpImage)

#================== h, w, c======================================
            height = tmpNarray.shape[0]
            width = tmpNarray.shape[1]
            channels = tmpNarray.shape[2]
            bytesPerline = channels * width
#================================================================
            tmpNarray = tmpNarray.astype("int8")
            self._image = QtGui.QImage(tmpNarray, width, height, QtGui.QImage.Format_Indexed8)
            self._image.setColorTable(self._color_table)

            pixmap = QtGui.QPixmap.fromImage(self._image)
            self.setPixmap(pixmap)

        pass


    def update_image(self):
        if self._data is not None:
            raw_data = self._data#.get_slice(0, 0)
            shape = raw_data.shape
            data = (raw_data - self._low_hu) / self.window_width * 256
            data = raw_data
            # data = raw_data
            data[data < 0] = 0
            data[data > 255] = 255
            data = data.astype("int8")
            self._image = QtGui.QImage(data, shape[1], shape[0], QtGui.QImage.Format_Indexed8)
            self._image.setColorTable(self._color_table)
        else:
            self._image = None
        self.update_pixmap()
        self.resize(self.winSize[0], self.winSize[1])
        pass

    def update_pixmap(self):
        if self._image is not None:
            pixmap = QtGui.QPixmap.fromImage(self._image)
            self._pixmap = pixmap

            self.setPixmap(self._pixmap)
            self.resize(pixmap.width(), pixmap.height())
            # self.resize(282, 512)
        else:
            self.setText("No image.")
        pass

    def redrawLine(self, axis, coord):
        if axis == 0:
            self.drawCoord[0] = coord[0]
        elif axis == 1:
            self.drawCoord[1] = coord[1]
        pass


# ==================just Qt Event==============
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.pos = event.pos()
            if(self.pos.x()>= 0 and self.pos.x() < self.width() and self.pos.y() >= 0 and self.pos.y() < self.height()):
                self.drawCoord[0] = self.pos.x()
                self.drawCoord[1] = self.pos.y()
                maxnum = max(self._data.shape)
                xaxis = math.floor(maxnum * self.pos.x() / self.width())
                yaxis = math.floor(maxnum * self.pos.y() / self.height())
                self.Drawsignle.emit([xaxis, yaxis])
                self.update_image()
                self.resize(self.winSize[0], self.winSize[1])
                # self._data[self._data == self.pos.x()*10] = self.pos.y()*100
                # print(self.pos.y())
        elif event.buttons() == Qt.RightButton:
            self.pos = event.pos()
            if(self.pos.x()>= 0 and self.pos.x() < self.width() and self.pos.y() >= 0 and self.pos.y() < self.height()):
                self.drawCoord2[0] = self.pos.x()
                self.drawCoord2[1] = self.pos.y()
                maxnum = max(self._data.shape)
                xaxis = math.floor(maxnum * self.pos.x() / self.width())
                yaxis = math.floor(maxnum * self.pos.y() / self.height())
                self.update_image()
                self.Targetsignle.emit([xaxis, yaxis])
                # self.resize(self.winSize[0], self.winSize[1])

        pass


        # if event.button == 3:
        #     print('this is right button')


    def paintEvent(self, QPaintEvent):


        pen3 = QPen(Qt.red, 1)
        pen4 = QPen(Qt.green, 1)

        painter = QPainter(self)

        # draw Hriazontal line
        painter.setPen(self.pen1)
        painter.drawPixmap(self.rect(), self._pixmap)
        painter.drawLine(self.drawCoord[0], 0, self.drawCoord[0], self.height())

        # draw Vertical line
        painter.setPen(self.pen2)
        painter.drawLine(0, self.drawCoord[1], self.width(), self.drawCoord[1])

        pen3.setWidth(3)
        painter.setPen(pen3)
        painter.drawPoint(self.drawCoord[0], self.drawCoord[1])

        pen4.setWidth(5)
        painter.setPen(pen4)
        painter.drawPoint(self.drawCoord2[0], self.drawCoord2[1])

        self.distancLine.setWidth(1)
        painter.setPen(self.distancLine)
        painter.drawLine(self.drawCoord[0], self.drawCoord[1], self.drawCoord2[0], self.drawCoord2[1])

        pass


    def getResizeEvent(self, sizeX, sizeY):
        self.resize(sizeX, sizeY)
        pass

    @property
    def window_width(self):
        """
        :rtype: float
        """
        return self._high_hu - self._low_hu

    @window_width.setter
    def window_width(self, value):
        if value < 0:
            value = 0
        original = self.window_width
        if value != original:
            self._low_hu -= (value - original) / 2
            self._high_hu = self._low_hu + value
            self.calibration_changed.emit()

    @property
    def plane(self):
        return self._plane

    @plane.setter
    def plane(self, value):
        if value != self._plane:
            # if value not in [dicom_data.ALLOWED_PLANES]:
                # raise ValueError("Invalid plane identificator")
            self._plane = value
            self.plane_changed.emit()
            self.data_selection_changed.emit()

    @property
    def slice(self):
        return self._slice

    @slice.setter
    def slice(self, n):
        pass

    @property
    def slice_count(self):
        pass