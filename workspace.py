
"""
Classes: WorkSpace, ScrollArea
WorkSpace class holds all elements displayed to user while working;
holds the scan, tools for drawing, buttons, etc.
Is used as a singleton.
"""

import pickle
import numpy as np
import nibabel as nib
from PyQt5 import QtGui, QtCore, QtWidgets
import FetalMRI_workspace
from Shapes import Shapes
from consts import *
from scan_file import ScanFile
import utils


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

        # holds the row index of the scan currently performing segmentation
        self._segmentation_running = NO_SEG_RUNNING

    def _init_ui(self):

        # store original stylesheets
        self._base_tool_style = self.paintbrush_btn.styleSheet()
        self._base_size_style = self.paintbrush_size1_btn.styleSheet()
        self.tool_chosen.connect(self._emphasize_tool_button)

        self.setAutoFillBackground(True)
        self.setStyleSheet('background-color: rgb(110, 137, 152)')

        # set icons
        self.paintbrush_btn.setIcon(QtGui.QIcon('images/paintbrush.png'))
        self.eraser_btn.setIcon(QtGui.QIcon('images/erase.jpg'))

        # set sizes
        self.frame_number.setFixedSize(self.frame_number.width() + 2, self.frame_number.height())

        # connect buttons
        self.perform_seg_btn.clicked.connect(self._perform_segmentation_wrapper)
        self.save_seg_btn.clicked.connect(self.save_segmentation)
        self.contrast_slider.valueChanged.connect(self._toggle_contrast)

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

        self.polygon_btn.clicked.connect(lambda: self.tool_chosen.emit(POLYGON))

        # set initially chosen buttons with different style
        self.paintbrush_btn.setStyleSheet(self._base_tool_style + ' border-width: 5px;')
        self.paintbrush_size2_btn.setStyleSheet(self._base_size_style + ' border-width: 5px;')
        self.eraser_size2_btn.setStyleSheet(self._base_size_style + ' border-width: 5px;')

        # set up table ui
        self.tableWidget.setHorizontalHeaderLabels(['File', 'Status', 'Remove'])
        self.tableWidget.cellDoubleClicked.connect(self._switch_scan)
        self.runAll_btn.clicked.connect(self._run_all_segmentations)

        # connect buttons and sliders contained in the info box
        self.quantizationSlider.valueChanged.connect(self._toggle_quantization)
        self.show_convex_btn.clicked.connect(self._toggle_convex)
        self.show_brain_halves_btn.clicked.connect(self._toggle_brain_halves)
        self.show_full_seg_btn.clicked.connect(self._toggle_show_seg)
        self.show_csf_btn.clicked.connect(self._toggle_csf)

        # hide info box which is relevant only after segmentation is shown
        self.verticalFrame.hide()

    @QtCore.pyqtSlot()
    def _toggle_csf(self):
        self._all_scans[self._current_scan_idx].show_csf()

    @QtCore.pyqtSlot()
    def _toggle_convex(self):
        self._all_scans[self._current_scan_idx].show_convex()

    @QtCore.pyqtSlot()
    def _toggle_brain_halves(self):
        self._all_scans[self._current_scan_idx].show_brain_halves()

    @QtCore.pyqtSlot()
    def _toggle_show_seg(self):
        '''Show full segmentation, and if more points were drawn, will add them.'''
        self._all_scans[self._current_scan_idx].show_segmentation()

    @QtCore.pyqtSlot(int, int)
    def _switch_scan(self, row, col):
        assert row < len(self._all_scans)
        self._current_scan_idx = row
        self._all_scans[self._current_scan_idx].load_image_label()
        self.scroll_area.set_image(self._all_scans[self._current_scan_idx].image_label)

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
        '''
        Insert all scans which have yet to be segmented, into queue to be segmented, and run them one by one.
        '''
        for i in range(len(self._all_scans)):
            if self._all_scans[i].status == '':
                self._seg_queue.append(i)
                self._all_scans[i].status = QUEUED
                self.tableWidget.setItem(i, 1, QtWidgets.QTableWidgetItem(QUEUED))

        # will execute segmentation on first scan in queue
        self._run_next_seg()

    @QtCore.pyqtSlot(int)
    def _remove_scan(self, scan_idx):
        # TODO: disable remove button while segmentation is performing

        if len(self._all_scans) == 1:
            utils.warn('At least one scan must remain in workspace.')
            return

        # TODO pop up utils.warning message that all work will be lost, do you want to save?
        self.tableWidget.removeRow(scan_idx)
        self._all_scans.pop(scan_idx)

        # choose new current scan
        if scan_idx == 0:
            self._current_scan_idx = 1
        else:
            self._current_scan_idx -= 1

    @QtCore.pyqtSlot(int)
    def _emphasize_tool_button(self, tool_chosen):
        '''Pick the current chosen tool and make the button's border more bold.'''
        # set all buttons to base style
        self.paintbrush_btn.setStyleSheet(self._base_tool_style)
        self.eraser_btn.setStyleSheet(self._base_tool_style)
        self.polygon_btn.setStyleSheet(self._base_tool_style)

        # emphasize chosen tool button
        if tool_chosen == USE_PAINTBRUSH:
            self.paintbrush_btn.setStyleSheet(self._base_tool_style + ' border-width: 5px;')
        elif tool_chosen == USE_ERASER:
            self.eraser_btn.setStyleSheet(self._base_tool_style + ' border-width: 5px;')
        elif tool_chosen == POLYGON:
            self.polygon_btn.setStyleSheet(self._base_tool_style + ' border-width: 5px;')

    def _change_paintbrush_size(self, size):
        # TODO: on scan change, set paintbrush_size
        self._all_scans[self._current_scan_idx].image_label.paintbrush_size = size
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

    def _perform_segmentation_wrapper(self):
        '''
        This methods starts all steps run for performing the segmentation.
        Sets up queue and items in workspace table, and runs the segmentation algorithm.
        '''

        # TODO: in scan file, when 'perform segmentation' is called, perform only if the thread is not already running?

        # if another segmentation is already running, insert request to waiting queue
        # Todo use lock in case current seg finishes at same time, and then does not know that someone is waiting
        if self._segmentation_running != NO_SEG_RUNNING:
            # insert to waiting queue
            self._seg_queue.append(self._current_scan_idx)

            # set status in workspace table
            item = QtWidgets.QTableWidgetItem(QUEUED)
            self.tableWidget.setItem(self._current_scan_idx, 1, item)

        else:
            self._segmentation_running = self._current_scan_idx

            # run perform_segmentation from thread so that progress bar will run in background
            self._all_scans[self._current_scan_idx].run_segmentation()

            # set status in workspace table
            item = QtWidgets.QTableWidgetItem(PROCESSING)
            self.tableWidget.setItem(self._current_scan_idx, 1, item)

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == QtCore.Qt.Key_F:
            self.jump_frame_lineedit.setFocus()
        elif QKeyEvent.key() == QtCore.Qt.Key_E:
            pass
            # Todo implement change focus to Eraser
        elif QKeyEvent.key() == QtCore.Qt.Key_B:
            pass
            # Todo implement change focus to Paint
        elif QKeyEvent.key() == QtCore.Qt.Key_P:
            self._all_scans[self._current_scan_idx].image_label.submit_polygon()
        else:
            QtWidgets.QWidget.keyPressEvent(self, QKeyEvent)

    def perform_segmentation(self):
        '''
        Worker function, runs as code in ScanFile._segmentation_thread
        Calculates and sets the segmentation on the image.
        Do not return anything from this method.
        '''
        segmentation_array = None
        try:
            # change stage title
            self.instructions.setText('<html><head/><body><p align="center">Stage 2:</p><p align="center">'
                                      'Calculating <\p><p>Segmentation...</p><p '
                                      'align="center">(please wait)</p></body></html>')

            segmentation_array = self._all_scans[self._segmentation_running].perform_segmentation()
        except Exception as ex:
            print('perform_segmentation', ex)

        if segmentation_array is None:
            utils.warn('An error occurred while computing the segmentation. Please perform better markings, '
                 'and try again.')
            self.instructions.setText(
                '<html><head/><body><p align="center">Stage 1 [retry]: Boundary Marking...</p><p '
                'align="center">(hover for instructions)</p></body></html>')

            # reset status in workspace table
            item = QtWidgets.QTableWidgetItem('')
            self.tableWidget.setItem(self._segmentation_running, 1, item)

            self.segmentation_finished.emit()
            return

        # update finished status in workspace table
        item = QtWidgets.QTableWidgetItem(SEGMENTED)
        self.tableWidget.setItem(self._segmentation_running, 1, item)

        # show hidden features which are now relevant to work on segmentation
        self.verticalFrame.show()

        self.instructions.setText('<html><head/><body><p align="center">Stage 3: Review Segmentation...</p><p '
                                  'align="center">(hover for instructions)</p></body></html>')
        self.instructions.setToolTip('Use paintbrush and eraser to fix result segmentation.\nWhen finished, '
                                     'save segmentation.')

        self.save_seg_btn.setEnabled(True)
        self.segmentation_finished.emit()  # next segmentation will be run

    def set_brain_volume(self, volume):
        brain_text = "Brain Volume: %.2f mm<sup>3</sup>"
        self.brain_volume_label.setText(brain_text % volume)

    def set_csf_volume(self, volume):
        csf_text = "CSF Volume: %.2f mm<sup>3</sup>"
        self.csf_volume_label.setText(csf_text % volume)
        if self._all_scans[self._current_scan_idx].brain_volume != 0:
            csf_ratio = float(volume / self._all_scans[self._current_scan_idx].brain_volume)
            ratio_text = "CSF to Brain ratio: %.2f" % csf_ratio
            self.csf_brain_prop_label.setText(ratio_text)

    def set_brain_halves_volume(self, left_volume, right_volume):
        left_text = "Left Brain Volume: %.2f mm<sup>3</sup>"
        right_text = "Right Brain Volume: %.2f mm<sup>3</sup>"
        self.left_brain_volume_label.setText(left_text % left_volume)
        self.right_brain_volume_label.setText(right_text % right_volume)

    def _run_next_seg(self):
        '''If there is a scan waiting in queue, perform its segmentation.'''
        if len(self._seg_queue) > 0:
            waiting_idx = self._seg_queue.pop(0)
            self._segmentation_running = waiting_idx
            self._all_scans[waiting_idx].run_segmentation()

            # update status in workspace table
            item = QtWidgets.QTableWidgetItem(PROCESSING)
            self.tableWidget.setItem(waiting_idx, 1, item)
        else:
            self._segmentation_running = NO_SEG_RUNNING

    def _toggle_quantization(self):
        try:
            tick_val = self.quantizationSlider.value()
            self._all_scans[self._current_scan_idx].show_quantization_segmentation(tick_val)
        except Exception as ex:
            print('_toggle_quantization error', ex)

    def toggle_segmentation(self, show):
        '''
        Show/hide the segmentation over the scan displaying.
        :param show: [bool]
        '''
        self._all_scans[self._current_scan_idx].image_label.paint_over = show
        self._all_scans[self._current_scan_idx].image_label.update()

    def toggle_scan(self, show):
        '''
        Show/hide the scan (independant of the segmentation showing).
        :param show: [bool]
        '''
        self._all_scans[self._current_scan_idx].image_label.show_scan = show
        self._all_scans[self._current_scan_idx].image_label.update()

    def save_all_segmentations(self):
        for i in range(len(self._all_scans)):
            if self._all_scans[i].status == SEGMENTED:
                try:
                    self.save_segmentation(i)
                except Exception as ex:
                    print('save segmentation', i, ex)

    def save_segmentation(self, scan_idx=None):
        try:
            if not scan_idx:
                scan_idx = self._current_scan_idx
            segmentation = self._all_scans[scan_idx].image_label.points_to_image()
            if segmentation is None:
                print("Error saving segmentation for scan #%d" %scan_idx)
                return
            segmentation = utils.shape_segtool_2_nifti(segmentation)

            file_dialog = QtWidgets.QFileDialog()
            options = QtWidgets.QFileDialog.Options()
            options |= QtWidgets.QFileDialog.DontUseNativeDialog
            fileName, _ = QtWidgets.QFileDialog.getSaveFileName(file_dialog, "Save segmentation", "",
                                        "Nifti Files (*.nii, *.nii.gz)", options=options)
            if fileName:
                if not (fileName.endswith('.nii') or fileName.endswith('.nii.gz')):
                    fileName += '.nii'
                if not fileName.endswith('.gz'):
                    fileName += '.gz'
                nifti = nib.Nifti1Image(segmentation, np.eye(4))
                nib.save(nifti, fileName)
                print('Segmentation saved to %s' % fileName)
        except Exception as ex:
            print("Save segmentation error: {}".format(ex))

    def set_segmentation(self, segmentation_array):
        self._all_scans[self._current_scan_idx].set_segmentation(segmentation_array)
        self.verticalFrame.show()

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

    @QtCore.pyqtSlot()
    def _toggle_contrast(self):
        tick_val = self.contrast_slider.value()
        self._all_scans[self._current_scan_idx].image_label.change_view(tick_val)


class ScrollArea(QtWidgets.QScrollArea):

    """
    A scroll area on which image_label is set and displayed.
    Allows for convenient scrolling and zooming of image. 
    """

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
        # ignore so that scrolling is handled only by ImageLabel
        if event.type() == QtCore.QEvent.Wheel:
            event.ignore()
