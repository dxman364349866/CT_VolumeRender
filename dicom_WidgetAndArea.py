import sys
import math
import SimpleITK
import numpy as np
from PyQt5.QtWidgets import QWidget, QLabel, QApplication, QGridLayout, \
    QHBoxLayout, QVBoxLayout, QPushButton, QComboBox, QScrollBar, QBoxLayout, \
    QDialogButtonBox, QGroupBox, QShortcut
from PyQt5.QtGui import QPixmap, QImage, QIcon, qRgb, QPalette, QColor, QKeySequence, \
    QPainter, QBrush, QPen
from PyQt5.QtCore import QRect, QPropertyAnimation, QPointF, pyqtProperty, QPoint
from PyQt5.QtCore import Qt, pyqtSignal

from Plot_RangeSlider import QRangeSlider

# ==解决pyqt5异常只要进入事件循环,程序就崩溃,而没有任何提示==
import cgitb
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

        self.seedsColors = []
        self.baseImageSize = 512
        self.regionDrawMod = 0

        #===============Regioin draw tool parmeter===================
        self.drawPanterbegin = QPoint()
        self.drawPanterEnd = QPoint()
        self.posX = 0
        self.posY = 0

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
        self.facePlane = ['mainFaceplane', 'leftFaceplane', 'frontFaceplane']
        self.idxSlice = 100

        self.currentFace = self.facePlane[self._face]
        #============================RegionGrowingParameter=====================
        self.PosXY = [150, 75]
        self.seedList = [(self.PosXY[0], self.PosXY[1])]
        self.seedSelectNum = 0

        self.LowAndUpper = [10, 3000]
        self.regionArea = []
        self.regionDrawSize = 5

        self.idxSlicelimt = self.datas.shape[0]
        # print(self.datas.shape[0])
        #=======================================================================
        self.initOperationButton()
        self.initDisplayfacePlane()
        self.choiceOpreationMod()

        pass

    def initOperationButton(self):
        self.facePlanes = QComboBox(self)
        self.facePlanes.addItem(self.facePlane[0])
        self.facePlanes.addItem(self.facePlane[1])
        self.facePlanes.addItem(self.facePlane[2])
        self.facePlanes.setCurrentIndex(self._face)
        # self.facePlanes.activated[str].connect(self.faceItem_Choice)
        self.facePlanes.currentTextChanged.connect(self.faceItem_Choice)
        self.facePlanes.keyPressEvent = self.customComboxKeyEvent
        self.facePlanes.move((self.width() - self.facePlanes.width()), 0)

        #==================================Active keyBoard event without combobox=======================
        # shorcut = QShortcut(QKeySequence(Qt.Key_F), self.facePlanes, activated=self.useforTestKeyEvent)
        #===============================================================================================

        #================================== Contrul region seed up and low range =======================
        regionWide = QRangeSlider(self)
        regionWide.setMax(255)
        regionWide.setMin(0)
        regionWide.setStart(150)
        regionWide.setEnd(255)
        regionWide.setRange(0, 255)
        regionWide.setDrawValues(True)
        regionWide.setBackgroundStyle('background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #222, stop:1 #333);')
        regionWide.handle.setStyleSheet('background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #8EE5EE, stop:1 #393);')
        regionWide.startValueChanged.connect(self.rangeSliderStartVolue)
        regionWide.endValueChanged.connect(self.rangeSliderEndVolue)
        #===============================================================================================

        self.modCombox = QComboBox(self)
        self.modCombox.addItem('Normal')
        self.modCombox.addItem('Region')
        self.modCombox.setCurrentIndex(self.OperationMod)
        # self.modCombox.activated[str].connect(self.mod_Choice)
        self.modCombox.currentTextChanged.connect(self.mod_Choice)
        self.modCombox.keyPressEvent = self.customComboxKeyEvent
        self.modCombox.move((self.width() - self.facePlanes.width() - self.modCombox.width()), 0)

        self.layerScrollBar = QScrollBar(Qt.Horizontal, self)
        self.layerScrollBar.setGeometry(0, 0, 128, 5)
        self.layerScrollBar.setMinimum(0)
        self.layerScrollBar.setMaximum(min(self.datas.shape))
        self.layerScrollBar.setValue(0)
        self.layerScrollBar.sliderMoved.connect(self.selectLayer)

        self.BaseBoxLayout = QBoxLayout(QBoxLayout.TopToBottom)
        self.BaseBoxLayout.addWidget(self.layerScrollBar, 0)
        self.BaseBoxLayout.addWidget(regionWide, 1)
        self.BaseBoxLayout.setAlignment(Qt.AlignTop)


        self.secondBoxLayout = QBoxLayout(QBoxLayout.LeftToRight)
        self.secondBoxLayout.addLayout(self.BaseBoxLayout)
        self.secondBoxLayout.addWidget(self.modCombox)
        self.secondBoxLayout.addWidget(self.facePlanes)
        self.secondBoxLayout.setAlignment(Qt.AlignTop)

        self.groupbox = QGroupBox(self)
        self.groupbox.setGeometry(28, -64, 512, 64)
        self.groupbox.setLayout(self.secondBoxLayout)

        self.showButton = QPushButton(self)
        self.showButton.setGeometry(0, 0, 16, 16)
        self.showButton.clicked.connect(self.playAnimation)


        self.initAnimation()
        pass

    def setGroup_pos(self, apos):
        self.groupbox.move(apos.x(), apos.y())
        pass

    def setSeedsColor(self, colorList):

        self.seedList.clear()
        self.seedsColors.clear()
        for i in range(0, len(colorList)):
            self.seedsColors.append(colorList[i][0])
            self.seedList.append(colorList[i][1])

        print('Color: ', self.seedsColors)
        print('--------------------------------')
        print('Seeds: ', self.seedList)
        pass

    def selectSeedinList(self, num):
        # tmpS = self.seedList[num]
        # tmpC = self.seedsColors[num]
        self.seedSelectNum = num
        print(self.seedsColors)
        print(self.seedList)
        # print('number is :', num)
        # print(tmpC, tmpS)
        pass

    def rangeSliderStartVolue(self, event):
        self.LowAndUpper[0] = event
        self.choiceDisplayMod()
        print(event)
        pass

    def rangeSliderEndVolue(self, event):
        self.LowAndUpper[1] = event
        self.choiceDisplayMod()
        print(event)
        pass

    def viewSeedinList(self, event):
        if event[0] == True:
            print('Open eye is:', event[1])
        elif event[0] == False:
            print('Close eye is:', event[1])
        else:
            print('viewSeedinList error.....')

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
        print('-----PlayAnimation-----')
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
        self.idxSlice = self.layerScrollBar.value()
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
        elif event == 'Region':
            self.OperationMod = 1
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


    def faceItem_Choice(self, faceEvent):
        
        if faceEvent == self.facePlane[0]:
            self.topfaceView()
            self.currentFace = self.facePlane[0]
            print('main view')
        elif faceEvent == self.facePlane[1]:
            self.leftfaceView()
            self.currentFace = self.facePlane[1]
            print('left view')
        elif faceEvent == self.facePlane[2]:
            self.frontfaceView()
            self.currentFace = self.facePlane[2]
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
        elif self.OperationMod == 1:
            self.imLable.mouseMoveEvent = self.regionModMouseMoveEvent
            self.imLable.mousePressEvent = self.regionModMousePressEvent
            self.imLable.mouseReleaseEvent = self.regionModMouseReleasedEvent

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
                                                           seedList=self.seedList,
                                                           lower=self.LowAndUpper[0],
                                                           upper=self.LowAndUpper[1],
                                                           replaceValue=1,
                                                           )
        self.regionArea = SimpleITK.GetArrayFromImage(self.imgWhiteMatter)
        self.drawGrowingAreaContour()
        pass

    def drawGrowingAreaContour(self):
        foreColorvalue = 1
        self.imgWhiteMatter = SimpleITK.GetImageFromArray(self.regionArea)
        self.imgWhiteMatterNoHoles = SimpleITK.VotingBinaryHoleFilling(image1=self.imgWhiteMatter,
                                                                       radius=[2] * 3,
                                                                       majorityThreshold=50,
                                                                       backgroundValue=0,
                                                                       foregroundValue=foreColorvalue)
        regionContour = SimpleITK.LabelContour(self.imgWhiteMatterNoHoles)
        # tmpWmatter = self.imgWhiteMatter
        # regionContour = tmpWmatter | regionContour
        tmpImage = SimpleITK.LabelOverlay(self.imgOriginal, regionContour)
        regionContourArray = SimpleITK.GetArrayFromImage(tmpImage)
        self.imData = regionContourArray
        self.displayDicomImage()

        # print(self.imgWhiteMatterNoHoles)
        # print('\n'.join(dir(self.imgWhiteMatterNoHoles)))

        pass

    #==============================Key board event ============================================
    def customComboxKeyEvent(self, event):
        print('ComboxKeyEvent')
        pass

    def useforTestKeyEvent(self):
        print('just test combobox key event')
        # self.displayDicomImage()
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

