import sys
import math
import cv2
from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from Operation.dicom_widget_Eve import Dicom2Dwindow
from Operation.dicom_3DWidget import volumeWindow
from Operation.Plot_OperationSecond import drawPlotinform
from Operation.Plot_OparationWindow import plotWindow


class multDicomWindows(QWidget):

    def __init__(self, **kwargs):
        super(multDicomWindows, self).__init__()
        self._path = kwargs.get('path', None)
        self.initUI()

    def initUI(self):
        hbox = QHBoxLayout(self)
        self.topView = Dicom2Dwindow(dirPath=self._path, cutface=0)
        self.frontView = Dicom2Dwindow(dirPath=self._path, cutface=1)
        self.leftView = Dicom2Dwindow(dirPath=self._path, cutface=2)
        self.volumView = volumeWindow(dirPath=self._path)


        self.topView.pix_label.Drawsignle.connect(self.operationNebor1)
        self.leftView.pix_label.Drawsignle.connect(self.operationNebor2)
        self.frontView.pix_label.Drawsignle.connect(self.operationNebor3)


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

    def openOperationTool(self, tmpVopacity, tmpVcolor, tmpGopacity):
        self.drawplotWin = plotWindow(points= tmpVopacity, colors= tmpVcolor, gOpacity= tmpGopacity)
        self.drawplotWin.OperationPointsingle.connect(self.setOpacity)
        self.drawplotWin.OperationColorsingle.connect(self.setColors)
        pass

    def operationNebor1(self, event):

        if self.frontView != None:
            maxnum = max(self.frontView.datas.shape)
            self.frontView.pix_label.choiceNumber(event[1])
            self.frontView.pix_label.redrawLine(0, [event[0] * (self.frontView.pix_label.winSize[0]/maxnum), 0])
        if self.leftView != None:
            maxnum = max(self.leftView.datas.shape)
            self.leftView.pix_label.choiceNumber(event[0])
            self.leftView.pix_label.redrawLine(0, [event[1] * (self.leftView.pix_label.winSize[0]/maxnum), 0])

    def operationNebor2(self,event):
        if self.topView != None:
            maxnum = max(self.topView.datas.shape)
            minnum = min(self.topView.datas.shape)
            choicenum = minnum - math.floor((event[1] - self.leftView.pixAppendup) / self.leftView.pixScaleSize)
            # print(event[1], choicenum)
            self.topView.pix_label.choiceNumber(choicenum)
            self.topView.pix_label.redrawLine(1, [0, event[0]*(self.topView.pix_label.winSize[1]/maxnum)])

        if self.frontView != None:
            maxnum = max(self.frontView.datas.shape)
            self.frontView.pix_label.choiceNumber(event[0])
            self.frontView.pix_label.redrawLine(1, [0, event[1] * (self.frontView.pix_label.winSize[1] / maxnum)])
        pass
    def operationNebor3(self,event):
        if self.topView != None:
            maxnum = max(self.topView.datas.shape)
            minnum = min(self.topView.datas.shape)
            choicenum = minnum - math.floor((event[1] - self.leftView.pixAppendup) / self.leftView.pixScaleSize)
            self.topView.pix_label.choiceNumber(choicenum)
            self.topView.pix_label.redrawLine(0, [event[0]*(self.topView.pix_label.winSize[0]/maxnum), 0])
        if self.leftView != None:
            maxnum = max(self.leftView.datas.shape)
            self.leftView.pix_label.choiceNumber(event[0])
            self.leftView.pix_label.redrawLine(1, [0, event[1] * (self.leftView.pix_label.winSize[1]/maxnum)])

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