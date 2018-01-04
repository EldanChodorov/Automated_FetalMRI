import nibabel as nib
from PyQt5 import QtGui
from PyQt5 import QtWidgets
import numpy as np
import FetalMRI_workspace
from threading import Thread
from collections import defaultdict
import numpy as np
from threading import Thread
from PyQt5 import QtWidgets
from PyQt5 import QtGui, QtCore
import qimage2ndarray
from skimage import color
import cv2
import segment3d_itk
import nibabel as nib
from image_label import ImageDisplay, ImageLabel


USE_PAINTBRUSH = 1
USE_SQUARE = 2
USE_ERASER = 3
ERASER_WIDTH = 15


class WorkSpace(QtWidgets.QWidget, FetalMRI_workspace.Ui_workspace):
    '''
    In this window, user performs all of the segmentation work.
    '''

    # signal that a new tool was chosen
    tool_chosen = QtCore.pyqtSignal(int)

    def __init__(self, nifti_path, parent=None):
        '''
        :param nifti_path [str]: path to Nifti file.
        :param parent [QtWidgets.QWidget]: parent window containing self
        '''
        QtWidgets.QWidget.__init__(self, parent)
        FetalMRI_workspace.Ui_workspace.__init__(self)

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

        # defined in FetalMRI_workspace.Ui_workspace
        self.setupUi(self)

        # normalize images
        self.frames = (self._array_data.astype(np.float64) / np.max(self._array_data)) * 255

        # index of current frame displayed
        self.frame_displayed_index = 0

        # numpy array of frames with segmentation as binary images
        self._segmentation_array = None

        # perform segmentation algorithm in separate thread so that gui is not frozen
        self._segmentation_thread = Thread(target=self._perform_segmentation)
        self._segmentation_thread.setDaemon(True)

        # Label with ImageDisplay
        self._image_label = ImageLabel(self.frames, self)
        self.ImageLayout.addWidget(self._image_label)

    def _connect_buttons(self):
        self.perform_seg_btn.clicked.connect(self._perform_segmentation_wrapper)
        self.paintbrush_btn.clicked.connect(lambda: self.tool_chosen.emit(USE_PAINTBRUSH))
        self.eraser_btn.clicked.connect(lambda: self.tool_chosen.emit(USE_ERASER))
        self.square_btn.clicked.connect(lambda: self.tool_chosen.emit(USE_SQUARE))

    def _perform_segmentation_wrapper(self):

        # setup progress bar
        self._progress_bar = QtWidgets.QProgressBar(self)
        # TODO: text is not displaying, fix.
        self._progress_bar.setFormat('Segmentation running...')
        self._progress_bar.setTextVisible(True)
        self._progress_bar.setMinimum(0)
        self._progress_bar.setMaximum(0)
        self._progress_bar.resize(60, 20)
        self._main_layout.addStretch()
        self._main_layout.addWidget(self._progress_bar)
        self._main_layout.addStretch()

        # disable button so that only one segmentation will run at each time
        # TODO: re-enable when loading or rechoosing points
        self._segment_button.setEnabled(False)

        # run perform_segmentation from thread so that progress bar will run in background
        self._segmentation_thread.start()

    def _remove_progress_bar(self):
        self._main_layout.removeWidget(self._progress_bar)
        self._progress_bar.deleteLater()

    def _perform_segmentation(self):
        try:
            if not self._image_label or not self._image_label.chosen_points:
                return
            seeds = []
            for frame_idx, frame_points in self._image_label.chosen_points.items():
                if frame_points:
                    for pos in frame_points:
                        translated_pos = self._image_label.label_to_image_pos(pos)
                        seeds.append((frame_idx, translated_pos.y(), translated_pos.x()))

            # run segmentation algorithm in separate thread so that gui does not freeze
            import time
            a = time.time()
            self._segmentation_array = segment3d_itk.segmentation_3d(self.frames, seeds) * 255
            print(time.time() - a)

            self._remove_progress_bar()

            if self._segmentation_array is None:
                self._segment_button.setEnabled(True)
                return

            self.set_segmentation(self._segmentation_array)

        except Exception as ex:
            print(ex, type(ex))

    def set_segmentation(self, segmentation_array):
        ''' Set given segmentation on top of scan image.'''
        self._image_label.frames = overlap_images(self.frames, segmentation_array)

        # set images to image label
        self._image_label.frame_displayed_index = 0
        self._image_label.set_image(self._image_label.frames[0])
        self._image_label.update()

    def save_segmentation(self, path):
        nifti = nib.Nifti1Image(self._segmentation_array, np.eye(4))
        nib.save(nifti, path)





def overlap_images(background_img_list, mask_img_list):
    '''
    Color mask in background image.
    :param background_img_list: [numpy.ndarray] main image to be in background, shape: num_images, x, y
    :param mask_img_list: [numpy.ndarray] binary image, display only white over image1
    :return: numpy.ndarray
    '''
    if background_img_list.shape != mask_img_list.shape:
        return mask_img_list
    colored = []
    for img, mask in zip(background_img_list, mask_img_list):
        # add RGB channels
        color_img = np.dstack((img,) * 3).astype(np.float64)
        mask_img = np.dstack((mask,) * 3).astype(np.float64)
        mask_img_orig = np.array(mask_img)

        # place original image over mask where there is no segmentation
        mask_img[np.where(mask_img_orig != 255)] = color_img[np.where(mask_img_orig != 255)]

        # color mask in red  TODO fix, doesn't work
        mask_img[np.where(mask_img_orig == 255), 0] = 255
        mask_img[np.where(mask_img_orig == 255), 1] = 255
        mask_img[np.where(mask_img_orig == 255), 2] = 255

        alpha = 0.6
        added_image = cv2.addWeighted(color_img, alpha, mask_img, 1-alpha, gamma=0)
        colored.append(added_image)
    return colored