#=============================Region mod mouse Press and released event============================
    def regionModMousePressEvent(self, event):

        if event.buttons() == Qt.LeftButton and self.regionDrawMod != 0:
            xAxis = event.pos().x()
            yAxis = event.pos().y()
            if xAxis >= 0 and yAxis >= 0:
                tmpX = math.floor(xAxis * (self.baseImageSize / self.imLable.width()))
                tmpY = math.floor(yAxis * (self.baseImageSize / self.imLable.height()))
                if self.regionDrawMod == 1:
                    self.regionArea[tmpY - self.regionDrawSize:tmpY + self.regionDrawSize,
                    tmpX - self.regionDrawSize:tmpX + self.regionDrawSize] = 1
                elif self.regionDrawMod == 2:
                    self.regionArea[tmpY - self.regionDrawSize:tmpY + self.regionDrawSize,
                    tmpX - self.regionDrawSize:tmpX + self.regionDrawSize] = 0
            self.drawGrowingAreaContour()

        pass

    def regionModMouseReleasedEvent(self, Event):
        if Event.buttons() == Qt.RightButton:
            print('Right button released')
        pass
#==================================================================================================

#=====================================Region mod mouse move event==================================
    def regionModMouseMoveEvent(self, event):
        self.posX = event.pos().x()
        self.posY = event.pos().y()
        if event.buttons() == Qt.LeftButton and self.regionDrawMod == 0:
            if self.regionDrawMod == 0:
                xAxis = event.pos().x()
                yAxis = event.pos().y()
                if xAxis >= 0 and yAxis >= 0:
                    self.PosXY[0] = math.floor(xAxis * (self.baseImageSize / self.imLable.width()))
                    self.PosXY[1] = math.floor(yAxis * (self.baseImageSize / self.imLable.height()))
                    self.seedList[self.seedSelectNum] = (self.PosXY[0], self.PosXY[1])
                else:
                    print('Region Mod has Nagtive number')
        elif event.buttons() == Qt.LeftButton and self.regionDrawMod != 0:
            xAxis = event.pos().x()
            yAxis = event.pos().y()
            if xAxis >= 0 and yAxis >= 0:
                tmpX = math.floor(xAxis * (self.baseImageSize / self.imLable.width()))
                tmpY = math.floor(yAxis * (self.baseImageSize / self.imLable.height()))
                if self.regionDrawMod == 2:
                    # self.drawPanterbegin = tmpY - self.regionDrawSize
                    # self.drawPanterEnd = tmpX - self.regionDrawSize
                    # self.showDrawTool()
                    self.regionArea[tmpY - self.regionDrawSize:tmpY + self.regionDrawSize, tmpX - self.regionDrawSize:tmpX + self.regionDrawSize] = 0
                elif self.regionDrawMod == 1:
                    # self.drawPanterbegin = tmpY - self.regionDrawSize
                    # self.drawPanterEnd = tmpX - self.regionDrawSize
                    # self.showDrawTool()
                    self.regionArea[tmpY - self.regionDrawSize:tmpY + self.regionDrawSize, tmpX - self.regionDrawSize:tmpX + self.regionDrawSize] = 1
                else:
                    print('regionModMouseMoveEvent regionDrawMod error......')
                    return
            self.drawGrowingAreaContour()
            return
        else:
            print('regionModMouseMoveEvent error......')
        self.choiceDisplayMod()
        pass
