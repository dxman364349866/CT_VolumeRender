from PyQt5.QtWidgets import QWidget, QApplication, QSplitter, QMainWindow, QHBoxLayout, QColorDialog
from PyQt5.QtCore import Qt
import sys
import struct
import math
import numpy as np

import matplotlib
import numpy as np
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle
from PyQt5.QtCore import pyqtSignal


class pltComponent(QMainWindow):
    updateItemSignal = pyqtSignal(bool)
    pointsSignal = pyqtSignal(list)
    colorsSignal = pyqtSignal(list)
    def __init__(self, **kwargs):
        super(pltComponent, self).__init__()
        self.setGeometry(50, 50, 512, 512)
        self.setWindowTitle('DensityOperation')
        self.plotRight = 3000
        self.plotLeft = 0
        self.plotTop = 1.0
        self.plotDown = 0.0

        self.points = kwargs.get('points', None)
        self.pColor = kwargs.get('colors', None)
        self.gOpacity = kwargs.get('gOpacity', None)

        self.initUI()
    def initUI(self):
        self.QS = QSplitter(Qt.Vertical)
        self.setCentralWidget(self.QS)
        self.line = None
        self.line2 = None
        # ===============Use set points=============
        self.upMarkerts = []
        self.downMarkerts = []
        self.downOpaicity = []
        self.currentMarkerts =[]
        #================Use set aix================
        self.currentAx = None
        self.currentMark = None
        self.currentMarkSize = None
        self.drawlocation = None
        self.edgeColor = 'b'

        self.isPicked = False
        self.isChoiceColor = False
        self.pickedIdex = -1
        self.pickedleft = -1
        self.pickedRight = -1


        self.initPlot()
        pass

    def initPlot(self):
        plt.cla()
        self.fig = plt.figure()
        cavans = FigureCanvas(self.fig)

        self.upPointsize = 20
        self.downPointSize = 99
        self.upPointMarker = 'o'
        self.downPointMarker = '^'
        self.edgeWidth = 1
        self.alpha = 0.9



        self.ax = self.fig.add_axes([0.05, 0.4, 0.9, 0.5])
        self.ax2 = self.fig.add_axes([0.05, 0.05, 0.9, 0.2])

        self.setAxsLim()
        self.QS.addWidget(cavans)

        self.sortPoints()
        self.drawPoints(self.points, self.pColor, self.pickedIdex)
        self.fig.canvas.mpl_connect('pick_event', self.onpick)
        self.fig.canvas.mpl_connect('button_press_event', self.onMousePress)
        self.fig.canvas.mpl_connect('button_release_event', self.onMouseRelased)
        self.fig.canvas.mpl_connect('motion_notify_event', self.mouseMoved)
        self.fig.canvas.mpl_connect('axes_enter_event', self.onEnterfigure)
        self.fig.canvas.mpl_connect('axes_leave_event', self.onLeavefigure)
        self.ax.grid(True)

    def setAxsLim(self):
        self.ax.set_xlim([self.plotLeft, self.plotRight])
        self.ax.set_ylim([self.plotDown, self.plotTop])

        self.ax2.set_xlim([self.plotLeft, self.plotRight])
        self.ax2.set_ylim([self.plotDown, 1])
        pass

    def drawPoints(self, points, color, pickindex):
        self.ax.clear()
        self.ax2.clear()
        self.upMarkerts.clear()
        self.downMarkerts.clear()
        self.setAxsLim()
        tmpYaxis = 0.5
        tmpMarker = 'H'
        if self.points == None:
            return True

        if pickindex == -1:
            for i in range(0, len(points)):
                tcolors = [color[i][1], color[i][2], color[i][3]]
                self.upMarkerts.append(self.ax.scatter(points[i][0], points[i][1], s=self.upPointsize, marker=self.upPointMarker, color=tcolors, linewidths=self.edgeWidth, edgecolors=self.edgeColor, alpha=self.alpha, picker=True))
                self.downMarkerts.append(self.ax2.scatter(points[i][0], tmpYaxis, s=self.downPointSize, marker=self.downPointMarker, color=tcolors, linewidths=self.edgeWidth, edgecolors=self.edgeColor, alpha=self.alpha, picker=True))
        else:
            for i in range(0, len(points)):
                if i != self.pickedIdex:
                    self.edgeColor = 'b'
                    tcolors = [color[i][1], color[i][2], color[i][3]]
                    self.upMarkerts.append(
                        self.ax.scatter(points[i][0], points[i][1], s=self.upPointsize, marker=self.upPointMarker, color=tcolors, linewidths=self.edgeWidth,
                                        edgecolors=self.edgeColor, alpha=self.alpha, picker=True))
                    self.downMarkerts.append(
                        self.ax2.scatter(points[i][0], tmpYaxis, s=self.downPointSize, marker=self.downPointMarker, color=tcolors, linewidths=self.edgeWidth,
                                         edgecolors=self.edgeColor, alpha=self.alpha, picker=True))

                else:
                    self.edgeColor = 'r'
                    tcolors = [color[self.pickedIdex][1], color[self.pickedIdex][2], color[self.pickedIdex][3]]
                    self.upMarkerts.append(
                        self.ax.scatter(points[self.pickedIdex][0], points[self.pickedIdex][1], s=self.upPointsize + 60, marker=self.upPointMarker, color=tcolors, linewidths=self.edgeWidth,
                                        edgecolors=self.edgeColor, alpha=self.alpha, picker=True))
                    self.downMarkerts.append(
                        self.ax2.scatter(points[self.pickedIdex][0], tmpYaxis, s=self.downPointSize + 100, marker=self.downPointMarker, color=tcolors, linewidths=self.edgeWidth,
                                         edgecolors=self.edgeColor, alpha=self.alpha, picker=True))


        self.drawLine(self.points)
        self.ax.grid(True)
        self.fig.canvas.draw()

    def drawLine(self, points):

        tmpx = []
        tmpy = []
        for i in range(0, len(points)):
            numx = points[i][0]
            tmpx.append(numx)
            numy = points[i][1]
            tmpy.append(numy)


        tmpx.insert(0, -sys.maxsize)
        tmpy.insert(0, points[0][1])

        tmpx.append(sys.maxsize)
        tmpy.append(points[len(points)-1][1])
        self.ax.plot(tmpx, tmpy, ':')

        pass

    def onLeavefigure(self,event):
        self.currentMarkerts = None
        self.currentAx = None
        self.currentMark = None
        self.currentMarkSize = None
        pass

    def onEnterfigure(self, event):
        if event.inaxes == self.ax:
            self.currentMarkerts = self.upMarkerts
            self.currentAx = self.ax
            self.currentMark = 'o'
            self.currentMarkSize = self.upPointsize

        elif event.inaxes == self.ax2:
            tmpx = event.xdata
            tmpy = event.ydata

            self.currentMarkerts = self.downMarkerts
            self.currentAx = self.ax2
            self.currentMark = '^'
            self.currentMarkSize = self.downPointSize
        else:
            self.currentAx = None
        pass

