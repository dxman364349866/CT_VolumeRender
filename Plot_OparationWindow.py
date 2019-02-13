import sys
from PyQt5.QtWidgets import QWidget, \
    QApplication, QSplitter, QHBoxLayout, \
    QLabel, QSlider, QStyleFactory, \
    QFrame, QPushButton, QGroupBox, \
    QVBoxLayout, QGridLayout, QComboBox
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import Qt

from Plot_OperationComponent import pltComponent
from Plot_RangeSlider import QRangeSlider

class plotWindow(QWidget):
    OperationPointsingle = pyqtSignal(list)
    OperationColorsingle = pyqtSignal(list)

    def __init__(self, **kwargs):
        super(plotWindow, self).__init__()
        self.setGeometry(50, 50, 512, 512)
        self.setWindowTitle('密度控制器')
        self.hBox = QHBoxLayout(self)
        self._points = kwargs.get('points', None)
        self._pColors = kwargs.get('colors', None)
        self._gOpacity = kwargs.get('gOpacity', None)
        self.initUI()
        self.show()

    def initUI(self):

        self.getPoint = None

        self.spliiter = QSplitter(Qt.Vertical)
        self.OperatPlt = pltComponent(points=self._points, colors=self._pColors, gOpacity=self._gOpacity)
        self.OperatPlt.updateItemSignal.connect(self.updataItme)
        self.OperatPlt.pointsSignal.connect(self.updatePoints)
        self.OperatPlt.colorsSignal.connect(self.updateColors)
        self.spliiter.addWidget(self.OperatPlt)
        self.spliiter.addWidget(self.rangeSliderGroup())
        self.spliiter.addWidget(self.shiftSliderGroup())
        self.spliiter.addWidget(self.ditailSliderGroup())


        self.hBox.addWidget(self.spliiter)
        self.setLayout(self.hBox)
        pass

    def rangeSliderGroup(self):
        groupBox = QGroupBox('控制区间')

        rS = QRangeSlider()
        rS.setMax(3000)
        rS.setEnd(3000)
        rS.setStart(0)
        rS.setMin(-1000)
        rS.setRange(0, 1500)
        rS.setDrawValues(True)
        rS.setBackgroundStyle('background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #222, stop:1 #333);')
        rS.handle.setStyleSheet('background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #8EE5EE, stop:1 #393);')
        rS.endValueChanged.connect(self.rangeSliderEndVolue)
        rS.startValueChanged.connect(self.rangeSliderStartVolue)

        self.OperatPlt.plotLeft = rS.getRange()[0]
        self.OperatPlt.plotRight = rS.getRange()[1]
        self.changeControlArea()


        vbox = QVBoxLayout()
        vbox.addWidget(rS)
        vbox.addStretch(1)

        groupBox.setLayout(vbox)

        return groupBox

    def shiftSliderGroup(self):
        grouBox = QGroupBox('Shift')
        shiftSlider = QSlider(Qt.Horizontal)
        shiftSlider.setMaximum(3000)
        shiftSlider.setMinimum(-1000)
        shiftSlider.setValue(self._points[0][0])
        shiftSlider.valueChanged[int].connect(self.changeShiftSliderVolue)

        hBox = QHBoxLayout()
        hBox.addWidget(shiftSlider)
        grouBox.setLayout(hBox)
        return grouBox
        pass

    def ditailSliderGroup(self):
        grid = QGridLayout()
        groupBox = QGroupBox('细节控制')

        self.locationSlider = QSlider(Qt.Horizontal)
        self.locationSlider.setTickPosition(QSlider.TicksAbove)
        self.locationSlider.setMaximum(100)
        self.locationSlider.setMinimum(0)
        self.locationSlider.setValue(50)
        self.locationSlider.valueChanged[int].connect(self.locatonSliderVolume)

        self.opacitySlider = QSlider(Qt.Horizontal)
        self.opacitySlider.setTickPosition(QSlider.TicksBelow)
        self.opacitySlider.setRange(0, 300)
        self.opacitySlider.valueChanged.connect(self.opacitySliderVolume)

        grid.addWidget(self.locationSlider, 0, 1)
        grid.addWidget(self.opacitySlider, 1, 1)
        grid.addWidget(self.detailListGroup(), 0, 0)

        groupBox.setLayout(grid)
        groupBox.setGeometry(0, 0, 32, 128)


        return groupBox
        pass



    def detailListGroup(self):
        # 创建下拉菜单
        groupBox = QGroupBox('控制菜单')
        self.comboBox = QComboBox()
        self.comboBox.move(20, 20)
        self.getAllcontrolPoint(self.comboBox)
        self.comboBox.activated[str].connect(self.itemChoice)

        hBox = QHBoxLayout(self)
        hBox.addWidget(self.comboBox)
        groupBox.setLayout(hBox)
        return groupBox
        pass

    def getAllcontrolPoint(self, comboBox):
        comboBox.clear()
        if self._points != None:
            for i in range(0, len(self._points)):
                comboBox.addItem('控制点_' + str(i + 1), self._points[i][0])


    def rangeSliderEndVolue(self, event):
        self.OperatPlt.plotRight = event
        self.changeControlArea()
        pass

    def rangeSliderStartVolue(self, event):
        self.OperatPlt.plotLeft = event
        self.changeControlArea()
        pass

    def changeControlArea(self):
        self.OperatPlt.ax.set_xlim(self.OperatPlt.plotLeft, self.OperatPlt.plotRight)
        self.OperatPlt.ax2.set_xlim(self.OperatPlt.plotLeft, self.OperatPlt.plotRight)
        self.OperatPlt.fig.canvas.draw()
        # self.OperationPointsingle.emit(self.OperatPlt.points)
        # self.OperationColorsingle.emit(self.OperatPlt.pColor)

    def changeShiftSliderVolue(self, event):
        for i in reversed(range(0, len(self.OperatPlt.points))):
            tmpValue = self.OperatPlt.points[i][0] - self.OperatPlt.points[0][0]
            self.OperatPlt.points[i][0] = tmpValue + event
            self.OperatPlt.pColor[i][0] = tmpValue + event
        self.OperatPlt.isPicked = False
        self.OperatPlt.drawPoints(self.OperatPlt.points, self.OperatPlt.pColor, -1)
        self.OperationPointsingle.emit(self.OperatPlt.points)
        self.OperationColorsingle.emit(self.OperatPlt.pColor)
        pass

    def itemChoice(self, event):
        text, num = event.split('_')
        num = int(num) - 1
        if num >= 0:
            tmpValue = self.OperatPlt.points[num][0]
            self.getPoint = self.OperatPlt.points[num]
            if num > 0 and num < len(self.OperatPlt.points)-1:
                self.locationSlider.setRange(self.OperatPlt.points[num - 1][0], self.OperatPlt.points[num + 1][0])
                self.locationSlider.setValue(tmpValue)
                print(tmpValue)
            elif num == 0:
                self.locationSlider.setRange(0, self.OperatPlt.points[num + 1][0])
                self.locationSlider.setValue(tmpValue)
            elif num == len(self.OperatPlt.points)-1:
                self.locationSlider.setRange(self.OperatPlt.points[num-1][0],self.OperatPlt.points[len(self.OperatPlt.points)-1][0])
                self.locationSlider.setValue(tmpValue)
            else:
                print('No any point has choice')

            tmpOpacity = self.OperatPlt.points[num][1]
            self.opacitySlider.setRange(0, 300)
            self.opacitySlider.setValue(tmpOpacity * 300)

        else:
            self.getPoint = None
        pass

    def locatonSliderVolume(self, event):
        if self.getPoint != None:
            self.changePointlocationState(event, self.getPoint)
            self.OperationPointsingle.emit(self.OperatPlt.points)
            self.OperationColorsingle.emit(self.OperatPlt.pColor)
        pass

    def opacitySliderVolume(self, val):
        value = float(val/300)
        if self.getPoint != None:
            self.changePointOpacityState(value, self.getPoint)
            self.OperationPointsingle.emit(self.OperatPlt.points)
            self.OperationColorsingle.emit(self.OperatPlt.pColor)
        pass

    def changePointOpacityState(self, valume, point):
        tmpValue = point[1]
        if point != None and valume != None:
            point[1] = valume
            self.OperatPlt.drawPoints(self.OperatPlt.points, self.OperatPlt.pColor, -1)
        pass

    def changePointlocationState(self, valume, point):
        tmpValue = point[0]
        if point != None and valume != None:
            point[0] = valume
            self.OperatPlt.drawPoints(self.OperatPlt.points, self.OperatPlt.pColor, -1)
        pass

    def updataItme(self, event):
        if event == True and self.comboBox != None:
            self.getAllcontrolPoint(self.comboBox)
        pass

    def updatePoints(self, event):
        self.OperationPointsingle.emit(event)
        pass

    def updateColors(self, event):
        self.OperationColorsingle.emit(event)
        pass



tmpPoints = [[0, 0], [500, 0.55], [1000, 0.55], [1150, 0.85]]
tmpColor = [[0, 0.0, 0.0, 0.0], [500, 0.6, 0.5, 0.3], [1000, 0.9, 0.9, 0.3], [1150, 1.0, 1.0, 0.9]]
tmpvOpacity = [[0, 0.2], [500, 0.55], [1000, 0.55], [1150, 0.85]]
tmpgOpacity = [[0, 0.0], [90, 0.8], [100, 1.0]]

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = plotWindow(points=tmpPoints, colors=tmpColor, vOpacity=tmpvOpacity, gOpacity=tmpgOpacity)
    sys.exit(app.exec_())