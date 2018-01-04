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


USE_PAINTBRUSH = 1
USE_SQUARE = 2
USE_ERASER = 3
ERASER_WIDTH = 15


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


class ImageLabel(QtWidgets.QLabel):

    # emits (frame idx, pos) of point chosen from images
    point_chosen = QtCore.pyqtSignal(tuple)

    def __init__(self, frames, workspace_parent):
        '''
        :param frames: [numpy.ndarray] list of images
        :param image_display: [WorkSpace]
        '''
        QtWidgets.QLabel.__init__(self, workspace_parent)

        # ImageDisplay holding this ImageLabel instance
        self._parent = workspace_parent

        # numpy array, list of images
        self.frames = frames

        # index of current frame displayed
        self.frame_displayed_index = 0

        # dict of frame#: points chosen manually by user per each frame
        self.chosen_points = defaultdict(list)

        # if using square tool, store here first corner clicked with mouse
        self._square_corner = None

        self._zoom = 1.0

        self.setContentsMargins(0, 0, 0, 0)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setFixedSize(512, 512)
        self.set_image(self.frames[self.frame_displayed_index])

        # decide what to do with point clicks (paint/square/erase)
        self._tool_chosen = USE_PAINTBRUSH
        self._parent.tool_chosen.connect(self._update_tool_in_use)

    @QtCore.pyqtSlot(int)
    def _update_tool_in_use(self, tool_chosen):
        self._tool_chosen = tool_chosen

    def sizeHint(self):
        # TODO: set label minimum size
        return QtCore.QSize(512, 512)

    def mouseMoveEvent(self, QMouseEvent):
        pos = QMouseEvent.pos()
        if self._tool_chosen == USE_PAINTBRUSH:
            self.chosen_points[self.frame_displayed_index].append(pos)
        elif self._tool_chosen == USE_ERASER:
            orig_x = pos.x()
            orig_y = pos.y()
            for i in range(-ERASER_WIDTH, ERASER_WIDTH):
                for j in range(-ERASER_WIDTH, ERASER_WIDTH):
                    pos.setX(orig_x+i)
                    pos.setY(orig_y+i)
                    if pos in self.chosen_points[self.frame_displayed_index]:
                        self.chosen_points[self.frame_displayed_index].remove(pos)

        # update so that paintEvent will be called
        self.update()

    def mousePressEvent(self, QMouseEvent):
        if self._tool_chosen == USE_SQUARE:
            self._square_corner = QMouseEvent.pos()

    def _handle_square_clicked(self, corner1, corner2):
        '''Calculate all points inside square.'''
        first_x, first_y = corner1.x(), corner1.y()
        second_x, second_y = corner2.x(), corner2.y()
        if first_x == second_x or first_y == second_y:
            return

        if first_x < second_x:
            start_x, end_x = first_x, second_x
        else:
            start_x, end_x = second_x, first_x
        if first_y < second_y:
            start_y, end_y = first_y, second_y
        else:
            start_y, end_y = second_y, first_y
        for x in range(start_x, end_x):
            self.chosen_points[self.frame_displayed_index].append(QtCore.QPoint(x, start_y))
            self.chosen_points[self.frame_displayed_index].append(QtCore.QPoint(x, end_y))
        for y in range(start_y, end_y):
            self.chosen_points[self.frame_displayed_index].append(QtCore.QPoint(start_x, y))
            self.chosen_points[self.frame_displayed_index].append(QtCore.QPoint(end_x, y))

    def mouseReleaseEvent(self, cursor_event):
        if self._tool_chosen == USE_SQUARE and self._square_corner:
            # using square tool
            self._handle_square_clicked(self._square_corner, cursor_event.pos())
            self._square_corner = None
            self.update()
        else:
            # using eraser or paintbrush tool
            self.mouseMoveEvent(cursor_event)
            # update() is called in mouseMoveEvent

    def label_to_image_pos(self, label_pos):
        # image is of size 512x512 pixels
        label_x, label_y = float(label_pos.x()), float(label_pos.y())
        image_x = (label_x / self.width()) * 512
        image_y = (label_y / self.height()) * 512
        return QtCore.QPoint(image_x, image_y)

    def paintEvent(self, paint_event):
        painter = QtGui.QPainter(self)

        # draw image first so that points will be on top of image
        painter.drawPixmap(self.rect(), self._displayed_pixmap)

        pen = QtGui.QPen()
        pen.setWidth(5)
        pen.setColor(QtGui.QColor('blue'))
        painter.setPen(pen)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        for pos in self.chosen_points[self.frame_displayed_index]:
            painter.drawPoint(pos)

    def set_image(self, img_numpy_array):

        image = qimage2ndarray.array2qimage(img_numpy_array)
        if image.isNull():
            image = QtGui.QImage('images\\unavailable.jpg')
        qimg = QtGui.QPixmap.fromImage(image)
        self._displayed_pixmap = QtGui.QPixmap(qimg)
        # scale image to fit label
        self._displayed_pixmap.scaled(self.width(), self.height(), QtCore.Qt.KeepAspectRatio)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setScaledContents(True)
        self.setMinimumSize(512, 512)
        self.show()

    def wheelEvent(self, event):
        '''Change frames when user uses wheel scroll.'''
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ControlModifier:
            print('control modifier')
            self._zoom = self._zoom + event.angleDelta().y() / 1200.0
            if self._zoom < 0:
                self._zoom = 0
            # self._img_pixmap = QtGui.QPixmap(self._img_pixmap, )
            # TODO: reset pixmap with zoom. maybe easier to use qgraphicsview instead of label/widget?

        direction_forwards = event.angleDelta().y() > 0
        if direction_forwards:
            self.frame_displayed_index += 1
        else:
            self.frame_displayed_index -= 1

        # interpolate to start/end if reached end/start
        if self.frame_displayed_index >= len(self.frames):
            self.frame_displayed_index = 0
        elif self.frame_displayed_index < 0:
            self.frame_displayed_index = len(self.frames) - 1

        # set new image and change frame number label

        self.set_image(self.frames[self.frame_displayed_index])
        self._parent.frame_number.setText(str(self.frame_displayed_index + 1) + "/" + str(len(self.frames)))

        self.update()


