import sys
import math
import SimpleITK
import numpy as np
from dicom_data import DicomData
from PyQt5.QtWidgets import QWidget, QLabel, QApplication, QGridLayout, \
    QHBoxLayout, QVBoxLayout, QPushButton, QComboBox, QScrollBar, QBoxLayout, \
    QDialogButtonBox, QGroupBox
from PyQt5.QtGui import QPixmap, QImage, QIcon, qRgb, QPalette, QColor
from PyQt5.QtCore import QRect, QPropertyAnimation, QPointF, pyqtProperty
from Plot_RangeSlider import QRangeSlider
from PyQt5.QtCore import Qt, pyqtSignal


import cgitb

# ==解决pyqt5异常只要进入事件循环,程序就崩溃,而没有任何提示==
cgitb.enable(format='text')
#=========================================================

class dicomImage2DdisplayWidget(QWidget):
    addSeedsSignal = pyqtSignal(bool)
    def __init__(self, **kwargs):
        super(dicomImage2DdisplayWidget, self).__init__()
        self._face = kwargs.get('face', 0)
        self._datas = kwargs.get('datas', 0)
        self._Spacing = kwargs.get('spacing', None)
        self._low_hu = kwargs.get("low_hu", -1150)
        self._high_hu = kwargs.get("high_hu", 3250)
        self._axis = 0

        self.baseImageSize = 512

        self.initUI()


    def initUI(self):
        self.setGeometry(0, 0, self.baseImageSize, self.baseImageSize)

        self.viewLayout = None
        self.imLable = QLabel(self)
        self.imLable.setScaledContents(True)
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
        self.idxSlice = 100

        self.currentFace = self.faceList[self._face]
        #============================RegionGrowingParameter=====================
        self.PosXY = [150, 75]
        self.lstSeeds = [(self.PosXY[0], self.PosXY[1])]


        self.LowAndUpper = [10, 3000]

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

        # self.lowHusBar = QScrollBar(Qt.Horizontal, self)
        # self.lowHusBar.setGeometry(0, 52, 488, 5)
        # self.lowHusBar.setMaximum(3250)
        # self.lowHusBar.setMinimum(-1150)
        # self.lowHusBar.setValue(0)
        # self.lowHusBar.sliderMoved.connect(self.sliderval)
        #
        # self.heighHusBar = QScrollBar(Qt.Horizontal, self)
        # self.heighHusBar.setGeometry(0, 40, 488, 5)
        # self.heighHusBar.setMaximum(3250)
        # self.heighHusBar.setMinimum(-1150)
        # self.heighHusBar.setValue(0)
        # self.heighHusBar.sliderMoved.connect(self.sliderval)

        self.layerBar = QScrollBar(Qt.Horizontal, self)
        self.layerBar.setGeometry(0, 0, 512, 5)
        self.layerBar.setMinimum(0)
        self.layerBar.setMaximum(min(self.datas.shape))
        self.layerBar.setValue(0)
        self.layerBar.sliderMoved.connect(self.selectLayer)

        self.addSeedsButton = QPushButton(self)
        self.addSeedsButton.setGeometry(0, 0, 16, 16)
        self.addSeedsButton.clicked.connect(self.addSeedsEvent)

        self.BaseBoxLayout = QBoxLayout(QBoxLayout.TopToBottom)
        # self.BaseBoxLayout.addWidget(self.heighHusBar, 0)
        # self.BaseBoxLayout.addWidget(self.lowHusBar, 0)
        self.BaseBoxLayout.addWidget(self.layerBar, 0)
        self.BaseBoxLayout.setAlignment(Qt.AlignTop)

        self.secondBoxLayout = QBoxLayout(QBoxLayout.LeftToRight)
        self.secondBoxLayout.addLayout(self.BaseBoxLayout)
        self.secondBoxLayout.addWidget(self.modCombox)
        self.secondBoxLayout.addWidget(self.faceCombox)
        self.secondBoxLayout.addWidget(self.addSeedsButton)
        self.secondBoxLayout.setAlignment(Qt.AlignTop)

        self.groupbox = QGroupBox(self)
        self.groupbox.setGeometry(32, -64, 512, 64)
        self.groupbox.setLayout(self.secondBoxLayout)

        self.showButton = QPushButton(self)
        self.showButton.setGeometry(0, 0, 16, 16)
        self.showButton.clicked.connect(self.playAnimation)

        # self.imLable.setAlignment(Qt.AlignCenter)

        self.initAnimation()
        pass

    def setGroup_pos(self, apos):
        self.groupbox.move(apos.x(), apos.y())
        pass

    def addSeedsEvent(self):
        self.addSeedsSignal.emit(True)
        tmpSeed = (0, 0)
        self.lstSeeds.append(tmpSeed)
        # print(self.lstSeeds[0])
        # print('\n'.join(dir(self.lstSeeds)))
        pass

    def removeSeedEvent(self, num):
        self.lstSeeds.remove(self.lstSeeds[num])
        print(len(self.lstSeeds))
        pass

    def getSeedEvent(self, num):
        print('---------------->')
        print(num, self.lstSeeds[num])
        pass

    def initAnimation(self):
        self.isBoardshow = False
        xAxis = self.groupbox.pos().x()
        yAxis = self.groupbox.height()

        self.groupBoxAnim = QPropertyAnimation(self, b'pos')
        self.groupBoxAnim.setDuration(200)
        self.groupBoxAnim.setStartValue(QPointF(xAxis, -yAxis))
        # self.anim.setKeyValueAt(0.5, QPointF(0, 10))
        # self.anim.setKeyValueAt(0.8, QPointF(0, 80))
        self.groupBoxAnim.setEndValue(QPointF(xAxis, 0))

        self.reverGroupBoxAnim = QPropertyAnimation(self, b'pos')
        self.reverGroupBoxAnim.setDuration(200)
        self.reverGroupBoxAnim.setStartValue(QPointF(xAxis, 0))
        self.reverGroupBoxAnim.setEndValue(QPointF(xAxis, -yAxis))

        pass

    def playAnimation(self):
        print('-----Play-----')
        if self.isBoardshow == False:
            self.reverGroupBoxAnim.stop()
            self.groupBoxAnim.start()
            self.isBoardshow = True
        elif self.isBoardshow == True:
            self.groupBoxAnim.stop()
            self.reverGroupBoxAnim.start()
            self.isBoardshow = False
        pass
    pos = pyqtProperty(QPointF, fset=setGroup_pos)

    def selectLayer(self, event):
        self.idxSlice = self.layerBar.value()
        self.choiceDisplayMod()
        pass

    def sliderval(self):
        self._low_hu = self.lowHusBar.value()
        self._high_hu = self.heighHusBar.value()

        self.choiceDisplayMod()
        # print(self.sBar.value(), self.sBar2.value())
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

    def initDisplayfacePlane(self):
        if self._face == 0:
            self.topfaceView()
        elif self._face == 1:
            self.leftfaceView()
        elif self._face == 2:
            self.frontfaceView()
        pass

    def item_Choice(self, event):
        if event == self.faceList[0]:
            self.topfaceView()
            self.currentFace = self.faceList[0]
            print('main view')
        elif event == self.faceList[1]:
            self.leftfaceView()
            self.currentFace = self.faceList[1]
            print('left view')
        elif event == self.faceList[2]:
            self.frontfaceView()
            self.currentFace = self.faceList[2]
            print('front view')

        self.choiceOpreationMod()
        self.getResizeEvent(self.width(), self.height())
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



    def topfaceView(self):
        self.datas = self._datas.copy()
        self.idxSlicelimt = self.datas.shape[0]
        self.faceWindowH = self.faceWindowV = self.width()
        tmpPalete = QPalette()
        tmpPalete.setColor(QPalette.Background, QColor(0, 0, 0))
        self.setPalette(tmpPalete)
        pass

    def leftfaceView(self):
        self.datas = self._datas.copy()
        self.datas = np.rot90(self.datas, -1)
        self.datas = np.rot90(self.datas,  axes=(0, 2))
        self.idxSlicelimt = self.datas.shape[0]

        self.setScaleSize(max(self.datas.shape), min(self.datas.shape))

        tmpPalete = QPalette()
        tmpPalete.setColor(QPalette.Background, QColor(0, 0, 0))
        self.setPalette(tmpPalete)
        pass


    def frontfaceView(self):
        self.datas = self._datas.copy()
        self.datas = np.rot90(self.datas, -1)
        self.idxSlicelimt = self.datas.shape[0]

        width = self.datas.shape[0]
        height = self.datas.shape[1]
        depth = self.datas.shape[2]
        self.setScaleSize(max(width, height, depth), min(width, height, depth))

        tmpPalete = QPalette()
        tmpPalete.setColor(QPalette.Background, QColor(0, 0, 0))
        self.setPalette(tmpPalete)
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
                # print('---------Update3d--------')
                #===========================================================
                data = data.astype(np.int8)
                tmpImage = QImage(data, shape[1], shape[0], shape[1] * shape[2], QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(tmpImage)
                # pixmap = pixmap.scaled(self.faceWindowH , self.faceWindowV )
                # pixmap = pixmap.scaled(self.xSpacing, self.zSpacing)
                # pixmap = pixmap.scaled(1024, 128)
                self.imLable.setPixmap(pixmap)
            elif len(shape) < 3:
                data = raw_data
                # data = (raw_data - self._low_hu) / self.window_width * 256
                # print('---------Update2d---------')
                data = data.astype(np.int8)
                tmpImage = QImage(data, shape[1], shape[0],  QImage.Format_Grayscale8)
                tmpImage.setColorTable(self._color_table)
                pixmap = QPixmap.fromImage(tmpImage)
                # pixmap = pixmap.scaled(self.faceWindowH, self.faceWindowV)
                # pixmap = pixmap.scaled(self.xSpacing, self.zSpacing)
                # pixmap = pixmap.scaled(1024, 128)
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
            if xAxis >= 0 and yAxis >= 0:
                self.PosXY[0] = math.floor(xAxis * (self.baseImageSize / self.imLable.width()))
                self.PosXY[1] = math.floor(yAxis * (self.baseImageSize / self.imLable.height()))
                self.lstSeeds = [(self.PosXY[0], self.PosXY[1])]
                # tmpLow = math.floor(np.clip(tmpLow - 50, -1000, 3000))
                # tmpHig = math.floor(np.clip(tmpHig + 100, -1000, 3000))
                # self.LowAndUpper = [tmpLow, tmpHig]
                # print(self.LowAndUpper)
                print('-------------------------')
                print(self.lstSeeds[0])
                print('-------------------------')

            else:
                print('Region Mod has Nagtive number')
                pass

        self.choiceDisplayMod()
        pass

    def setScaleSize(self, maxnum, minnum):
        self.faceWindowH = maxnum
        self.faceWindowV = minnum * (max(self.xSpacing, self.ySpacing, self.zSpacing) / min(self.xSpacing, self.ySpacing, self.zSpacing))
        pass

    def getResizeEvent(self, sizeX, sizeY):
        if self.currentFace == self.faceList[0]:
            tmpSize = min(sizeX, sizeY)
            self.imLable.resize(tmpSize, tmpSize)

        elif self.currentFace == self.faceList[1]:
            #==================Resize Lable===================

            self.setScaleSize(min(sizeX, sizeY), min(sizeX, sizeY) * (min(self.datas.shape)/max(self.datas.shape)))
            self.imLable.resize(self.faceWindowH, self.faceWindowV)

        elif self.currentFace == self.faceList[2]:

            self.setScaleSize(min(sizeX, sizeY), min(sizeX, sizeY) * (min(self.datas.shape) / max(self.datas.shape)))
            self.imLable.resize(self.faceWindowH, self.faceWindowV)



        #==================Move Lable=====================
        maxPosY = max(sizeY, self.imLable.height())
        minPoxY = min(sizeY, self.imLable.height())
        tmpPosX = np.clip((sizeX - sizeY), 0, max(sizeX, sizeY)) / 2
        tmpPosY = (maxPosY - minPoxY) / 2
        self.imLable.move(tmpPosX, tmpPosY)
        pass

    # def resizeEvent(self, QResizeEvent):
    #     pass

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

        print(self.LowAndUpper)
        self.choiceDisplayMod()
        pass

    def NormalWheelEvent(self, event):
        # angle = event.angleDelta() / 8
        # angleX = angle.x()
        # angleY = angle.y()
        # if angleY > 0:
        #     self.idxSlice = np.clip(self.idxSlice + 1, 0, self.idxSlicelimt - 1)
        # elif angleY < 0:
        #     self.idxSlice = np.clip(self.idxSlice - 1, 0, self.idxSlicelimt - 1)
        #
        # # print(self.faceWindowH, self.faceWindowV)
        # self.choiceDisplayMod()
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