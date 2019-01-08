import sys
import math
import numpy as np
import vtk
from PyQt5.QtWidgets import QWidget, QApplication, QLabel
from PyQt5.QtCore import Qt, pyqtSignal
from dicom_widget import DicomWidget
from dicom_data import DicomData


class Dicom2Dwindow(QWidget):
    # drawSignle = pyqtSignal(list)
    def __init__(self, **kwargs):
        super(Dicom2Dwindow, self).__init__()
        self._axis = 0
        self._path = kwargs.get('dirPath',None)
        self._cutfac = kwargs.get('cutface', 0)

        self.neighbor = [None, None]

        self.initUI2()
        self.initUI()
        self.show()

    def initUI2(self):
        self.reader = vtk.vtkDICOMImageReader()
        self.reader.SetDirectoryName(self._path)
        self.reader.Update()

        xMin, xMax, yMin, yMax, zMin, zMax = self.reader.GetDataExtent()
        xSpacing, ySpacing, zSpacing = self.reader.GetOutput().GetSpacing()
        x0, y0, z0 = self.reader.GetOutput().GetOrigin()


        center = [x0 + xSpacing * 0.5 * (xMin + xMax),
                  y0 + ySpacing * 0.5 * (yMin + yMax),
                  z0 + zSpacing * 0.5 * (zMin + zMax)]

        print(xSpacing, ySpacing, zSpacing)
        print(x0, y0, z0)
        print((xMin + xMax),(yMin + yMax),(zMin + zMax))
        print(center)

        self.axial = vtk.vtkMatrix4x4()
        self.axial.DeepCopy((1, 0, 0, center[0],
                        0, 1, 0, center[1],
                        0, 0, 1, center[2],
                        0, 0, 0, 1))
        self.coronal = vtk.vtkMatrix4x4()
        self.coronal.DeepCopy((1, 0, 0, center[0],
                          0, 0, 1, center[1],
                          0, -1, 0, center[2],
                          0, 0, 0, 1))

        self.sagittal = vtk.vtkMatrix4x4()
        self.sagittal.DeepCopy((0, 0, -1, center[0],
                           1, 0, 0, center[1],
                           0, -1, 0, center[2],
                           0, 0, 0, 1))



    def initUI(self):
        self.setGeometry(0, 0, 512, 512)
        self.setWindowTitle('Loading...')

        self.label = QWidget(self)
        self.datas = []
        self.datas = DicomData.from_files(self._path)




        self.maxlevel = max(self.datas.shape)
        self.minlevel = min(self.datas.shape)

        self.xAxis, self.yAxis, self.zAxis = self.datas.shape

        self.pixScaleSize = 1

        # self.pixAppendup = 0
        # self.pixAppenddown = 0
        # if self.pixScaleSize <= 1:
        #     self.pixAppendup = math.floor((self.maxlevel - self.minlevel)/2)
        #     self.pixAppenddown = math.floor((self.maxlevel - self.minlevel) - self.pixAppendup)
        #     # self.pixScaleSize = 3
        #     print('Jump')
        # else:
        #     self.pixAppendup = math.floor((self.maxlevel - int(self.minlevel * self.pixScaleSize)) / 2)
        #     self.pixAppenddown = math.floor((self.maxlevel - int(self.minlevel * self.pixScaleSize))) - self.pixAppendup
        #     # self.pixScaleSize = 1
        #     print('not jump')

        self.pixAppendup = math.floor((self.maxlevel - int(self.minlevel * self.pixScaleSize)) / 2)
        self.pixAppenddown = math.floor((self.maxlevel - int(self.minlevel * self.pixScaleSize))) - self.pixAppendup

        # cunt append horizantol and vertical
        self.AppendA = np.full((512, 512, self.pixAppendup), -2000)
        self.AppendB = np.full((512, 512, self.pixAppenddown), -2000)

        vlineColor = Qt.blue
        hlineColor = Qt.green

        self.datas[self.datas == 741] = -1164
        self.datas[self.datas == -6534] = 3607

        if self._cutfac == 1:
            self.datas = np.stack(self.datas, 2)
            self.datas = np.repeat(self.datas, self.pixScaleSize, axis=2)
            self.appendPix()
            for i in range(0, self.datas.shape[0] - 1):
                self.datas[i] = np.fliplr(self.datas[i])

            vlineColor = Qt.blue
            hlineColor = Qt.green


            self._axis = 1

        elif self._cutfac == 2:
            print(self.xAxis, self.yAxis, self.zAxis)
            self.datas = np.stack(self.datas, 2)
            self.datas = np.stack(self.datas, 1)
            self.datas = np.repeat(self.datas, self.pixScaleSize, axis=2)
            self.appendPix()

            for i in range(0, self.datas.shape[0] - 1):
                self.datas[i] = np.fliplr(self.datas[i])

            vlineColor = Qt.yellow
            hlineColor = Qt.green

            self._axis = 1

        else:
            self.scaleSizeY = self.maxlevel
            self.scaleSizeY = self.maxlevel
            vlineColor = Qt.blue
            hlineColor = Qt.yellow
            self._axis = 0
            pass

    #=====================================Get DicomWidget =================================================
        self.pix_label = DicomWidget(self, data=np.stack(self.datas[0], axis=self._axis), axis=self._axis)
        self.pix_label.pixmaps = self.datas
        self.pix_label.winSize[0] = self.minlevel
        self.pix_label.winSize[1] = self.maxlevel
        self.pix_label.update_image()
        self.pix_label.pen1.setColor(vlineColor)
        self.pix_label.pen2.setColor(hlineColor)
        self.pix_label.setScaledContents(True)
#=====================================Draw position Text =============================================
        self.texPositionLabel = QLabel(self)
        self.showPosition('helloCT')
        self.show()
    def appendPix(self):
        if self.pixScaleSize >= 1:
            self.datas = np.concatenate((self.datas, self.AppendA), axis=2)
            self.datas = np.concatenate((self.AppendB, self.datas), axis=2)
        else:
            print('Dont need pixScaleSize')
        pass

    def showPosition(self, Text = 'hello'):
        self.texPositionLabel.setText(Text)
        self.texPositionLabel.setGeometry(10, 0, 500, 20)
        self.texPositionLabel.setStyleSheet('color:red')
        pass
    def resizeEvent(self, QResizeEvent):

        if self.width() < self.height():
            self.pix_label.winSize[0] = self.width()
            self.pix_label.winSize[1] = self.width()
            self.pix_label.getResizeEvent(self.width(), self.width())
        else:
            self.pix_label.winSize[0] = self.height()
            self.pix_label.winSize[1] = self.height()
            self.pix_label.getResizeEvent(self.height(), self.height())

        pass




if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Dicom2Dwindow(dirPath='D:/Dicomfile/MT_07/', cutface=0)
    sys.exit(app.exec_())