#===================================================================================================


    def setScaleSize(self, maxnum, minnum):
        self.faceWindowH = maxnum
        self.faceWindowV = minnum * (max(self.xSpacing, self.ySpacing, self.zSpacing) / min(self.xSpacing, self.ySpacing, self.zSpacing))
        pass

    def getResizeEvent(self, sizeX, sizeY):
        if self.currentFace == self.facePlane[0]:
            tmpSize = min(sizeX, sizeY)
            self.imLable.resize(tmpSize, tmpSize)

        elif self.currentFace == self.facePlane[1]:
            #==================Resize Lable===================
            self.setScaleSize(min(sizeX, sizeY), min(sizeX, sizeY) * (min(self.datas.shape)/max(self.datas.shape)))
            self.imLable.resize(self.faceWindowH, self.faceWindowV)

        elif self.currentFace == self.facePlane[2]:
            self.setScaleSize(min(sizeX, sizeY), min(sizeX, sizeY) * (min(self.datas.shape) / max(self.datas.shape)))
            self.imLable.resize(self.faceWindowH, self.faceWindowV)

        #==================Move Lable=====================
        maxPosY = max(sizeY, self.imLable.height())
        minPoxY = min(sizeY, self.imLable.height())
        tmpPosX = np.clip((sizeX - sizeY), 0, max(sizeX, sizeY)) / 2
        tmpPosY = (maxPosY - minPoxY) / 2
        self.imLable.move(tmpPosX, tmpPosY)
        pass


    def regionGrowingWheelEvent(self, event):
        angle = event.angleDelta() / 8
        angleX = angle.x()
        angleY = angle.y()

        if angleY > 0:
            self.regionDrawSize += 1
        elif angleY < 0:
            self.regionDrawSize -= 1
        pass

    def setRegionDrawMod(self, event):
        if event == 0:
            self.regionDrawMod = 0
        elif event == 1:
            self.regionDrawMod = 1
        elif event == 2:
            self.regionDrawMod = 2
        else:
            print('setRegionDrawMod error....')
        pass

    def paintEvent(self, QPaintEvent):
        pen1 = QPen(Qt.blue, 1)
        q = QPainter(self)
        q.setPen(pen1)
        q.drawRect(self.posX - 25, self.posY - 25, 50, 50)
        print('draw ---------- draw')



    @property
    def window_width(self):
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