import sys
from PyQt5.QtWidgets import QWidget, QApplication

class dicomImage3DdisplayWidget(QWidget):
    def __init__(self):
        super(dicomImage3DdisplayWidget,self).__init__()
        self.setWindowTitle('Dicom3DWidget')
        self.setGeometry(0, 0, 512, 512)
        self.initUI()
    def initUI(self):
        pass



if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = dicomImage3DdisplayWidget()
    win.show()
    sys.exit(app.exec_())
