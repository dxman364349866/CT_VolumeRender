import vtk
from numpy import *
import numpy as np
import SimpleITK
import matplotlib.pyplot as plt
import matplotlib.image as IMG
from vtk.util.numpy_support import vtk_to_numpy as vtk_to_np

def createVlume(polyData, colorFunc, alphaChannelFunc, volumGradientOpacity ,spacings, position ):

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


pathDicom = "D:/Dicomfile/MT_07/"
idxSlice = 50
reader = SimpleITK.ImageSeriesReader()
filenamesDICOM = reader.GetGDCMSeriesFileNames(pathDicom)

reader.SetFileNames(filenamesDICOM)
imgOriginals = reader.Execute()
datas = SimpleITK.GetArrayFromImage(imgOriginals)
datas = datas.astype(np.int8)

# datas = np.rot90(datas)
DxSize, DySize, DzSize = datas.shape
Spacings = np.array(imgOriginals.GetSpacing())

# print('\n'.join(dir(imgOriginals)))


PosXY = [279, 265]
# PosXY = [111, 158]

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

print(AreaArray.shape)
print(datas.shape)
print(resualtArray.shape)

'''
#==========================Save Numpy to Text=========================
# with open('D:/Dicomfile/Horse/Hello3D.txt', 'w') as outfile:
#     for slice_2d in TmpArray:
#         np.savetxt(outfile, slice_2d)
# np.savetxt('D:/Dicomfile/Horse/Hello3.txt', TmpArray[1])
#=====================================================================
'''



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




volume1 = createVlume(resualtArray, colorFunc, alphaChannelFunc, volumGradientOpacity, Spacings, [0, 0, 0])
volume2 = createVlume(datas, colorFunc, alphaChannelFunc, volumGradientOpacity, Spacings, [-400, 0, 0])

#===========================BoneExtrctor==============================

dv = 1.75
rf = 1

data_matrix = resualtArray
data_matrix = np.rot90(data_matrix, 1)
data_matrix = data_matrix.astype(np.uint8)
xSize, ySize, zSize = data_matrix.shape

dataImporter = vtk.vtkImageImport()
data_string = data_matrix.tostring()
dataImporter.CopyImportVoidPointer(data_string, len(data_string))
dataImporter.SetDataScalarTypeToUnsignedChar()
dataImporter.SetNumberOfScalarComponents(1)

dataImporter.SetDataExtent(0, xSize-1, 0, ySize-1, 0, zSize-1)
dataImporter.SetWholeExtent(0, xSize-1, 0, ySize-1, 0, zSize-1)
dataImporter.SetDataExtentToWholeExtent()
#=============================================================================


# Smoothed pipeline.
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

colors = vtk.vtkNamedColors()
colors.SetColor("ActorColor", [235, 235, 235, 255])


'''
threshold = vtk.vtkImageThreshold ()
threshold.SetInputConnection(smooth.GetOutputPort())
threshold.ThresholdByLower(10)  # remove all soft tissue
threshold.ReplaceInOn()
threshold.SetInValue(0)  # set all values below 400 to 0
threshold.ReplaceOutOn()
threshold.SetOutValue(1)  # set all values above 400 to 1
threshold.Update()


dmc = vtk.vtkDiscreteMarchingCubes()
dmc.SetInputConnection(threshold.GetOutputPort())
# dmc.SetValue(0, 1150)
dmc.GenerateValues(1, 1, 1)
dmc.Update()

meshMapper = vtk.vtkPolyDataMapper()
meshMapper.SetInputConnection(dmc.GetOutputPort())
meshMapper.ScalarVisibilityOff()
# print('\n'.join(dir(meshMapper)))
'''


tmpTransfor = vtk.vtkTransform()
tmpTransfor.Scale(Spacings)
tmpTransfor.Translate(400, 0, 0)

meshActor = vtk.vtkActor()
meshActor.SetMapper(isoSmoothedMapper)
meshActor.SetUserTransform(tmpTransfor)
meshActor.GetProperty().SetColor(colors.GetColor3d("ActorColor"))

#=====================================================================

renderer = vtk.vtkRenderer()
renderWin = vtk.vtkRenderWindow()
renderWin.AddRenderer(renderer)
renderInteractor = vtk.vtkRenderWindowInteractor()
renderInteractor.SetRenderWindow(renderWin)

renderer.AddActor(meshActor)
renderer.AddVolume(volume1)
renderer.AddVolume(volume2)

renderer.SetBackground(0.5, 0.5, 0.5)
renderWin.SetSize(512, 512)

renderInteractor.Initialize()
renderWin.Render()
renderInteractor.Start()



