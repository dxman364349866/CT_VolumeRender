import numpy as np
import pydicom
import os

# Anatomical planes
TRANSVERSE = AXIAL = 0
FRONTAL = CORONAL = 1
MEDIAN = SAGITTAL = 2
ALLOWED_PLANES = (AXIAL, CORONAL, SAGITTAL)



class DicomData(object):
    ALLOWED_MODALITIES = ('CT', 'MR', 'CR', 'RT')

    def __init__(self, data, **kwargs):
        self._array = data
        self.modality = kwargs.get("modality")

    @classmethod
    def from_files(cls, files):
        """
        :type files: list (str)
        :rtype: DicomData
        """

        data = []
        modality = None
        DicomFiles = []
        spacing = [0, 0, 0]

        DicomFiles = [pydicom.read_file(files + '/' + s) for s in os.listdir(files)]
        DicomFiles.sort(key=lambda x : int(x.InstanceNumber))


        for file in DicomFiles:
            data.append(np.array(file.pixel_array))

        spacing[0] = float(DicomFiles[0].PixelSpacing[0])
        spacing[1] = float(DicomFiles[0].PixelSpacing[1])
        spacing[2] = float(DicomFiles[0].SpacingBetweenSlices)

        # print('\n'.join(dir(DicomFiles[0])))
        # print('----------------------------------------')
        # print(DicomFiles[0].SpacingBetweenSlices)
        # print('----------------------------------------')
        # print(DicomFiles[0].PixelSpacing)
        # print(DicomFiles[0].SliceThickness)
        # print(spacing)

        returnData = np.array(data)
        return returnData, spacing

    @classmethod
    def _read_pixel_data(cls, f):
        """
        :rtype: np.ndarray
        """
        # if f.Modality == "CT":
        #     data = f.RescaleSlope * f.pixel_array + f.RescaleIntercept
        #     return np.array(data)
        # else:
        #     return np.array(f.pixel_array)

        return np.array(f.pixel_array)


    @property
    def shape(self):
        """
        :rtype: tuple
        """
        return self._array.shape

    @property
    def array(self):
        """The underlying numpy array.

        :rtype: np.ndarray
        """
        return self._array

    def get_slice(self, plane, n):
        # if plane not in ALLOWED_PLANES:
        #     raise ValueError("Invalid plane identificator (allowed are 0,1,2)")
        # index = [slice(None, None, None) for i in range(3)]
        # index[plane] = n
        return self._array[0]

    def get_slice_shape(self, plane):
        # TODO:
        shape = list(self.shape)
        # shape.pop(plane)
        return shape




