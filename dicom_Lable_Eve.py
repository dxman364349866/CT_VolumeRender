from PyQt5.QtWidgets import QLabel, QGridLayout
from dicom_Lable import dicom_2DLable

class dicom_Lable_Eve(QLabel):
    def __init__(self, **kwargs):
        super(dicom_Lable_Eve, self).__init__()
        self._data = kwargs.get('data',None)
        self._datas = kwargs.get('datas', None)
        self.dcmLable = dicom_2DLable(datas=self._datas, data=self._data)
        self.dcmLable.show()
        print(self.dcmLable)

    def initUI(self):
        self.tmpLayout = QGridLayout()
        self.tmpLayout.addWidget(self.dcmLable)
        self.setLayout(self.tmpLayout)
        pass

