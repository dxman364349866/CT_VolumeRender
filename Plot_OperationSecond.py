
import os

import math
import matplotlib
import numpy as np
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QPushButton
from PyQt5.QtGui import QPainter, QColor
from PyQt5.Qt import Qt

import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import sys


class drawPlotinform(QtWidgets.QMainWindow):
    DrawSignal = QtCore.pyqtSignal(list)
    def __init__(self,parent = None):
        super(drawPlotinform, self).__init__(parent)
        # 重新调整大小
        self.plotRight = 3000
        self.plotLeft = 0
        self.plotTop = 1.0
        self.plotDown = 0.0
        self.isRelease = True

        self.setWindowTitle('密度控制')
        self.setWindowIcon(QtGui.QIcon('../Atomic_Icon/area.ico'))
        self.isControlPoint = None
        self.isControlLeftValue = self.plotLeft
        self.isControlRightValue = self.plotRight

        # self.resize(300, 300)
        self.setGeometry(0, 0, 300, 300)
        self.canChange = False

        subWin = QtWidgets.QWidget()

        self.splitter = QtWidgets.QSplitter(Qt.Vertical)
        self.setCentralWidget(self.splitter)
        # self.hBox = QtWidgets.QHBoxLayout()
        # self.hBox.addWidget(self.splitter)


        self.setMouseTracking(True)

        # SavePoints
        self.points = [[self.plotLeft, 0], [self.plotRight, 0]]
        #绘制plot
        self.plot_()
        self.operationWin()

    def operationWin(self):

        self.DownW = QtWidgets.QWidget()
        button = QPushButton('节点',self.DownW)
        button.setGeometry(20, 0, 50, 20)


        # 创建强度控制器
        self.DownW.sliderTag = 0
        self.DownW.slider = QtWidgets.QSlider(Qt.Horizontal, self.DownW)
        self.DownW.slider.move(100, 20)
        self.DownW.enableSlider = False
        self.DownW.slider.setFocusPolicy(Qt.StrongFocus)
        self.DownW.slider.setTickPosition(QtWidgets.QSlider.TicksAbove)
        self.DownW.slider.setTickInterval(100)
        self.DownW.slider.setSingleStep(1)
        self.DownW.slider.setValue(50)
        self.DownW.slider.valueChanged[int].connect(self.IntenstyChange)


        # 创建下拉菜单
        self.DownW.comboBox = QtWidgets.QComboBox(self.DownW)
        self.DownW.comboBox.move(20, 20)
        self.DownW.comboBox.activated[str].connect(self.Item_choice)


        # palette1 = QtGui.QPalette()
        # palette1.setColor(QtGui.QPalette.Background, QColor(12, 66, 12))
        # self.DownW.setAutoFillBackground(True)
        # self.DownW.setPalette(palette1)

        self.splitter.addWidget(self.DownW)



    # 绘图方法
    def plot_(self):
        # 清屏
        plt.cla()
        # 获取绘图并绘制
        self.fig = plt.figure()
        self.ax =self.fig.add_axes([0.05, 0.05, 0.9, 0.9])
        # self.ax.hold(True)
        self.ax.grid(True)
        self.ax.set_xlim([self.plotLeft, self.plotRight])
        self.ax.set_ylim([self.plotDown, self.plotTop])
        cavans = FigureCanvas(self.fig)

        self.fig.canvas.mpl_connect('button_press_event', self.onMousePress)
        self.fig.canvas.mpl_connect('button_release_event', self.onMouseRelease)
        self.fig.canvas.mpl_connect('motion_notify_event', self.OnMouseMove)

        self.splitter.addWidget(cavans)


    def IntenstyChange(self, event):

        if self.DownW.enableSlider == True:
            self.points[self.DownW.sliderTag][0] = event
            self.onDrawLine()
            self.onDrawPoints()
            self.DrawSignal.emit(self.points)
        else:
            print('this is endge of the points')


    def Item_choice(self, event):
        text, num = event.split('_')
        num = int(num) - 1


        if num < len(self.points) - 1 and num > 0:
            self.DownW.enableSlider = True
            self.DownW.sliderTag = num
            self.DownW.slider.setMinimum(self.points[num - 1][0])
            self.DownW.slider.setMaximum(self.points[num + 1][0])
            self.DownW.slider.setValue(self.DownW.comboBox.itemData(num))
        else:
            self.DownW.enableSlider = False
            self.DownW.slider.setMinimum(0)
            self.DownW.slider.setMaximum(100)
            self.DownW.slider.setValue(50)


    def OnMouseMove(self,event):
        if event.xdata != None and event.ydata != None:
            if self.isRelease == False and self.isControlPoint == None:
                self.newPoint[0] = np.clip(event.xdata, self.isControlLeftValue, self.isControlRightValue)
                self.newPoint[1] = event.ydata
                if len(self.points) >= 2:
                    self.onDrawLine()
                self.onDrawPoints()
                self.DrawSignal.emit(self.points)

            elif self.isRelease == False and self.isControlPoint != None:
                self.isControlPoint[0] = np.clip(event.xdata, self.isControlLeftValue, self.isControlRightValue)
                self.isControlPoint[1] = event.ydata
                if len(self.points) >= 2:
                    self.onDrawLine()
                self.onDrawPoints()


    def onMouseRelease(self,event):
        self.isRelease = True
        self.isControlPoint = None
        # print(self.DownW.comboBox.itemData(0))
        # if event.button == 3 and len(self.points) > 0:
        self.setComboBox()

    def setComboBox(self):
        self.DownW.comboBox.clear()
        for i in range(0, len(self.points)):
            self.DownW.comboBox.addItem('位置_' + str(i + 1), self.points[i][0])


    def onMousePress(self, event):
        # 鼠标左键加点
        if event.button == 1:
            self.isRelease = False
            self.isControlPoint = self.nearestPoint([event.xdata, event.ydata])
            if self.isControlPoint == None:
                self.points.append([event.xdata, event.ydata])
                self.newPoint = self.points[len(self.points) - 1]
                self.sortPoints()
                self.nearestPoint([self.newPoint[0], self.newPoint[1]])


            self.onDrawLine()
            self.onDrawPoints()
            # self.fig.canvas.draw()

        # 鼠标右键删除点
        elif event.button == 3 and len(self.points) > 0:
            tmp = self.nearestPoint([event.xdata, event.ydata])
            if tmp:
                self.points.remove(tmp)
                plt.cla()
                self.ax.set_xlim([self.plotLeft, self.plotRight])
                self.ax.set_ylim([self.plotDown, self.plotTop])
                self.onDrawLine()
            self.onDrawLine()
            self.onDrawPoints()
            self.fig.canvas.draw()

    def onDrawPoints(self):
        tmpx = []
        tmpy = []
        for each in self.points:
            tmpx.append(each[0])
            tmpy.append(each[1])
        self.ax.plot(tmpx, tmpy, '.', color='blue')
        if self.isControlPoint != None :
            self.ax.plot(self.isControlPoint[0], self.isControlPoint[1], 'o', color='red')
        self.fig.canvas.draw()

    def onDrawLine(self):

        plt.cla()
        self.ax.grid(True)
        self.ax.set_xlim([self.plotLeft, self.plotRight])
        self.ax.set_ylim([self.plotDown, self.plotTop])
        tmpx = []
        tmpy = []

        for i in range(0, len(self.points)):
            numx = self.points[i][0]
            tmpx.append(numx)
            numy = self.points[i][1]
            tmpy.append(numy)

        self.ax.plot(tmpx, tmpy, ':')
        self.fig.canvas.draw()

    def nearestPoint(self, point):
        if len(self.points) > 0:
            for idx, each in enumerate(self.points):
                length = self.countDistanc(point, each)
                if length < 9:
                    if idx != 0 and idx != len(self.points) - 1:
                        self.isControlLeftValue = self.points[idx - 1][0]
                        self.isControlRightValue = self.points[idx + 1][0]
                    elif idx == len(self.points) - 1:
                        self.isControlLeftValue = self.points[idx - 1][0]
                        self.isControlRightValue = self.plotRight
                    elif idx == 0:
                        self.isControlLeftValue = self.plotLeft
                        self.isControlRightValue = self.points[idx + 1][0]
                    return each
            return None
        else:
            print('sorry points is empty')
            return None

    def countDistanc(self, object, target):
        x = target[0] - object[0]
        y = target[1] - object[1]
        length = math.sqrt(x ** 2 + y ** 2)
        return length

    #   对点进行排序
    def sortPoints(self):
        self.points.sort(key=self.takeFirst)

    def takeFirst(self, elem):
        return elem[0]


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main_window = drawPlotinform()
    main_window.show()
    app.exec()