#===============Mouse Event=================
    def onMouseRelased(self, event):
        self.edgeColor = 'b'
        if event.button == 3:
            self.pickedIdex = -1
            self.isPicked = False

        if event.button == 1:
            self.isChoiceColor = False
            self.isPicked = False

        self.sortPoints()
        self.drawPoints(self.points, self.pColor, -1)
        self.emitSignles()

        pass

    def onMousePress(self, event):

        if event.button == 3 and self.isPicked == True:
            del self.points[self.pickedIdex]
            del self.pColor[self.pickedIdex]
            self.updateItemSignal.emit(True)

        elif event.button == 1 and \
                self.isPicked == False and \
                self.isChoiceColor == False and \
                self.currentMarkerts == self.upMarkerts:
            x = event.xdata
            y = event.ydata
            point = [x, y]
            color = [x, 0, 0, 0]
            self.points.append(point)
            self.pColor.append(color)
            self.updateItemSignal.emit(True)


        elif event.button == 3 and self.isPicked == False:
            print('Event button 3 and self.isPicked')
            pass
        else:
            pass
        pass

    def mouseMoved(self, event):
        if self.isPicked == True and event.button == 1 and  self.currentAx != None:
            x = event.xdata
            y = event.ydata
            self.points[self.pickedIdex][0] = x
            self.points[self.pickedIdex][1] = y
            self.pColor[self.pickedIdex][0] = x
            self.drawPoints(self.points, self.pColor, self.pickedIdex)
            self.emitSignles()
            # 如果在非边缘点上的交换方法
            if self.pickedleft >= 0 and self.pickedRight >= 0 and self.pickedRight <= len(self.points)-1:
                distanceLeft = self.points[self.pickedIdex][0] - self.points[self.pickedleft][0]
                distanceRight = self.points[self.pickedRight][0] - self.points[self.pickedIdex][0]
                if distanceLeft < 0 and self.pickedleft >= 0:
                    tmpIdex = self.pickedIdex
                    self.pickedIdex = self.pickedIdex - 1
                    self.pickedleft = self.pickedleft - 1
                    self.pickedRight = tmpIdex
                    self.sortPoints()
                elif distanceRight < 0 and self.pickedRight <= len(self.points)-1:
                    tmpIdex = self.pickedIdex
                    self.pickedIdex = self.pickedIdex + 1
                    self.pickedRight = self.pickedRight + 1
                    self.pickedleft = tmpIdex
                    self.sortPoints()
                else:
                    return True

            # 在边缘点上的交换方法
            elif self.pickedleft < 0:
                distanceRight = self.points[self.pickedRight][0] - self.points[self.pickedIdex][0]
                if distanceRight < 0:
                    tmpIdex = self.pickedIdex
                    self.pickedIdex = self.pickedIdex + 1
                    self.pickedRight = self.pickedRight + 1
                    self.pickedleft = tmpIdex
                    self.sortPoints()
            elif self.pickedRight > len(self.points)-1 or self.pickedRight < 0:
                distanceLeft = self.points[self.pickedIdex][0] - self.points[self.pickedleft][0]
                if distanceLeft < 0:
                    tmpIdex = self.pickedIdex
                    self.pickedIdex = self.pickedIdex - 1
                    self.pickedleft = self.pickedleft - 1
                    self.pickedRight = tmpIdex
                    self.sortPoints()
            else:
                print('Move Point error! on the part of exchange point ')
        else:
            print('Nothing has choiced')
            pass


        pass

