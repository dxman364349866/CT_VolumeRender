import sys
import vtk
import SimpleITK
import numpy as np
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout

class MainInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):

    def __init__(self,parent=None):
        self.AddObserver("MiddleButtonPressEvent", self.middleButtonPressEvent)
        self.AddObserver("MiddleButtonReleaseEvent", self.middleButtonReleaseEvent)

    def middleButtonPressEvent(self,obj,event):
        self.OnMiddleButtonDown()
        return

    def middleButtonReleaseEvent(self,obj,event):
        self.OnMiddleButtonUp()
        return

class dicomImage3DdisplayWidget(QWidget):
    def __init__(self, **kwargs):
        super(dicomImage3DdisplayWidget, self).__init__()
        self.initWidth = 512
        self.initHeight = 512
        self.setWindowTitle('Dicom3DWidget')
        self.setGeometry(0, 0, self.initWidth, self.initHeight)

        self._polyData = kwargs.get('polyData', None)
        self._colorFunc = kwargs.get('colorFunc', None)
        self._alphaChannelFunc = kwargs.get('alphaChannelFunc', None)
        self._volumGradientOpacity = kwargs.get('volumGradientOpacity', None)
        self._spacings = kwargs.get('spacings', None)
        self._position = kwargs.get('position', None)

        self.initUI()
    def initUI(self):
        #=================SetVtkWindow=======================
        self.winlayout = QGridLayout()
        self.vtkWidget = QVTKRenderWindowInteractor(self)
        self.vtkWidget.resize(self.initWidth, self.initHeight)
        self.winlayout.addWidget(self.vtkWidget)
        self.initRenderWindow()
        pass

    def initRenderWindow(self):
        self.renderer = vtk.vtkRenderer()

        self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)
        self.vtkWidget.GetRenderWindow().GetInteractor().SetInteractorStyle(MainInteractorStyle())
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()

        #=================SetWindowBackgroundColor=============================
        self.colors = vtk.vtkNamedColors()
        self.colors.SetColor("BackGroundcolors", [0, 255, 0, 255])
        self.renderer.SetBackground(self.colors.GetColor3d("BackGroundcolors"))

        volume = self.createVolume(self._polyData, self._colorFunc, self._alphaChannelFunc, self._volumGradientOpacity, self._spacings, self._position)
        brainMesh = self.createMesh(self._polyData, self._spacings)

        # self.renderer.AddVolume(volume)
        self.renderer.AddActor(brainMesh)
        self.iren.Initialize()
        pass

    def createMesh(self, polyData, spacing):
        dv = 1.75
        rf = 1
        data_matrix = polyData
        data_matrix = np.rot90(data_matrix, 1)
        data_matrix = data_matrix.astype(np.uint8)
        xSize, ySize, zSize = data_matrix.shape

        #================================BoneExtrctor==================================
        dataImporter = vtk.vtkImageImport()
        data_string = data_matrix.tostring()
        dataImporter.CopyImportVoidPointer(data_string, len(data_string))
        dataImporter.SetDataScalarTypeToUnsignedChar()
        dataImporter.SetNumberOfScalarComponents(1)

        dataImporter.SetDataExtent(0, xSize - 1, 0, ySize - 1, 0, zSize - 1)
        dataImporter.SetWholeExtent(0, xSize - 1, 0, ySize - 1, 0, zSize - 1)
        dataImporter.SetDataExtentToWholeExtent()

        #============================= Smoothed pipeline ==============================
        smooth = vtk.vtkImageGaussianSmooth()
        smooth.SetDimensionality(3)
        smooth.SetInputConnection(dataImporter.GetOutputPort())
        smooth.SetStandardDeviations(dv, dv, dv)
        smooth.SetRadiusFactor(rf)

        subsampleSmoothed = vtk.vtkImageShrink3D()
        subsampleSmoothed.SetInputConnection(smooth.GetOutputPort())
        subsampleSmoothed.SetShrinkFactors(4, 4, 1)

        isoSmoothed = vtk.vtkImageMarchingCubes()
        isoSmoothed.SetInputConnection(smooth.GetOutputPort())
        isoSmoothed.SetValue(0, 10)

        isoSmoothedMapper = vtk.vtkPolyDataMapper()
        isoSmoothedMapper.SetInputConnection(isoSmoothed.GetOutputPort())
        isoSmoothedMapper.ScalarVisibilityOff()

        tmpTransfor = vtk.vtkTransform()
        tmpTransfor.Scale(spacing)

        meshActor = vtk.vtkActor()
        meshActor.SetMapper(isoSmoothedMapper)
        meshActor.SetUserTransform(tmpTransfor)

        return meshActor


    def createVolume(self, polyData, colorFunc, alphaChannelFunc, volumGradientOpacity ,spacings, position ):
        data_matrix = polyData
        data_matrix = np.rot90(data_matrix, 1)
        data_matrix = data_matrix.astype(np.uint8)
        xSize, ySize, zSize = data_matrix.shape

        dataImporter = vtk.vtkImageImport()
        data_string = data_matrix.tostring()
        dataImporter.CopyImportVoidPointer(data_string, len(data_string))
        dataImporter.SetDataScalarTypeToUnsignedChar()
        dataImporter.SetNumberOfScalarComponents(1)

        dataImporter.SetDataExtent(0, xSize - 1, 0, ySize - 1, 0, zSize - 1)
        dataImporter.SetWholeExtent(0, xSize - 1, 0, ySize - 1, 0, zSize - 1)
        dataImporter.SetDataExtentToWholeExtent()

        volumeProperty = vtk.vtkVolumeProperty()
        volumeProperty.SetColor(colorFunc)
        volumeProperty.SetScalarOpacity(alphaChannelFunc)
        volumeProperty.SetGradientOpacity(volumGradientOpacity)
        volumeProperty.ShadeOn()
        volumeProperty.SetAmbient(0.4)
        volumeProperty.SetDiffuse(0.6)
        volumeProperty.SetSpecular(0.2)

        volumeMapper = vtk.vtkGPUVolumeRayCastMapper()
        volumeMapper.SetInputConnection(dataImporter.GetOutputPort())

        volume = vtk.vtkVolume()
        volume.SetMapper(volumeMapper)
        volume.SetProperty(volumeProperty)
        transform = vtk.vtkTransform()
        transform.Scale(spacings)
        transform.Translate(position)
        volume.SetUserTransform(transform)
        return volume



    def resizeEvent(self, QResizeEvent):
        if self.width() < self.height():
            self.vtkWidget.resize(self.width(), self.width())
        elif self.width() > self.height():
            self.vtkWidget.resize(self.height(), self.height())
        else:
            self.vtkWidget.resize(self.width(), self.height())
        self.vtkWidget.update()
        print('resize event')
        pass


