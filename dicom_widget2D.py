import sys
import SimpleITK
import numpy as np
from dicom_Lable import dicom_2DLable
from dicom_Lable_Eve import dicom_Lable_Eve
from dicom_LableOperation import dicom_2DLableOperation

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout,QSplitter, QPushButton, QComboBox
from PyQt5.QtGui import QIcon, QImage
from PyQt5.QtCore import Qt, QTimer

class dicom_widget(QWidget):
    def __init__(self, **kwargs):
        super(dicom_widget,self).__init__()
        self._datas = kwargs.get('datas', None)
        self._viewPlane = kwargs.get('viewPlane', 0)

        self.initParameter()
        self.initUI()

    def initParameter(self):


        # pushbutton = QPushButton('hello',self)
        # pushbutton.setAttribute(Qt.WA_TranslucentBackground)

        self.imLable = dicom_2DLable(data=self._datas[50], datas=self._datas)
        self.comBox = QComboBox()
        self.comBox.addItem('mainface')
        self.comBox.addItem('topface')
        self.comBox.addItem('sideface')
        self.comBox.activated[str].connect(self.item_Choice)
        self.comBox.move(300, 30)

        # self.timer = QTimer(self)
        # self.timer.timeout.connect(self.createcomBox)
        # self.timer.start(3)

        pass

    def item_Choice(self,event):
        if event == 'mainface':
            self.imLable.viewPlane = 0
            print('mymainface')
        elif event == 'topface':
            self.imLable.viewPlane = 1
            print('mytopface')
        elif event == 'sideface':
            self.imLable.viewPlane = 2
            print('myside face')

        self.imLable.displayfacePlane()

    def initUI(self):


        self.setWindowTitle('DicomWidget')
        self.setWindowIcon(QIcon('../Atomic_Icon/area.ico'))
        self.dicomLayout = QGridLayout()

        self.setGeometry(0, 0, 512, 512)

        self.dicomLayout.addWidget(self.comBox)
        self.dicomLayout.addWidget(self.imLable)
        self.setLayout(self.dicomLayout)

        self.initViewPlane()

        pass

    def initViewPlane(self):
        pass



pathDicom = "D:/Dicomfile/MT_07/"
reader = SimpleITK.ImageSeriesReader()
filenamesDICOM = reader.GetGDCMSeriesFileNames(pathDicom)
reader.SetFileNames(filenamesDICOM)
imgOriginals = reader.Execute()
datas = np.array(SimpleITK.GetArrayFromImage(imgOriginals))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = dicom_widget(datas=datas)
    win.show()
    sys.exit(app.exec_())