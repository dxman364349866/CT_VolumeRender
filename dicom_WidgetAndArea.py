import sys
import SimpleITK
import numpy as np
from dicom_data import DicomData
from PyQt5.QtWidgets import QWidget, QLabel, QApplication, QGridLayout, \
    QHBoxLayout, QVBoxLayout, QPushButton, QComboBox, QScrollBar
from PyQt5.QtGui import QPixmap, QImage, QIcon, qRgb, QPalette, QColor
from Plot_RangeSlider import QRangeSlider
from PyQt5.QtCore import Qt


class dicomImage2DdisplayWidget(QWidget):
    def __init__(self, **kwargs):
        super(dicomImage2DdisplayWidget, self).__init__()
        self._face = kwargs.get('face', 0)
        self._datas = kwargs.get('datas', 0)
        self._Spacing = kwargs.get('spacing', None)
        self._low_hu = kwargs.get("low_hu", -1150)
        self._high_hu = kwargs.get("high_hu", 3250)

        self.initUI()


    def initUI(self):
        self.setGeometry(0, 0, 512, 512)

        self.viewLayout = None
        self.imLable = QLabel(self)
        self.imData = None

        self.topLable = QLabel(self)
        self.downLable = QLabel(self)
        self.imLable.resize(self.width(), self.height())

        self.initDicomParameter()
        pass

    def initDicomParameter(self):
        #============================SetDataParameter===========================
        self._color_table = [qRgb(i, i, i) for i in range(64)]
        self.datas = self._datas.copy()

        self.faceWindowV = self.faceWindowH = max(self.datas.shape)

        #============================ChangeFaceSize=============================
        self.xSpacing, self.ySpacing, self.zSpacing = self._Spacing

        #============================OperationMod===============================
        self.OperationMod = 0
        self.faceList = ['MainFace', 'LeftFace', 'FrontFace']
        self.beforFaceName = self.faceList[self._face]
        #============================RegionGrowingParameter=====================
        self.PosXY = [150, 75]
        self.lstSeeds = [(self.PosXY[0], self.PosXY[1])]
        self.LowAndUpper = [100, 300]
        self._axis = 0
        self.idxSlice = 0
        self.idxSlicelimt = self.datas.shape[0]
        # print(self.datas.shape[0])
        #=======================================================================
        self.initOperationButton()
        self.initDisplayfacePlane()
        self.choiceOpreationMod()

        pass

    def initOperationButton(self):
        self.faceCombox = QComboBox(self)
        self.faceCombox.addItem(self.faceList[0])
        self.faceCombox.addItem(self.faceList[1])
        self.faceCombox.addItem(self.faceList[2])
        self.faceCombox.setCurrentIndex(self._face)
        self.faceCombox.activated[str].connect(self.item_Choice)
        self.faceCombox.move((self.width() - self.faceCombox.width()), 0)

        self.modCombox = QComboBox(self)
        self.modCombox.addItem('Normal')
        self.modCombox.addItem('Region')
        self.modCombox.setCurrentIndex(self.OperationMod)
        self.modCombox.activated[str].connect(self.mod_Choice)
        self.modCombox.move((self.width() - self.faceCombox.width()-self.modCombox.width()), 0)

        self.sBar = QScrollBar(Qt.Horizontal, self)
        self.sBar.setGeometry(0, 52, 488, 10)
        self.sBar.setMaximum(255)
        self.sBar.sliderMoved.connect(self.sliderval)

        self.sBar2 = QScrollBar(Qt.Horizontal,self)
        self.sBar2.setGeometry(0, 40, 488, 10)
        self.sBar2.setMaximum(255)
        self.sBar2.sliderMoved.connect(self.sliderval)



        pass

    def sliderval(self):
        print(self.sBar.value(), self.sBar2.value())
        pass

    def mod_Choice(self, event):
        if event == 'Normal':
            self.OperationMod = 0
            # print('N')
        elif event == 'Region':
            self.OperationMod = 1
            # print('R')
        self.choiceOpreationMod()
        pass

    def item_Choice(self, event):
        if event == self.faceList[0]:
            self.topfaceView()
        elif event == self.faceList[1]:
            self.leftfaceView()
        elif event == self.faceList[2]:
            self.frontfaceView()
        self.choiceOpreationMod()
        pass

    #==========================MakeSureDisplayMod=============================
    def choiceDisplayMod(self):
        if self.OperationMod == 0:
            self.drawNomralArea()
        elif self.OperationMod == 1:
            self.drawGrowingArea()
        pass
    #=========================================================================

    def choiceOpreationMod(self):
        if self.OperationMod == 0:
            self.imLable.mouseMoveEvent = self.normalModMouseMoveEvent
            self.imLable.wheelEvent = self.NormalWheelEvent
        elif self.OperationMod == 1:
            self.imLable.mouseMoveEvent = self.regionModMouseMoveEvent
            self.imLable.wheelEvent = self.regionGrowingWheelEvent
        self.choiceDisplayMod()
        pass

    def initDisplayfacePlane(self):
        if self._face == 0:
            self.topfaceView()
        elif self._face == 1:
            self.leftfaceView()
        elif self._face == 2:
            self.frontfaceView()
        pass

    def topfaceView(self):
        self.datas = self._datas.copy()
        self.idxSlicelimt = self.datas.shape[0]
        self.faceWindowH = self.faceWindowV = 512
        tmpPalete = QPalette()
        tmpPalete.setColor(QPalette.Background, QColor(0, 0, 0))
        self.setPalette(tmpPalete)
        pass

    def leftfaceView(self):
        self.datas = self._datas.copy()
        self.datas = np.rot90(self.datas, -1)
        self.datas = np.rot90(self.datas,  axes=(0, 2))
        self.idxSlicelimt = self.datas.shape[0]
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
        self.datas = self._datas.copy()
        self.datas = np.rot90(self.datas, -1)
        self.idxSlicelimt = self.datas.shape[0]
        tmpPalete = QPalette()
        tmpPalete.setColor(QPalette.Background, QColor(0, 0, 0))
        self.setPalette(tmpPalete)
        self.faceWindowH = 512
        self.faceWindowV = self.faceWindowH * self.zSpacing
        pass

    def drawNomralArea(self):
        self.idxSlice = np.clip(self.idxSlice, 0, self.idxSlicelimt -1)
        self.imData = self.datas[self.idxSlice]
        self.displayDicomImage()
        pass

    def drawGrowingArea(self):
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


        self.imData = MyNarray
        self.displayDicomImage()

        pass

