import sys
import math
import numpy as np
import cv2
from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from dicom_widget_Eve import Dicom2Dwindow
from dicom_3DWidget import volumeWindow
from Plot_OperationSecond import drawPlotinform
from Plot_OparationWindow import plotWindow


class multDicomWindows(QWidget):

    def __init__(self, **kwargs):
        super(multDicomWindows, self).__init__()
        self._path = kwargs.get('path', None)
        self.axisBounds = None
        self.initUI()

    def initUI(self):
        hbox = QHBoxLayout(self)
        self.topView = Dicom2Dwindow(dirPath=self._path, cutface=0)
        self.frontView = Dicom2Dwindow(dirPath=self._path, cutface=1)
        self.leftView = Dicom2Dwindow(dirPath=self._path, cutface=2)
        self.volumView = volumeWindow(dirPath=self._path)


        self.topView.pix_label.Drawsignle.connect(self.operationNebor1)
        self.topView.pix_label.Targetsignle.connect(self.EnterLocation1)

        self.leftView.pix_label.Drawsignle.connect(self.operationNebor2)
        self.leftView.pix_label.Targetsignle.connect(self.EnterLocation2)

        self.frontView.pix_label.Drawsignle.connect(self.operationNebor3)
        self.frontView.pix_label.Targetsignle.connect(self.EnterLocation3)



        splitter1 = QSplitter(Qt.Horizontal)
        splitter1.setGeometry(0, 0, 512, 512)

        splitter1.addWidget(self.leftView)
        splitter1.addWidget(self.topView)

        splitter2 = QSplitter(Qt.Horizontal)
        splitter2.setGeometry(0, 0, 512, 512)
        splitter2.addWidget(self.frontView)
        splitter2.addWidget(self.volumView)

        splitter3 = QSplitter(Qt.Vertical)
        splitter3.setSizes([512, 512])
        splitter3.addWidget(splitter2)
        splitter3.addWidget(splitter1)


        pe_gray = QPalette()
        pe_gray.setColor(QPalette.Background, Qt.gray)
        splitter3.setPalette(pe_gray)

        hbox.addWidget(splitter3)

        self.setLayout(hbox)
        self.setGeometry(300, 300, 1024, 720)
        self.setWindowTitle('3D viewer')
        self.show()
        self.initAxisBounds()

        self.volumView.drawPoint[0][0] = 0
        self.volumView.drawPoint[0][1] = 0
        self.volumView.drawPoint[0][2] = 0


    def initAxisBounds(self):
        self.axisBounds = np.array(self.volumView.volume.GetBounds())
        self.axisBounds = np.array(self.axisBounds[self.axisBounds != 0])

    def openOperationTool(self, tmpVopacity, tmpVcolor, tmpGopacity):
        self.drawplotWin = plotWindow(points= tmpVopacity, colors= tmpVcolor, gOpacity= tmpGopacity)
        self.drawplotWin.OperationPointsingle.connect(self.setOpacity)
        self.drawplotWin.OperationColorsingle.connect(self.setColors)
        pass

    def EnterLocation1(self, event):

        if self.volumView != None:
            shape = self.frontView.pix_label.volumeShape
            xAxis = event[0] / shape[0] * self.axisBounds[0]
            yAxis = self.axisBounds[1] - event[1] / shape[1] * self.axisBounds[1]

            self.volumView.drawPoint[0][0] = xAxis
            self.volumView.drawPoint[0][1] = yAxis
            self.volumView.drawFunction()

        if self.leftView != None:
            maxnum = max(self.leftView.datas.shape)
            self.leftView.pix_label.drawCoord2[0] = event[1] * self.leftView.pix_label.winSize[1] / maxnum
            # self.leftView.pix_label.drawCoord2[1] = self.frontView.pix_label.drawCoord2[1]
            self.leftView.pix_label.update_image()
        if self.frontView != None:
            maxnum = max(self.frontView.datas.shape)
            self.frontView.pix_label.drawCoord2[0] = event[0] * self.frontView.pix_label.winSize[0] / maxnum
            # self.frontView.pix_label.drawCoord2[1] = self.leftView.pix_label.drawCoord2[1]
            self.frontView.pix_label.update_image()

        pass
    def EnterLocation2(self, event):
        if self.volumView != None:
            shape = self.leftView.pix_label.volumeShape
            yAxis = self.axisBounds[0] - event[0] / shape[0] * self.axisBounds[0]
            movStep = event[1] - self.leftView.pixAppendup
            movSize = shape[1] - self.leftView.pixAppenddown - self.leftView.pixAppendup
            movRate = movStep / movSize
            zAxis = movRate * self.axisBounds[2]

            self.volumView.drawPoint[0][1] = yAxis
            self.volumView.drawPoint[0][2] = zAxis
            self.volumView.drawFunction()

        if self.topView != None:
            maxnum = max(self.topView.datas.shape)
            self.topView.pix_label.drawCoord2[1] = event[0] * self.topView.pix_label.winSize[0] / maxnum
            self.topView.pix_label.update_image()

        if self.frontView != None:
            maxnum = max(self.frontView.datas.shape)
            self.frontView.pix_label.drawCoord2[1] = event[1] * self.frontView.pix_label.winSize[1] / maxnum
            self.frontView.pix_label.update_image()

        pass
    def EnterLocation3(self, event):
        if self.volumView != None:
            shape = self.frontView.pix_label.volumeShape
            xAxis = event[0] / shape[0] * self.axisBounds[0]
            movStep = event[1] - self.frontView.pixAppenddown
            movSize = shape[1] - self.frontView.pixAppenddown - self.frontView.pixAppendup
            movRate = movStep / movSize
            zAxis = movRate * self.axisBounds[2]

            self.volumView.drawPoint[0][0] = xAxis
            self.volumView.drawPoint[0][2] = zAxis
            self.volumView.drawFunction()

        if self.leftView != None:
            maxnum = max(self.leftView.datas.shape)
            self.leftView.pix_label.drawCoord2[1] = event[1] * self.leftView.pix_label.winSize[1] / maxnum
            self.leftView.pix_label.update_image()
        if self.topView != None:
            maxnum = max(self.topView.datas.shape)
            self.topView.pix_label.drawCoord2[0] = event[0] * self.topView.pix_label.winSize[0] / maxnum
            self.topView.pix_label.update_image()

        pass

    def operationNebor1(self, event):
        if self.volumView != None:
            shape = self.topView.pix_label.volumeShape
            xAxis = event[0] / shape[0] * self.axisBounds[0]
            yAxis = self.axisBounds[1] - event[1] / shape[1] * self.axisBounds[1]
            self.volumView.drawPoint[1][0] = xAxis
            self.volumView.drawPoint[1][1] = yAxis
            self.volumView.drawFunction()
            #===================SetTopViewPositionAxisText==================
            self.topView.texPositionLabel.setText('x: ' + str(event[0]) + ' ' + 'y: ' + str(event[1]))


        if self.frontView != None:
            maxnum = max(self.frontView.datas.shape)
            self.frontView.pix_label.choiceNumber(event[1])
            self.frontView.pix_label.redrawLine(0, [event[0] * (self.frontView.pix_label.winSize[0]/maxnum), 0])
            #===================SetfrontViewPositionAxisText=================
            zAxis = self.frontView.pix_label.drawCoord[1]
            self.frontView.texPositionLabel.setText('x: ' + str(event[0]) + ' '+ 'z: ' + str(zAxis))

        if self.leftView != None:
            maxnum = max(self.leftView.datas.shape)
            self.leftView.pix_label.choiceNumber(event[0])
            self.leftView.pix_label.redrawLine(0, [event[1] * (self.leftView.pix_label.winSize[0]/maxnum), 0])

            #===================SetleftViewPositionAxisText=================
            zAxis = self.leftView.pix_label.drawCoord[1]
            self.leftView.texPositionLabel.setText('y: ' + str(event[1]) + ' ' + 'z: ' + str(zAxis))

    def operationNebor2(self,event):

        if self.volumView != None:
            shape = self.leftView.pix_label.volumeShape
            yAxis = self.axisBounds[0] - event[0] / shape[0] * self.axisBounds[0]
            movStep = event[1] - self.leftView.pixAppendup
            movSize = shape[1] - self.leftView.pixAppenddown - self.leftView.pixAppendup
            movRate = movStep / movSize
            zAxis = movRate * self.axisBounds[2]

            self.volumView.drawPoint[1][1] = yAxis
            self.volumView.drawPoint[1][2] = zAxis
            self.volumView.drawFunction()

            self.leftView.texPositionLabel.setText('y:' + str(event[0]) + ' ' + 'z: ' + str(event[1]))

        if self.topView != None:
            maxnum = max(self.topView.datas.shape)
            minnum = min(self.topView.datas.shape)
            choicenum = minnum - math.floor((event[1] - self.leftView.pixAppendup) / self.leftView.pixScaleSize)
            # print(event[1], choicenum)
            self.topView.pix_label.choiceNumber(choicenum)
            self.topView.pix_label.redrawLine(1, [0, event[0]*(self.topView.pix_label.winSize[1]/maxnum)])

            #===================SettopViewPositionAxisText=================
            xAxis = self.topView.pix_label.drawCoord[0]
            self.topView.texPositionLabel.setText('x: ' + str(xAxis) + ' ' + 'y: '+ str(event[0]))

        if self.frontView != None:
            maxnum = max(self.frontView.datas.shape)
            self.frontView.pix_label.choiceNumber(event[0])
            self.frontView.pix_label.redrawLine(1, [0, event[1] * (self.frontView.pix_label.winSize[1] / maxnum)])
            #===================SetfrontViewPositionAxisText=================
            xAxis = self.frontView.pix_label.drawCoord[0]
            self.frontView.texPositionLabel.setText('x:' + str(xAxis) + ' ' + 'z: ' + str(event[1]))
        pass

    def operationNebor3(self,event):
        if self.volumView != None:
            shape = self.frontView.pix_label.volumeShape
            xAxis = event[0] / shape[0] * self.axisBounds[0]
            movStep = event[1] - self.frontView.pixAppenddown
            movSize = shape[1] - self.frontView.pixAppenddown - self.frontView.pixAppendup
            movRate = movStep / movSize
            zAxis = movRate * self.axisBounds[2]
            self.volumView.drawPoint[1][0] = xAxis
            self.volumView.drawPoint[1][2] = zAxis
            self.volumView.drawFunction()

            self.frontView.texPositionLabel.setText('x:' + str(event[0]) + ' ' + 'z: ' + str(event[1]))

        if self.topView != None:
            maxnum = max(self.topView.datas.shape)
            minnum = min(self.topView.datas.shape)
            choicenum = minnum - math.floor((event[1] - self.leftView.pixAppendup) / self.leftView.pixScaleSize)
            self.topView.pix_label.choiceNumber(choicenum)
            self.topView.pix_label.redrawLine(0, [event[0]*(self.topView.pix_label.winSize[0]/maxnum), 0])
            #===================SettopViewPositionAxisText=================
            yAxis = self.topView.pix_label.drawCoord[1]
            self.topView.texPositionLabel.setText('x: ' + str(event[0]) + ' ' + 'y: '+ str(yAxis))

        if self.leftView != None:
            maxnum = max(self.leftView.datas.shape)
            self.leftView.pix_label.choiceNumber(event[0])
            self.leftView.pix_label.redrawLine(1, [0, event[1] * (self.leftView.pix_label.winSize[1]/maxnum)])
            #===================SetleftViewPositionAxisText=================
            xAxis = self.leftView.pix_label.drawCoord[0]
            self.leftView.texPositionLabel.setText('y:' + str(xAxis) + ' ' + 'z: ' + str(event[1]))
        pass
    def setOpacity(self, volume):
        self.volumView.setOpacityValue(volume)
        pass

    def setColors(self, volume):
        self.volumView.setOpacityColor(volume)
        pass

# def main():
#     app = QApplication(sys.argv)
#     exf = multDicomWindows()
#     sys.exit(app.exec_())
#
#
# if __name__ == '__main__':
#     main()