class ImageDisplay(QtWidgets.QWidget):

    def __init__(self, frames, nifti_obj, parent=None):
        '''
        :param frames: array data of shape (num_images, x, y) 
        :param nifti_obj: [Nifti]
        '''
        QtWidgets.QWidget.__init__(self, parent)

        # normalize images
        self.frames = (frames.astype(np.float64) / np.max(frames)) * 255

        # index of current frame displayed
        self.frame_displayed_index = 0

        self._nifti = nifti_obj

        # numpy array of frames with segmentation as binary images
        self._segmentation_array = None

        self._init_ui()

        # perform segmentation algorithm in separate thread so that gui is not frozen
        self._segmentation_thread = Thread(target=self._perform_segmentation)
        self._segmentation_thread.setDaemon(True)

    def _init_ui(self):
        self._main_layout = QtWidgets.QVBoxLayout()

        # user explanation and label of frame number
        # text_layout = QtWidgets.QHBoxLayout()
        # user_initial_explanation = QtWidgets.QLabel(
        #     'Scroll through frames, and several points inside the brain.')
        # user_initial_explanation.setStyleSheet('color: black; font-size: 18pt; '
        #                                        'font-family: Courier;')
        # self.frame_number = QtWidgets.QLabel(str(self.frame_displayed_index + 1) + "/" + str(len(self.frames)))
        # self.frame_number.setStyleSheet('color: solid purple;'
        #                                  'font-weight: bold; font-size: 18pt; '
        #                                  'font-family: Courier;  border-style : outset;'
        #                                  'border-width 2px; border-radius: 10px; border-color: beige;'
        #                                  'min-width: 10em; padding: 6px')
        # text_layout.addWidget(user_initial_explanation)
        # text_layout.addWidget(self.frame_number)

        self._main_layout.setContentsMargins(0,0,0,0)

        # self._main_layout.addStretch()
        # self._main_layout.addLayout(text_layout)
        # self._main_layout.addStretch()

        # Label with ImageDisplay
        self._image_label = ImageLabel(self.frames, self)

        self._main_layout.addWidget(self._image_label)

        self._main_layout.addStretch()

        # bottom layout with 'segment' button
        # bottom_layout = QtWidgets.QHBoxLayout()
        # self._segment_button = QtWidgets.QPushButton('Perform Segmentation')
        # self._segment_button.setIcon(QtGui.QIcon('images/buttons_PNG103.png'))
        # self._segment_button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        # self._segment_button.resize(200, 20)
        # self._segment_button.clicked.connect(self._perform_segmentation_wrapper)
        # button_style_sheet = 'background-color:#88abdb; color: black; font-weight: regular; font-size: 12pt;' \
        #                      'border-radius: 15px; border-color: black; border-width: 3px; ' \
        #                      'border-style: outset;'
        # self._segment_button.setStyleSheet(button_style_sheet)
        #
        # self.tool_kit = ToolKit()
        # self.tool_kit.tool_chosen.connect(self._image_label.update_tool_in_use)
        #
        # bottom_layout.addStretch()
        # bottom_layout.addLayout(self.tool_kit)
        # bottom_layout.addStretch()
        # bottom_layout.addWidget(self._segment_button)
        # bottom_layout.addStretch()

        # self._main_layout.addLayout(bottom_layout)
        self.setLayout(self._main_layout)

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


class ToolKit(QtWidgets.QHBoxLayout):

    # signal that a new tool was chosen
    tool_chosen = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):

        QtWidgets.QHBoxLayout.__init__(self, parent)
        try:

            paintbrush_button = QtWidgets.QPushButton()
            paintbrush_button.setIcon(QtGui.QIcon('images/paintbrush.png'))
            paintbrush_button.clicked.connect(lambda: self.tool_chosen.emit(USE_PAINTBRUSH))
            self.addWidget(paintbrush_button)

            square_button = QtWidgets.QPushButton()
            square_button.setIcon(QtGui.QIcon('images/square.png'))
            square_button.clicked.connect(lambda: self.tool_chosen.emit(USE_SQUARE))
            self.addWidget(square_button)

            eraser_button = QtWidgets.QPushButton()
            eraser_button.setIcon(QtGui.QIcon('images/eraser.jpg'))
            eraser_button.clicked.connect(lambda: self.tool_chosen.emit(USE_ERASER))
            self.addWidget(eraser_button)

        except Exception as ex:
            print(ex)
