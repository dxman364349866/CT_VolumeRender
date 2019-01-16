import sys
import math
import numpy as np
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from PyQt5.QtWidgets import QWidget, QApplication, QMdiSubWindow
from PyQt5.Qt import QGridLayout, QHBoxLayout, QLayout
from Atomic_Class import Atomic_SlicerBar as As
from Atomic_Class import Atomic_Param as Ap

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

        if self.cutSlider != None:
            self.cutSlider.GetPoint1Coordinate().SetValue(20,  10)
            self.cutSlider.GetPoint2Coordinate().SetValue(200, 10)
        pass

    def initUI(self):
        self.planes = vtk.vtkPlanes()
        self.ren = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.vtkWidget.GetRenderWindow().GetInteractor().SetInteractorStyle(MainInteractorStyle())
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()

        self.drawPoint = [[0, 0, 0], [360, 0, 0]]

        self.loadFile(self._filePath)



        #================Draw CoordLine================
        self.lineSource = vtk.vtkLineSource()
        self.targetPoint = vtk.vtkSphereSource()
        self.incidencePoint = vtk.vtkSphereSource()

        self.drawCoordLine()
        self.drawCoordPoint()
        self.initCutPlane()
        self.initCutSlider()
        self.initText()

        # self.initBoxWidget()
        pass

    def getDistance(self):
        normal = [0, 0, 0]
        normal[0] = self.drawPoint[1][0] - self.drawPoint[0][0]
        normal[1] = self.drawPoint[1][1] - self.drawPoint[0][1]
        normal[2] = self.drawPoint[1][2] - self.drawPoint[0][2]

        distance = math.sqrt(normal[0] ** 2 + normal[1] ** 2 + normal[2] ** 2)
        return distance

    def getDirection(self):
        distance = self.getDistance()
        direction = [0, 0, 0]
        direction[0] = (self.drawPoint[1][0] - self.drawPoint[0][0])/distance
        direction[1] = (self.drawPoint[1][1] - self.drawPoint[0][1])/distance
        direction[2] = (self.drawPoint[1][2] - self.drawPoint[0][2])/distance

        return direction

    def sliceCallback(self, obj, event):
        # disance = self.getDistance()
        tmpVal = [0, 0, 0]
        sdiract = [0, 0, 0]

        fdiract = self.cureenDirector
        sdiract[0] = fdiract[0] * -1
        sdiract[1] = fdiract[1] * -1
        sdiract[2] = fdiract[2] * -1

        val = self.cureenDistance * (1.0 - self.cutSlider.GetValue())
        tmpVal[0] = self.drawPoint[1][0] + sdiract[0] * val
        tmpVal[1] = self.drawPoint[1][1] + sdiract[1] * val
        tmpVal[2] = self.drawPoint[1][2] + sdiract[2] * val


        self.drawPoint[0] = tmpVal

        self.lineSource.SetPoint1(self.drawPoint[0])
        self.lineSource.SetPoint2(self.drawPoint[1])
        # Draw Points
        self.incidencePoint.SetCenter(self.drawPoint[0])
        self.targetPoint.SetCenter(self.drawPoint[1])
        self.controlCutPlane(tmpVal, fdiract)

        # Show Distance
        self.txt.SetInput('Distance:' + str(round(self.getDistance()/10, 2)) + ' cm')
        self.vtkWidget.update()
        pass

    def controlCutPlane(self, cutlocation= [0.0, 0.0, 0,0], cutnormal = [0, 0, 1]):

        location = cutlocation
        normal = cutnormal

        self.planeClip.SetOrigin(location[0], location[1], location[2])
        self.planeClip.SetNormal(normal[0], normal[1], normal[2])

        pass

    def initCutSlider(self):
        yAxis = 10
        self.cutSlider = As.Atomic_Clicer.SliderRepresentation2D(As)
        self.CutSliderWidget = As.Atomic_Clicer.ConfigSlider(As, self.cutSlider, "CutDirection",  yAxis)
        self.CutSliderWidget.SetInteractor(self.iren)
        self.CutSliderWidget.EnabledOn()
        self.cureenDistance = self.getDistance()
        self.cureenDirector = self.getDirection()
        self.CutSliderWidget.AddObserver('InteractionEvent', self.sliceCallback)
        # print(self.CutSliderWidget.GetPoint1Coordinate())

    def initCutPlane(self):
        self.planeClip = vtk.vtkPlane()

        self.volumMapper.AddClippingPlane(self.planeClip)
        self.controlCutPlane(self.drawPoint[0], self.getDirection())
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

    def initText(self):
        self.txt = vtk.vtkTextActor()
        self.txt.SetInput("Distance:")
        self.txtprop = self.txt.GetTextProperty()
        self.txtprop.SetFontFamilyToArial()
        self.txtprop.SetFontSize(15)
        self.txtprop.SetColor(0, 1, 0)
        self.txt.SetDisplayPosition(20, 35)
        self.ren.AddActor(self.txt)
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
        self.colors.SetColor("BackGroundcolors", [255, 255, 255, 255])

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

    def drawCoordLine(self):

        self.lineSource.SetPoint1(self.drawPoint[0])
        self.lineSource.SetPoint2(self.drawPoint[1])


        colors = vtk.vtkNamedColors()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(self.lineSource.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetLineWidth(1)
        actor.GetProperty().SetColor(colors.GetColor3d("Peacock"))
        self.ren.AddActor(actor)

        pass

    def drawCoordPoint(self):
        colors = vtk.vtkNamedColors()

        # Create a TargetPoint
        self.targetPoint.SetCenter(0.0, 0.0, 0.0)
        self.targetPoint.SetRadius(2.0)
        # 设置球面的细分
        self.targetPoint.SetPhiResolution(10)
        self.targetPoint.SetThetaResolution(10)

        # Create a incidencePoint
        self.incidencePoint.SetCenter(0., 0., 0., )
        self.incidencePoint.SetRadius(2.0)
        # 设置球面的细分
        self.incidencePoint.SetPhiResolution(10)
        self.incidencePoint.SetThetaResolution(10)


        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(self.targetPoint.GetOutputPort())

        mapper2 = vtk.vtkPolyDataMapper()
        mapper2.SetInputConnection(self.incidencePoint.GetOutputPort())

        actor = vtk.vtkActor()
        actor2 = vtk.vtkActor()

        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(colors.GetColor3d("Red"))

        actor2.SetMapper(mapper2)
        actor2.GetProperty().SetColor(colors.GetColor3d("Blue"))

        self.ren.AddActor(actor)
        self.ren.AddActor(actor2)
        pass


    def drawFunction(self):
        # get CurentDistance and Director
        self.cureenDistance = self.getDistance()
        self.cureenDirector = self.getDirection()
        # Draw Line
        self.lineSource.SetPoint1(self.drawPoint[0])
        self.lineSource.SetPoint2(self.drawPoint[1])
        # Draw Points
        self.incidencePoint.SetCenter(self.drawPoint[0])
        self.targetPoint.SetCenter(self.drawPoint[1])
        # ControlCutPlane
        self.controlCutPlane(self.drawPoint[0],  self.cureenDirector)
        self.vtkWidget.update()
        pass



# filePath = 'D:/Dicomfile/MT_07/'
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     win = volumeWindow(dirPath=filePath)
#     win.show()
#     sys.exit(app.exec_())