#================pick event====================
    def onpick(self, event):
        if self.currentMarkerts == None:
            return True
        elif self.currentMarkSize == None:
            return True
        elif self.currentMark == None:
            return True
        elif self.currentAx == None:
            return True

        if self.currentMarkerts == self.downMarkerts:
            self.isPicked = False
            num = len(self.currentMarkerts)
            for i in range(0, num):
                if event.artist == self.currentMarkerts[i]:
                    self.pickedIdex = i
                    self.isChoiceColor = True
                    self.choiceColor()
                    self.drawPoints(self.points, self.pColor, self.pickedIdex)
                    return True


        elif self.currentMarkerts == self.upMarkerts:
            num = len(self.currentMarkerts)
            for i in range(0, num):
                if event.artist == self.currentMarkerts[i]:
                    self.isPicked = True
                    self.pickedIdex = i
                    if i > 0 and i < num - 1:
                        self.pickedleft = i - 1
                        self.pickedRight = i + 1
                    elif i == num-1:
                        self.pickedleft = i - 1
                        self.pickedRight = -1
                    elif i == 0:
                        self.pickedleft = -1
                        self.pickedRight = i + 1
                    else:
                        print('pickedNum error')
                    self.drawPoints(self.points, self.pColor, self.pickedIdex)
                    return True
        else:
            self.isPicked = False

#===========================================

#================SortOfpoints===============
    def sortPoints(self):
        if self.points !=None:
            self.points.sort(key=self.takeFirst)
            self.pColor.sort(key=self.takeFirst)

    def takeFirst(self, elem):
        return elem[0]

#===========================================


#===============ChangeColor====================
    def choiceColor(self):
        col = QColorDialog.getColor()
        got = np.array(self.hex_to_rgb(col.name()))
        self.pColor[self.pickedIdex][1] = got[0]
        self.pColor[self.pickedIdex][2] = got[1]
        self.pColor[self.pickedIdex][3] = got[2]
        self.drawPoints(self.points, self.pColor,  -1)
        self.emitSignles()
#==============================================

#========== 字符串转RGB元素范围(0-1)============
    def hex_to_rgb(self,hex_str):
        int_tuple = struct.unpack('BBB', bytes.fromhex(hex_str[1:]))
        return tuple([val / 255 for val in int_tuple])
#==============================================

    def emitSignles(self):
        self.pointsSignal.emit(self.points)
        self.colorsSignal.emit(self.pColor)