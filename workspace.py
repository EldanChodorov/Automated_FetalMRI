import cv2
import pickle
import numpy as np
import nibabel as nib
from threading import Thread
from PyQt5 import QtGui, QtCore, QtWidgets
import FetalMRI_workspace
import segment3d_itk
from skimage.exposure import equalize_adapthist
from image_label import ImageLabel
from Shapes import Shapes
from consts import USE_PAINTBRUSH, INNER_SQUARE, OUTER_SQUARE, USE_ERASER,\
    BRUSH_WIDTH_LARGE, BRUSH_WIDTH_MEDIUM, BRUSH_WIDTH_SMALL, ALPHA_TRANSPARENT


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

        self._nifti_path = nifti_path

        try:
            self._nifti = nib.load(self._nifti_path)
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

        # TODO: perform in separate thread somehow
        contrasted_frames = self._histogram_equalization(self.frames)

        # store original stylesheets
        self._base_tool_style = self.paintbrush_btn.styleSheet()
        self._base_size_style = self.paintbrush_size1_btn.styleSheet()
        self.tool_chosen.connect(self._emphasize_tool_button)

        # Label with ImageLabel
        try:
            self._image_label = ImageLabel(self.frames, contrasted_frames, self)
            self.MainLayout.addWidget(self._image_label)
            self.MainLayout.addStretch(1)
        except Exception as ex:
            print('image label init', ex)

        self._init_ui()

    def _init_ui(self):

        self.setAutoFillBackground(True)
        self.setStyleSheet('background-color: rgb(110, 137, 152)')

        # set sizes
        self.frame_number.setFixedSize(self.frame_number.width() + 2, self.frame_number.height())

        # connect buttons
        self.perform_seg_btn.clicked.connect(self._perform_segmentation_wrapper)
        self.save_seg_btn.clicked.connect(self.save_segmentation)
        self.standard_view_btn.clicked.connect(lambda: self._contrast_button_clicked(False))
        self.contrast_view_btn.clicked.connect(lambda: self._contrast_button_clicked(True))

        # connect brushes buttons
        self.paintbrush_btn.clicked.connect(lambda: self.tool_chosen.emit(USE_PAINTBRUSH))
        self.paintbrush_size1_btn.clicked.connect(lambda: self._change_paintbrush_size(BRUSH_WIDTH_SMALL))
        self.paintbrush_size2_btn.clicked.connect(lambda: self._change_paintbrush_size(BRUSH_WIDTH_MEDIUM))
        self.paintbrush_size3_btn.clicked.connect(lambda: self._change_paintbrush_size(BRUSH_WIDTH_LARGE))

        self.eraser_btn.clicked.connect(lambda: self.tool_chosen.emit(USE_ERASER))
        self.eraser_size1_btn.clicked.connect(lambda: self._change_eraser_size(BRUSH_WIDTH_SMALL))
        self.eraser_size2_btn.clicked.connect(lambda: self._change_eraser_size(BRUSH_WIDTH_MEDIUM))
        self.eraser_size3_btn.clicked.connect(lambda: self._change_eraser_size(BRUSH_WIDTH_LARGE))

        self.outer_square_btn.clicked.connect(lambda: self.tool_chosen.emit(OUTER_SQUARE))
        self.inner_square_btn.clicked.connect(lambda: self.tool_chosen.emit(INNER_SQUARE))

        # set initially chosen buttons with different style
        self.paintbrush_btn.setStyleSheet(self._base_tool_style + ' border-width: 5px;')
        self.paintbrush_size2_btn.setStyleSheet(self._base_size_style + ' border-width: 5px;')
        self.eraser_size2_btn.setStyleSheet(self._base_size_style + ' border-width: 5px;')

    @QtCore.pyqtSlot(int)
    def _emphasize_tool_button(self, tool_chosen):
        # set all buttons to base style
        self.paintbrush_btn.setStyleSheet(self._base_tool_style)
        self.eraser_btn.setStyleSheet(self._base_tool_style)
        self.inner_square_btn.setStyleSheet(self._base_tool_style)
        self.outer_square_btn.setStyleSheet(self._base_tool_style)

        # emphasize chosen tool button
        if tool_chosen == USE_PAINTBRUSH:
            self.paintbrush_btn.setStyleSheet(self._base_tool_style + ' border-width: 5px;')
        elif tool_chosen == USE_ERASER:
            self.eraser_btn.setStyleSheet(self._base_tool_style + ' border-width: 5px;')
        elif tool_chosen == INNER_SQUARE:
            self.inner_square_btn.setStyleSheet(self._base_tool_style + ' border-width: 5px;')
        elif tool_chosen == OUTER_SQUARE:
            self.outer_square_btn.setStyleSheet(self._base_tool_style + ' border-width: 5px;')

    def _change_paintbrush_size(self, size):
        self._image_label.paintbrush_size = size
        self.tool_chosen.emit(USE_PAINTBRUSH)

        self.paintbrush_size1_btn.setStyleSheet(self._base_size_style)
        self.paintbrush_size2_btn.setStyleSheet(self._base_size_style)
        self.paintbrush_size3_btn.setStyleSheet(self._base_size_style)

        # emphasize border of chosen button
        if size == BRUSH_WIDTH_SMALL:
            self.paintbrush_size1_btn.setStyleSheet(self._base_size_style + ' border-width: 5px;')
        elif size == BRUSH_WIDTH_MEDIUM:
            self.paintbrush_size2_btn.setStyleSheet(self._base_size_style + ' border-width: 5px;')
        else:
            self.paintbrush_size3_btn.setStyleSheet(self._base_size_style + ' border-width: 5px;')

    def _change_eraser_size(self, size):
        self._image_label.eraser_size = size
        self._image_label.shapes.eraser_width = size
        self.tool_chosen.emit(USE_ERASER)

        self.eraser_size1_btn.setStyleSheet(self._base_size_style)
        self.eraser_size2_btn.setStyleSheet(self._base_size_style)
        self.eraser_size3_btn.setStyleSheet(self._base_size_style)

        # emphasize border of chosen button
        if size == BRUSH_WIDTH_SMALL:
            self.eraser_size1_btn.setStyleSheet(self._base_size_style + ' border-width: 5px;')
        elif size == BRUSH_WIDTH_MEDIUM:
            self.eraser_size2_btn.setStyleSheet(self._base_size_style + ' border-width: 5px;')
        else:
            self.eraser_size3_btn.setStyleSheet(self._base_size_style + ' border-width: 5px;')

    def _contrast_button_clicked(self, contrast_view):
        '''
        Set whether frames shown are regular or contrasted.
        :param contrast_view: [bool] if True, show contrasted frames, otherwise regular.
        '''
        self._image_label.change_view(contrast_view)
        self.contrast_view_btn.setEnabled(not contrast_view)
        self.standard_view_btn.setEnabled(contrast_view)

    def _perform_segmentation_wrapper(self):
        # setup progress bar
        self._progress_bar = QtWidgets.QProgressBar(self)
        # TODO: text is not displaying, fix.
        self._progress_bar.setFormat('Segmentation running...')
        self._progress_bar.setTextVisible(True)
        self._progress_bar.setMinimum(0)
        self._progress_bar.setMaximum(0)
        self._progress_bar.resize(60, 20)
        self.MainLayout.addStretch()
        self.MainLayout.addWidget(self._progress_bar)
        self.MainLayout.addStretch()

        # disable button so that only one segmentation will run at each time
        # TODO: re-enable when loading or rechoosing points
        self.perform_seg_btn.setEnabled(False)

        # run perform_segmentation from thread so that progress bar will run in background
        self._segmentation_thread.start()

    def _remove_progress_bar(self):
        self.MainLayout.removeWidget(self._progress_bar)
        self._progress_bar.deleteLater()

    def _perform_segmentation(self):
        try:
            if not self._image_label:
                return
            all_points = self._image_label.shapes.all_points()
            if not all_points:
                return

            # change stage title
            self.instructions.setText('<html><head/><body><p align="center">Stage 2: Calculating Segmentation...</p><p '
                                      'align="center">(please wait)</p></body></html>')

            seeds = []
            for frame_idx, frame_points in all_points.items():
                if frame_points:
                    for pos in frame_points:
                        translated_pos = self._image_label.label_to_image_pos(pos)
                        seeds.append((frame_idx, translated_pos.y(), translated_pos.x()))

            # run segmentation algorithm in separate thread so that gui does not freeze
            self._segmentation_array = segment3d_itk.segmentation_3d(self.frames, seeds) * 255

            self._remove_progress_bar()

            if self._segmentation_array is None:
                self.perform_seg_btn.setEnabled(True)
                self.instructions.setText(
                    '<html><head/><body><p align="center">Stage 1 [retry]: Boundary Marking...</p><p '
                    'align="center">(hover for instructions)</p></body></html>')
                return

            self.save_seg_btn.setEnabled(True)
            self.set_segmentation(self._segmentation_array)

        except Exception as ex:
            print(ex, type(ex))

    def set_segmentation(self, segmentation_array):
        ''' Set given segmentation on top of scan image.'''
        print('set segmentation', segmentation_array.shape)
        # self._image_label.frames = overlap_images(self.frames, segmentation_array)
        self._image_label.set_segmentation(segmentation_array)

        # set images to image label
        self._image_label.frame_displayed_index = 0
        self._image_label.set_image(self._image_label.frames[0])
        # self._image_label.update()

        # update stage title text
        self.instructions.setText('<html><head/><body><p align="center">Stage 3: Review Segmentation...</p><p '
                                  'align="center">(hover for instructions)</p></body></html>')
        self.instructions.setToolTip('Use paintbrush and eraser to fix result segmentation.\nWhen finished, '
                                     'save segmentation.')

    def save_segmentation(self):
        segmentation = self._image_label.points_to_image()
        segmentation = segmentation.transpose(2, 0, 1)  # convert to (x, y, num_frames)
        try:
            file_dialog = QtWidgets.QFileDialog()
            options = QtWidgets.QFileDialog.Options()
            options |= QtWidgets.QFileDialog.DontUseNativeDialog
            fileName, _ = QtWidgets.QFileDialog.getSaveFileName(file_dialog, "Save segmentation", "",
                                        "Nifti Files (*.nii, *.nii.gz)", options=options)
            if fileName:
                print('saving size', segmentation.shape)
                nifti = nib.Nifti1Image(segmentation, np.eye(4))
                nib.save(nifti, fileName)
                print('Segmentation saved to %s' % fileName)
        except Exception as ex:
            print(ex)

    def _histogram_equalization(self, frames):
        '''
        Perform histogram equalization on the given images to improve contrast.
        :param frames: [numpy.ndarray] list of images
        :return: equalized frames, same type and shape of input.
        '''
        equalized_frames = np.zeros(frames.shape)
        for i in range(frames.shape[0]):
            hist, bins = np.histogram(frames[i].flatten(), bins=256, normed=True)
            cdf = hist.cumsum()  # cumulative distribution function
            cdf = 255 * cdf / cdf[-1]  # normalize

            # use linear interpolation of cdf to find new pixel values
            image_equalized = np.interp(frames[i].flatten(), bins[:-1], cdf)
            equalized_frames[i] = image_equalized.reshape(frames[i].shape)

        return equalized_frames

    def save_points(self):
        '''If exists, save current points that were marked on screen by user.'''
        if self._image_label:
            self._image_label.shapes.save(self._nifti_path)

    def load_points(self):
        '''Load a file containing points previously marked by user for current scans.'''
        if self._image_label:
            try:
                file_dialog = QtWidgets.QFileDialog()
                options = QtWidgets.QFileDialog.Options()
                options |= QtWidgets.QFileDialog.DontUseNativeDialog
                chosen_file, _ = QtWidgets.QFileDialog.getOpenFileName(file_dialog, "Choose points PICKLE file", "",
                                                      "Pickle Files (*.pickle)", options=options)
                if chosen_file.endswith('.pickle'):
                    with open(chosen_file, 'rb') as f:
                        loaded = pickle.load(f)
                    if type(loaded) == Shapes:
                        self._image_label.shapes = loaded
                        self._image_label.alpha_channel = ALPHA_TRANSPARENT
                        return
            except EOFError:
                print('Empty file.')
        print('Error in loading file.')


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