#=================================All of this just use for test==============================
pathDicom = "D:/Dicomfile/MT_07/"
idxSlice = 50
reader = SimpleITK.ImageSeriesReader()
filenamesDICOM = reader.GetGDCMSeriesFileNames(pathDicom)

reader.SetFileNames(filenamesDICOM)
imgOriginals = reader.Execute()
datas = SimpleITK.GetArrayFromImage(imgOriginals)
datas = datas.astype(np.int8)

DxSize, DySize, DzSize = datas.shape
Spacings = np.array(imgOriginals.GetSpacing())

PosXY = [279, 265]
lstSeeds = [(PosXY[0], PosXY[1])]
LowAndUpper = [100, 300]
rangeSize = min(DxSize, DySize, DzSize)

#================================Extractor ChoiceArea to 3D Data================================
AreaArray = []
for i in range(0, rangeSize):
    imgOriginal = imgOriginals[:, :, i]
    imgWhiteMatter = SimpleITK.ConnectedThreshold(image1=imgOriginal,
                                                  seedList=lstSeeds,
                                                  lower=LowAndUpper[0],
                                                  upper=LowAndUpper[1],
                                                  replaceValue=1,
                                                  )

    imgWhiteMatterNoHoles = SimpleITK.VotingBinaryHoleFilling(image1=imgWhiteMatter,
                                                              radius=[2] * 3,
                                                              majorityThreshold=50,
                                                              backgroundValue=0,
                                                              foregroundValue=1)
    tmpAdd = np.full((512, 512), 0)
    # GotAdd = SimpleITK.GetImageFromArray(tmpAdd)
    # tmpImage = SimpleITK.LabelOverlay(imgOriginal, imgWhiteMatterNoHoles)
    # tmpData = np.array(SimpleITK.GetArrayFromImage(tmpImage))
    tmpData = np.array(SimpleITK.GetArrayFromImage(imgWhiteMatterNoHoles))
    AreaArray.append(tmpData)

AreaArray = np.array(AreaArray)
resualtArray = datas * AreaArray

Spacings[1] = Spacings[2]
Spacings[2] = Spacings[0]

vcolor = [[0, 0.0, 0.0, 0.0],
          [500, 0.6, 0.5, 0.3],
          [1000, 0.9, 0.9, 0.3],
          [1150, 1.0, 1.0, 0.9]]

vOpacity = [[0, 0], [500, 0.75], [1000, 0.85], [1150, 1]]
gOpacity = [[0, 0.0], [90, 0.8], [100, 1.0]]

alphaChannelFunc = vtk.vtkPiecewiseFunction()
for each in vOpacity:
    alphaChannelFunc.AddPoint(each[0], each[1])

colorFunc = vtk.vtkColorTransferFunction()
for each in vcolor:
    colorFunc.AddRGBPoint(each[0], each[1], each[2], each[3])

volumGradientOpacity = vtk.vtkPiecewiseFunction()
for each in gOpacity:
    volumGradientOpacity.AddPoint(each[0], each[1])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = dicomImage3DdisplayWidget(polyData=resualtArray, colorFunc=colorFunc, alphaChannelFunc=alphaChannelFunc,
                                    volumGradientOpacity=volumGradientOpacity, spacings=Spacings, position=[0, 0, 0])

    win.show()
    sys.exit(app.exec_())
