import sys
import math
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QSplitter, QLabel
from PyQt5.QtCore import Qt
from Operation.dicom_data import DicomData
from Operation.dicom_widget import DicomWidget

class MultDicomViwer(QWidget):

    def __init__(self, Dirpath, **kwargs ):
        super(MultDicomViwer, self).__init__()
        self._path = Dirpath

        self.initUI()

    def initUI(self):

        # path = 'D:/Dicomfile/brian_and_vessel/SE3'

        self.datas = []
        self.datas = DicomData.from_files(self._path)
        self.datas2 = self.datas

        self.datas = np.stack(self.datas, 2)

        value = self.datas.shape[0] // self.datas2.shape[0]
        value = math.ceil(value / 2)
        las = self.datas.shape[0] % self.datas2.shape[0]
        up = self.datas2.shape[0] * value + las
        down = up // value

        print(up)
        print(down)

        AppendA = np.full((512, 512, 112), -2000)
        AppendB = np.full((512, 512, 112), -2000)

        self.datas = np.repeat(self.datas, value, axis=2)
        self.datas = np.concatenate((self.datas, AppendA), axis=2)
        self.datas = np.concatenate((AppendB, self.datas), axis=2)

        self.datas3 = np.stack(self.datas, 1)

        for i in range(0, self.datas3.shape[0] - 1):
            self.datas3[i] = np.fliplr(self.datas3[i])

        for i in range(0, self.datas2.shape[0] - 1):
            self.datas2[i] = np.flipud(self.datas2[i])

        for i in range(0, self.datas.shape[0] - 1):
            self.datas[i] = np.fliplr(self.datas[i])

        self.pix_label1 = DicomWidget(self, data=np.stack(self.datas[0], axis=1))
        self.pix_label1.pixmaps = self.datas
        self.pix_label1.paxis = 1
        self.pix_label1.update_image()
        self.pix_label1.pen1.setColor(Qt.yellow)
        self.pix_label1.pen2.setColor(Qt.green)
        self.pix_label1.setScaledContents(True)

        self.pix_label2 = DicomWidget(self, data=self.datas2[0])
        self.pix_label2.paxis = 0
        self.pix_label2.pixmaps = self.datas2
        self.pix_label2.update_image()
        self.pix_label2.pen1.setColor(Qt.yellow)
        self.pix_label2.pen2.setColor(Qt.blue)
        self.pix_label2.setScaledContents(True)

        self.pix_label3 = DicomWidget(self, data=np.stack(self.datas3[0], axis=1))
        self.pix_label3.paxis = 1
        self.pix_label3.pixmaps = self.datas3
        self.pix_label3.update_image()
        self.pix_label3.pen1.setColor(Qt.blue)
        self.pix_label3.pen2.setColor(Qt.green)
        self.pix_label3.setScaledContents(True)

        self.pix_label1.Drawsignle.connect(self.OperationImage1)
        self.pix_label2.Drawsignle.connect(self.OperationImage2)
        self.pix_label3.Drawsignle.connect(self.OperationImage3)


        hbox = QHBoxLayout(self)


        splitter1 = QSplitter(Qt.Horizontal)
        splitter1.addWidget(self.pix_label3)
        splitter1.addWidget(self.pix_label2)
        # splitter1.setSizes([256, 256])

        tmpLay = QLabel(self)
        tmpLay.setGeometry(0, 0, 512, 512)
        splitter2 = QSplitter(Qt.Horizontal)
        splitter2.addWidget(self.pix_label1)
        splitter2.addWidget(tmpLay)

        splitter3 = QSplitter(Qt.Vertical)
        splitter3.addWidget(splitter2)
        splitter3.addWidget(splitter1)


        hbox.addWidget(splitter3)

        self.setLayout(hbox)

        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('QSplitter demo')
        self.show()

    def resizeEvent(self, QResizeEvent):
        tmp = QResizeEvent.size()
        # print(tmp.width(), tmp.height())

    def OperationImage1(self, event1):
        if self.pix_label3 != None:
            self.pix_label3.choiceNumber(event1[0])
            self.pix_label3.redrawLine(1, [0, event1[1]])

        if self.pix_label2 != None:
            tmp = self.datas2.shape[0] - int(((event1[1]) - 112) / 3)
            self.pix_label2.choiceNumber(tmp)
            self.pix_label2.redrawLine(0, [event1[0], 0])
        pass
    def OperationImage2(self, event2):
        if self.pix_label1 != None:
            self.pix_label1.choiceNumber(self.datas.shape[0] - event2[1])
            self.pix_label1.redrawLine(0, [event2[0], 0])
        if self.pix_label3 != None:
            self.pix_label3.choiceNumber(event2[0])
            self.pix_label3.redrawLine(0, [self.datas.shape[2] - event2[1], 0])
        pass
    def OperationImage3(self, event3):
        if self.pix_label1 != None:
            self.pix_label1.choiceNumber(event3[0])
            self.pix_label1.redrawLine(1, [0, event3[1]])
        if self.pix_label2 != None:
            tmp = self.datas2.shape[0] - int(((event3[1]) - 112) / 3)
            self.pix_label2.choiceNumber(tmp)
            self.pix_label2.redrawLine(1, [0, self.datas2.shape[2] - event3[0]])
        pass
# def main():
#     app = QApplication(sys.argv)
#     ex = MultDicomViwer()
#     sys.exit(app.exec_())
#
#
# if __name__ == '__main__':
#     main()