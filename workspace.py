from PyQt5 import QtWidgets
from PyQt5 import QtGui, QtCore
import nibabel as nib
from image_label import ImageDisplay


class WorkSpace(QtWidgets.QWidget):
    '''
    In this window, user performs all of the segmentation work.
    '''

    def __init__(self, nifti_path, parent=None):
        '''
        :param nifti_path [str]: path to Nifti file.
        :param parent [QtWidgets.QWidget]: parent window containing self
        '''
        super(WorkSpace, self).__init__(parent)
        try:
            self._nifti = nib.load(nifti_path)
        except FileNotFoundError:
            print('Error in path %s' % self._source)
            return

        self._array_data = self._nifti.get_data()

        # Nifti file does not show stable shape, sometimes as (num,x,y) and at times as (x,y,num) or (x,num,y)
        num_frames_index = self._nifti.shape.index(min(self._nifti.shape))
        x_orig_index, y_orig_index = 1, 2
        if num_frames_index == 1:
            x_orig_index, y_orig_index = 0, 2
        elif num_frames_index == 2:
            x_orig_index, y_orig_index = 0, 1
        self._array_data = self._array_data.transpose(num_frames_index, x_orig_index, y_orig_index)

        self._init_ui()

    def _init_ui(self):

        self.setBackgroundRole(QtGui.QPalette.Shadow)
        self.setAutoFillBackground(True)

        main_layout = QtWidgets.QVBoxLayout()

        self.image_display = ImageDisplay(self._array_data, self._nifti)

        image_display_layout = QtWidgets.QHBoxLayout()
        image_display_layout.addStretch()
        image_display_layout.addWidget(self.image_display)
        image_display_layout.addStretch()

        main_layout.addStretch()
        main_layout.addLayout(image_display_layout)
        main_layout.addStretch()
        self.setLayout(main_layout)

