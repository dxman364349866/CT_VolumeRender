import sys
import numpy as np
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from PyQt5.QtWidgets import QWidget, QApplication, QMdiSubWindow
from PyQt5.Qt import QGridLayout, QHBoxLayout, QLayout

class MainInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):

    def __init__(self,parent=None):
        self.AddObserver("MiddleButtonPressEvent",self.middleButtonPressEvent)
        self.AddObserver("MiddleButtonReleaseEvent",self.middleButtonReleaseEvent)

    def middleButtonPressEvent(self,obj,event):
        self.OnMiddleButtonDown()
        return

    def middleButtonReleaseEvent(self,obj,event):
        self.OnMiddleButtonUp()
        return

class volumeWindow(QWidget):
    def __init__(self, **kwargs):
        super(volumeWindow, self).__init__()
        self._filePath = kwargs.get('dirPath', None)
        initWidth = 300
        initHeight = 300
        self.setWindowTitle('AtomicMedical')
        self.gridLayout = QGridLayout()
        self.setGeometry(0, 0, initWidth, initHeight)

        self.vtkWidget = QVTKRenderWindowInteractor(self)
        self.vtkWidget.resize(initWidth, initHeight)

        self.gridLayout.addWidget(self.vtkWidget)
        self.initUI()

    def sliceCubevolum(self, object, event):
        object.GetPlanes(self.planes)
        object.GetSelectedHandleProperty().SetColor(0, 1, 0)
        self.volumMapper.SetCroppingRegionPlanes(self.planes.GetPoints().GetBounds())
        pass

    def resizeEvent(self, QResizeEvent):
        if self.width() < self.height():
            self.vtkWidget.resize(self.width(), self.width())
        elif self.width() > self.height():
            self.vtkWidget.resize(self.height(), self.height())
        else:
            self.vtkWidget.resize(self.width(), self.height())
        pass

    def initUI(self):
        self.planes = vtk.vtkPlanes()
        self.ren = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.vtkWidget.GetRenderWindow().GetInteractor().SetInteractorStyle(MainInteractorStyle())
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
        # self.iren = self.vtkWidget.GetRenderWindow().SetInteractor(vtk.vtkRenderWindowInteractor().SetInteractorStyle(MainInteractorStyle()))

        # self.iren.SetInteractor(MainInteractorStyle())


        self.loadFile(self._filePath)
        self.initBoxWidget()
        pass

    def initBoxWidget(self):
        self.boxWidget = vtk.vtkBoxWidget()
        self.boxWidget.SetInteractor(self.iren)
        self.boxWidget.SetProp3D(self.volume)
        self.boxWidget.SetPlaceFactor(1.25)
        self.boxWidget.PlaceWidget(self.boxWidget.GetProp3D().GetBounds())
        self.boxWidget.SetRotationEnabled(0)
        self.boxWidget.AddObserver("InteractionEvent", self.sliceCubevolum)
        self.boxWidget.GetOutlineProperty().SetOpacity(0.1)
        self.boxWidget.GetOutlineProperty().SetColor(0, 0, 0.3)
        self.boxWidget.On()
        self.volumMapper.SetCropping(1)  # 开启3D剪切模式
        self.volumMapper.SetCroppingRegionPlanes(self.boxWidget.GetProp3D().GetBounds())

        pass

    def loadFile(self, path):
        if path != '':
            self.initWindow(path)

    def initWindow(self, path):
        self.vcolor = [[0, 0.0, 0.0, 0.0],
                       [500, 0.6, 0.5, 0.3],
                       [1000, 0.9, 0.9, 0.3],
                       [1150, 1.0, 1.0, 0.9]]
        self.vOpacity = [[0, 0], [500, 0.55],
                         [1000, 0.55], [1150, 0.85]]
        self.gOpacity = [[0, 0.0], [90, 0.8], [100, 1.0]]

        self.source = vtk.vtkDICOMImageReader()
        self.source.SetDirectoryName(path)
        self.source.Update()

        self.volumcolors = vtk.vtkColorTransferFunction()
        self.setOpacityColor(self.vcolor)
        self.volumScalarOpacity = vtk.vtkPiecewiseFunction()
        self.setOpacityValue(self.vOpacity)
        self.volumGradientOpacity = vtk.vtkPiecewiseFunction()
        self.setGradientOpacity(self.gOpacity)

        self.volumMapper = vtk.vtkGPUVolumeRayCastMapper()
        self.volumMapper.SetInputConnection(self.source.GetOutputPort())

        self.volumeProperty = vtk.vtkVolumeProperty()
        self.volumeProperty.SetColor(self.volumcolors)
        self.volumeProperty.SetScalarOpacity(self.volumScalarOpacity)
        self.volumeProperty.SetGradientOpacity(self.volumGradientOpacity)
        self.volumeProperty.SetInterpolationTypeToLinear()
        self.volumeProperty.ShadeOn()
        self.volumeProperty.SetAmbient(0.4)
        self.volumeProperty.SetDiffuse(0.6)
        self.volumeProperty.SetSpecular(0.2)

        self.volume = vtk.vtkVolume()
        self.volume.SetMapper(self.volumMapper)
        self.volume.SetProperty(self.volumeProperty)

        self.colors = vtk.vtkNamedColors()
        self.colors.SetColor("BackGroundcolors", [44, 77, 89, 255])


        self.ren.SetBackground(self.colors.GetColor3d("BackGroundcolors"))
        self.ren.AddVolume(self.volume)


        self.iren.Initialize()

        pass

    def setOpacityColor(self, valume):
        self.volumcolors.RemoveAllPoints()
        for each in valume:
            self.volumcolors.AddRGBPoint(each[0], each[1], each[2], each[3])

    def setGradientOpacity(self, valume):
        self.volumGradientOpacity.RemoveAllPoints()
        for each in valume:
            self.volumGradientOpacity.AddPoint(each[0],each[1])

    def setOpacityValue(self, valume):
        self.volumScalarOpacity.RemoveAllPoints()
        for each in valume:
            self.volumScalarOpacity.AddPoint(each[0], each[1])
        self.vtkWidget.update()



# filePath = 'D:/Dicomfile/brian_and_vessel/SE3/'
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     win = volumeWindow(dirPath=filePath)
#     win.show()
#     sys.exit(app.exec_())