#==============================Use for display dicom image=================================
    def displayDicomImage(self):
        if self.imData is not None:
            raw_data = self.imData
            shape = self.imData.shape
            # maxNum = max(shape)
            # minNum = min(shape)
            raw_data[raw_data < 0] = 0
            raw_data[raw_data > 255] = 255
            if len(shape) >= 3:
                data = raw_data
                #=================用于调节对比度的方法=======================
                # data = (raw_data - self._low_hu) / self.window_width * 256
                #===========================================================
                data = data.astype(np.int8)
                tmpImage = QImage(data, shape[1], shape[0], shape[1] * shape[2], QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(tmpImage)
                pixmap = pixmap.scaled(self.faceWindowH, self.faceWindowV)
                self.imLable.setPixmap(pixmap)
            elif len(shape) < 3:
                data = raw_data
                data = data.astype(np.int8)
                tmpImage = QImage(data, shape[1], shape[0],  QImage.Format_Grayscale8)
                tmpImage.setColorTable(self._color_table)
                pixmap = QPixmap.fromImage(tmpImage)
                pixmap = pixmap.scaled(self.faceWindowH, self.faceWindowV)
                self.imLable.setPixmap(pixmap)
        pass

    def normalModMouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            xAxis = event.pos().x()
            yAxis = event.pos().y()
        self.choiceDisplayMod()
        pass

    def regionModMouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            xAxis = event.pos().x()
            yAxis = event.pos().y()
            self.PosXY[0] = xAxis
            self.PosXY[1] = yAxis
            self.lstSeeds = [(self.PosXY[0], self.PosXY[1])]
            # self.drawGrowingArea()
        self.choiceDisplayMod()
        pass

    def getResizeEvent(self, sizeX, sizeY):
        self.resize(sizeX, sizeY)
        pass

    def resizeEvent(self, QResizeEvent):
        # self.resize(self.width(), self.width())
        self.imLable.move(self.width() / 2 - self.imLable.width() / 2, self.height() / 2 - self.imLable.width() / 2)
        pass

    def regionGrowingWheelEvent(self, event):
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

        self.choiceDisplayMod()
        pass

    def NormalWheelEvent(self, event):
        angle = event.angleDelta() / 8
        angleX = angle.x()
        angleY = angle.y()
        if angleY > 0:
            self.idxSlice = np.clip(self.idxSlice + 1, 0, self.idxSlicelimt - 1)
        elif angleY < 0:
            self.idxSlice = np.clip(self.idxSlice - 1, 0, self.idxSlicelimt - 1)

        self.choiceDisplayMod()
        pass

    @property
    def window_width(self):
        """
        :rtype: float
        """
        return self._high_hu - self._low_hu


#=======================================================================================================================
# pathDicom = "D:/Dicomfile/MT_07/"
# idxSlice = 50
# reader = SimpleITK.ImageSeriesReader()
# filenamesDICOM = reader.GetGDCMSeriesFileNames(pathDicom)
#
# reader.SetFileNames(filenamesDICOM)
# imgOriginals = reader.Execute()
# datas = SimpleITK.GetArrayFromImage(imgOriginals)
# Spacing = imgOriginals.GetSpacing()
#
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     win = dicomImage2DdisplayWidget(face=0, datas= datas, spacing=Spacing)
#     win.show()
#     sys.exit(app.exec_())