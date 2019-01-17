from PyQt5.QtWidgets import QLabel, QApplication, QPushButton

class dicom_2DLableOperation(QLabel):
    def __init__(self):
        super(dicom_2DLableOperation, self).__init__()
        self.setGeometry(0, 0, 512, 256)
        self.initUI()

    def initUI(self):
        self.button = QPushButton('Choice',self)
        self.button.setGeometry(0, 0, 256, 256)
        pass


