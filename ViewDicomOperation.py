import os
import re
import sys
import numpy as np
import pydicom
from glob import glob
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QPoint, Qt
from Operation.dicom_data import DicomData
from Operation.dicom_widget import DicomWidget

class ShowMyImage(QWidget):
    def __init__(self):
        super(ShowMyImage,self).__init__()
        width = 512
        height = 512
        self.choiceNum = 0
        self.setGeometry(20, 20, 512, 512)
        self.resize(width, height)
        self.layout = QVBoxLayout()
        self.isActiveWindow()


        path = 'D:/Dicomfile/brian_and_vessel/SE3'

        self.datas = []
        self.datas = DicomData.from_files(path)

        self.pix_label = DicomWidget(self, data= self.datas[0])
        self.pix_label.pixmaps = self.datas
        self.pix_label.update_image()
        # self.pix_label.setScaledContents(True)

        # self.pix_labe2 = DicomWidget(self, data= self.datas[0])
        # self.pix_labe2.pixmaps = self.datas
        # self.pix_labe2.update_image()
        # self.pix_labe2.setScaledContents(True)

        self.layout.addWidget(self.pix_label)

        self.initUI()

    # def embedded_numbers(self,s):
    #     pieces = self.re_digits.split(s)
    #     pieces[1::2] = map(int, pieces[1::2])
    #     return pieces
    #
    # def sort_string(self,lst):
    #     return sorted(lst, key=self.embedded_numbers)


    def resizeEvent(self, QResizeEvent):
        self.pix_label.resize(QResizeEvent.size())


    def initUI(self):
        # HBox = QHBoxLayout(self)
        # Splitter1 = QSplitter(Qt.Horizontal)
        # Splitter2 = QSplitter(Qt.Horizontal)
        # Splitter1.addWidget(self.pix_label)
        # Splitter1.addWidget(self.pix_labe2)
        # Splitter2.addWidget(Splitter1)
        # HBox.addWidget(Splitter2)
        # self.setLayout(HBox)
        pass

    def wheelEvent(self, event):
        up_down = QPoint(event.angleDelta())
        if up_down.y() < 0 and self.choiceNum > 0:
            self.choiceNum -= 1
            self.pix_label._data  = self.datas[self.choiceNum]


        elif up_down.y() > 0 and self.choiceNum < len(self.datas)-1:
            self.choiceNum += 1
            self.pix_label._data = self.datas[self.choiceNum]

        self.pix_label.update_image()
        self.pix_label.resize(self.size())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ShowMyImage()
    window.show()
    sys.exit(app.exec_())


