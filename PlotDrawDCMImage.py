import os
import sys
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pydicom
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QIcon

from glob import glob
import math
import pydicom
from pydicom.data import get_testdata_files



class ShowDicom(QWidget):
    def __init__(self):
        super(ShowDicom, self).__init__()
        self.setWindowTitle('密度控制')
        self.setWindowIcon(QIcon('../Atomic_Icon/area.ico'))
        self.setGeometry(10, 30, 600, 600)
        self.initUI()
    def initUI(self):
        # 设置布局方式，要有布局才能添加东西进去
        self.vbl = QVBoxLayout()
        self.initPlot()

    def initPlot(self):
        #清屏
        plt.cla()

        self.fig = plt.figure()
        # matplotlib占据画面中的位置及比例
        self.ax = self.fig.add_axes([0.1, 0.1, 0.8, 0.8])
        # 绘制网格
        self.ax.grid(True)
        # 设置x，y轴的数值区间
        self.ax.set_xlim(0, 512)
        self.ax.set_ylim(0, 512)
        self.scrollnum = 0;
        # FigureCanvas 是一个PyQt5 的QWidget类，又是一个matplotlib的FigureCanvas，
        # 这是链接pyqt5和 matplotlib的关键
        self.canvas = FigureCanvas(self.fig)
        # 将canvas加入布局中
        self.vbl.addWidget(self.canvas)
        # 最后设置布局就可以显示出来了
        self.fig.canvas.mpl_connect('scroll_event', self.scrollimage)
        self.setLayout(self.vbl)
        self.inputDicom()

    def scrollimage(self,event):

        if(event.button == 'down') and self.scrollnum >0:
            self.scrollnum = self.scrollnum - 1
            self.ax.imshow(self.newData[self.scrollnum], cmap=plt.cm.bone)
        elif(event.button == 'up') and self.scrollnum < 96:
            self.scrollnum = self.scrollnum + 1
            self.ax.imshow(self.newData[self.scrollnum], cmap=plt.cm.bone)

        self.fig.canvas.draw()

    def inputDicom(self):
        data_path = 'D:/Dicomfile/brian_and_vessel/SE3/'
        listDicomName = glob(data_path + '/*.dcm')

        # for each in listDicomName:
            # dcm = pydicom.read_file(each)
            # print(dcm.PatientID)
            # print(dcm.PatientName)
            # print(dcm.PatientBirthDate)
            # print(dcm.PatientSex)
            # print(dcm.StudyID)
            # print(dcm.StudyDate)
            # print(dcm.InstitutionName)
            # print(dcm.Manufacturer)
            # print('========================')

            # listDicomFile.append(dcm)
        # dir 方法可以看见字典中的具体信息
        # print('\n'.join(dir(listDicomFile[0])))
        # print(listDicomFile[0].pixel_array[0])
        # image = np.stack([s for s in listDicomFile[0].pixel_array], 0)
        # image = image.astype(np.int16)
        # image[image == -2000] = 0

        patient = self.load_scan(data_path)
        imgs = self.get_pixels_hu(patient)
        # width, height = imgs.size
        self.newData = np.squeeze(imgs)

        # self.ax.set_xlim(0,width)
        # self.ax.set_ylim(0,height)
        self.ax.imshow(self.newData[0], cmap= plt.cm.bone)
        # plt.show()
        # print(dir(patient ))
        # print(self.newData[0])

    def load_scan(self, path):
        slices = [pydicom.read_file(path + '/' + s) for s in os.listdir(path)]
        slices.sort(key=lambda x: int(x.InstanceNumber))
        try:
            slice_thickness = np.abs(slices[0].ImagePositionPatient[2] - slices[1].ImagePositionPatient[2])
        except:
            slice_thickness = np.abs(slices[0].SliceLocation - slices[1].SliceLocation)

        for s in slices:
            s.SliceThickness = slice_thickness
        return slices

    def get_pixels_hu(self, scans):
        image = np.stack([s.pixel_array for s in scans])
        image = image.astype(np.int16)
        image[image == -2000] = 0
        intercept = scans[0].RescaleIntercept
        slope = scans[0].RescaleSlope

        if slope != 1:
            image = slope * image.astype(np.int16)
            image = image.astype(np.int16)

        image += np.int16(intercept)
        return np.array(image, dtype = np.int16)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dicomWindow = ShowDicom()
    dicomWindow.show()
    app.exec_()
