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
from consts import *
from scan_file import ScanFile


class WorkSpace(QtWidgets.QWidget, FetalMRI_workspace.Ui_workspace):
    '''
    In this window, user performs all of the segmentation work.
    '''

    # signal that a new tool was chosen
    tool_chosen = QtCore.pyqtSignal(int)

    # signal that a segmentation has finished running
    segmentation_finished = QtCore.pyqtSignal()

    def __init__(self, nifti_path, parent=None):
        '''
        :param nifti_path [str]: path to Nifti file.
        :param parent [QtWidgets.QWidget]: parent window containing self
        '''
        QtWidgets.QWidget.__init__(self, parent)
        FetalMRI_workspace.Ui_workspace.__init__(self)

        # defined in FetalMRI_workspace.Ui_workspace
        self.setupUi(self)

        self._init_ui()

        # all nifti paths held in workspace
        self._all_scans = []
        self._all_scans.append(ScanFile(nifti_path, self))
        self._current_scan_idx = 0

        # display image label
        self._all_scans[self._current_scan_idx].load_image_label()

        # add item & remove button to table
        item = QtWidgets.QTableWidgetItem(str(self._all_scans[self._current_scan_idx]))
        self.tableWidget.setItem(0, 0, item)
        button = QtWidgets.QPushButton('X')
        button.clicked.connect(lambda: self._remove_scan(0))
        self.tableWidget.setCellWidget(0, 2, button)

        # create scrollArea containing the current image label
        self.scroll_area = ScrollArea(self._all_scans[self._current_scan_idx].image_label)
        self.scrollLayout.addWidget(self.scroll_area)

        # scans which are in queue waiting to perform segmentation
        self._seg_queue = []
        self.segmentation_finished.connect(self._run_next_seg)

    def _init_ui(self):

        # store original stylesheets
        self._base_tool_style = self.paintbrush_btn.styleSheet()
        self._base_size_style = self.paintbrush_size1_btn.styleSheet()
        self.tool_chosen.connect(self._emphasize_tool_button)

        self.setAutoFillBackground(True)
        self.setStyleSheet('background-color: rgb(110, 137, 152)')

        # set sizes
        self.frame_number.setFixedSize(self.frame_number.width() + 2, self.frame_number.height())

        # connect buttons
        self.perform_seg_btn.clicked.connect(self._perform_segmentation_wrapper)
        self.save_seg_btn.clicked.connect(self.save_segmentation)
        self.standard_view_btn.clicked.connect(lambda: self._contrast_button_clicked(False))
        self.contrast_view_btn.clicked.connect(lambda: self._contrast_button_clicked(True))

        # connect lineEdit
        self.jump_frame_lineedit.returnPressed.connect(self._change_frame_number)

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

        # set up table ui
        self.tableWidget.setHorizontalHeaderLabels(['File', 'Status', 'Remove'])
        self.tableWidget.cellDoubleClicked.connect(self._switch_scan)

    @QtCore.pyqtSlot(int, int)
    def _switch_scan(self, row, col):
        assert row < len(self._all_scans)
        self._current_scan_idx = row
        try:
            self._all_scans[self._current_scan_idx].load_image_label()
            self.scroll_area.set_image(self._all_scans[self._current_scan_idx].image_label)
        except Exception as ex:
            print(ex)

    def add_scan(self, nifti_path):
        new_scan = ScanFile(nifti_path, self)
        self._all_scans.append(new_scan)

        # add to workspace table
        item = QtWidgets.QTableWidgetItem(str(new_scan))
        full_rows = self.tableWidget.rowCount()
        self.tableWidget.insertRow(full_rows)
        self.tableWidget.setItem(full_rows, 0, item)

        # add remove button to table
        button = QtWidgets.QPushButton('X')
        button.clicked.connect(lambda: self._remove_scan(full_rows))
        self.tableWidget.setCellWidget(full_rows, 2, button)

    def _run_all_segmentations(self):
        # todo CREATE SEG QUEUE CLASS AND JUST PUSH IN TASKS
        pass
        self._seg_queue = range(len(self._all_scans))


    @QtCore.pyqtSlot(int)
    def _remove_scan(self, scan_idx):

        if len(self._all_scans) == 1:
            warn('At least one scan must remain in workspace.')
            return

        # TODO pop up warning message that all work will be lost, do you want to save?
        self.tableWidget.removeRow(scan_idx)
        self._all_scans.pop(scan_idx)

        # choose new current scan
        if scan_idx == 0:
            self._current_scan_idx = 1
        else:
            self._current_scan_idx -= 1

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
        self._all_scans[self._current_scan_idx].image_label.paintbrush_size = size # TODO: on scan change, set paintbrush_size
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
        self._all_scans[self._current_scan_idx].image_label.eraser_size = size
        self._all_scans[self._current_scan_idx].image_label.shapes.eraser_width = size
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

    @QtCore.pyqtSlot()
    def _change_frame_number(self):
        try:
            frame_number = int(self.jump_frame_lineedit.text())
        except ValueError:
            '''frame number must be integer'''
        else:
            self._all_scans[self._current_scan_idx].image_label.change_frame_number(frame_number)
        self.jump_frame_lineedit.clear()

    def _contrast_button_clicked(self, contrast_view):
        '''
        Set whether frames shown are regular or contrasted.
        :param contrast_view: [bool] if True, show contrasted frames, otherwise regular.
        '''
        self._all_scans[self._current_scan_idx].image_label.change_view(contrast_view)
        self.contrast_view_btn.setEnabled(not contrast_view)
        self.standard_view_btn.setEnabled(contrast_view)

    def _setup_progress_bar(self):
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

    def _perform_segmentation_wrapper(self):

        # self._setup_progress_bar()

        # disable button so that only one segmentation will run at each time
        # TODO: re-enable when loading or rechoosing points
        self.perform_seg_btn.setEnabled(False)

        # if another segmentation is already running, insert request to waiting queue
        # Todo use lock in case current seg finishes at same time, and then does not know that someone is waiting
        if len(self._seg_queue) > 0:
            self._seg_queue.append(self._current_scan_idx)
        else:
            # run perform_segmentation from thread so that progress bar will run in background
            self._all_scans[self._current_scan_idx].run_segmentation()
            item = QtWidgets.QTableWidgetItem(self._all_scans[self._current_scan_idx].status)
            # self.tableWidget.setCellWidget(self._current_scan_idx, 1, item)

    def _remove_progress_bar(self):
        self.MainLayout.removeWidget(self._progress_bar)
        self._progress_bar.deleteLater()

    def perform_segmentation(self):
        try:
            # change stage title
            self.instructions.setText('<html><head/><body><p align="center">Stage 2: Calculating Segmentation...</p><p '
                                      'align="center">(please wait)</p></body></html>')

            segmentation_array = self._all_scans[self._current_scan_idx].perform_segmentation()

            # update workspace table
            item = QtWidgets.QTableWidgetItem(self._all_scans[self._current_scan_idx].status)
            self.tableWidget.setCellWidget(self._current_scan_idx, 1, item)

            self._remove_progress_bar()

            if segmentation_array is None:
                self.perform_seg_btn.setEnabled(True)
                self.instructions.setText(
                    '<html><head/><body><p align="center">Stage 1 [retry]: Boundary Marking...</p><p '
                    'align="center">(hover for instructions)</p></body></html>')
                return

            self.save_seg_btn.setEnabled(True)
            self.set_segmentation(segmentation_array)
            self.segmentation_finished.emit()  # next segmentation will be run

        except Exception as ex:
            print(ex, type(ex))

    def _run_next_seg(self):
        '''If there is a scan waiting in queue, perform its segmentation.'''
        if len(self._seg_queue) > 0:
            waiting_idx = self._seg_queue.pop(0)
            self._all_scans[waiting_idx].run_segmentation()
            item = QtWidgets.QTableWidgetItem(self._all_scans[waiting_idx].status)
            self.tableWidget.setCellWidget(waiting_idx, 1, item)

    def toggle_segmentation(self, show):
        '''
        Show/hide the segmentation over the scan displaying.
        :param show: [bool]
        '''
        self._all_scans[self._current_scan_idx].image_label.show_segmentation = show
        self._all_scans[self._current_scan_idx].image_label.update()

    def set_segmentation(self, segmentation_array):
        ''' Set given segmentation on top of scan image.'''
        print('set segmentation', segmentation_array.shape)
        self._all_scans[self._current_scan_idx].set_segmentation(segmentation_array)

        # update stage title text
        self.instructions.setText('<html><head/><body><p align="center">Stage 3: Review Segmentation...</p><p '
                                  'align="center">(hover for instructions)</p></body></html>')
        self.instructions.setToolTip('Use paintbrush and eraser to fix result segmentation.\nWhen finished, '
                                     'save segmentation.')

    def save_segmentation(self):
        segmentation = self._all_scans[self._current_scan_idx].image_label.points_to_image()
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

    def save_points(self):
        '''If exists, save current points that were marked on screen by user.'''
        self._all_scans[self._current_scan_idx].image_label.shapes.save(self._nifti_path)

    def load_points(self):
        '''Load a file containing points previously marked by user for current scans.'''
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
                    self._all_scans[self._current_scan_idx].image_label.shapes = loaded
                    self._all_scans[self._current_scan_idx].image_label.alpha_channel = ALPHA_TRANSPARENT
                    return
            else:
                print("Implement! read segmentation from file and convert to shapes")
        except EOFError:
            print('Empty file.')


class ScrollArea(QtWidgets.QScrollArea):

    def __init__(self, image_label):
        QtWidgets.QScrollArea.__init__(self)
        self.setStyleSheet('background-color:  rgb(4, 51, 57);')
        self.setWidget(image_label)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setVisible(True)
        self.verticalScrollBar().setPageStep(100)
        self.horizontalScrollBar().setPageStep(100)

    def set_image(self, new_label):
        # first take away from scrollArea the ownership over label, so that it will not delete it
        placeholder = self.takeWidget()
        self.setWidget(new_label)

    def wheelEvent(self, event):
        if event.type() == QtCore.QEvent.Wheel:
            event.ignore()


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


def warn(main_msg):
    '''
    Pop up a warning message box.
    '''
    msg_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, main_msg, main_msg, QtWidgets.QMessageBox.Ok)
    msg_box.setWindowTitle('Seg Tool Warning')
    msg_box.setMinimumSize(100, 200)
    msg_box.exec_()

