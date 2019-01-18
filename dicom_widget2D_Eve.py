import sys
import SimpleITK
from PyQt5.QtWidgets import  QWidget, QApplication, QGridLayout, QMdiSubWindow, QHBoxLayout, QVBoxLayout,QSplitter
from dicom_WidgetAndArea import dicomImage2DdisplayWidget

class dicom_widgetEve(QWidget):
    def __init__(self, **kwargs):
        super(dicom_widgetEve,self).__init__()
        self.setGeometry(50, 50, 512, 512)
        self.setWindowTitle('Dicom2DEve')
        self.initUI()

    def initUI(self):
        #==============================TmpTestsParameter==================================
        pathDicom = "D:/Dicomfile/MT_07/"
        idxSlice = 50
        reader = SimpleITK.ImageSeriesReader()
        filenamesDICOM = reader.GetGDCMSeriesFileNames(pathDicom)

        reader.SetFileNames(filenamesDICOM)
        imgOriginals = reader.Execute()
        datas = SimpleITK.GetArrayFromImage(imgOriginals)
        Spacing = imgOriginals.GetSpacing()
        #=================================================================================



        self.GLayout = QGridLayout(self)
        self.dicom2D = dicomImage2DdisplayWidget(face=0, datas=datas, spacing=Spacing)
        print(self.dicom2D)
        self.GLayout.addWidget(self.dicom2D)
        self.setLayout(self.GLayout)
        pass





if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = dicom_widgetEve()
    win.show()
    sys.exit(app.exec_())