from collections import defaultdict
import numpy as np
from threading import Thread
from PyQt5 import QtGui, QtCore, QtWidgets
import qimage2ndarray
from skimage import color
import cv2
import segment3d_itk
import nibabel as nib
from Shapes import Shapes
from consts import OUTER_SQUARE, INNER_SQUARE, USE_ERASER, USE_PAINTBRUSH, MIN_ZOOM


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

    def __init__(self, frames, contrasted_frames, workspace_parent):
        '''
        :param frames: [numpy.ndarray] list of images
        :param contrasted_frames: [numpy.ndarray] list of images, after histogram equalization
        :param workspace_parent: [WorkSpace]
        '''
        QtWidgets.QLabel.__init__(self, workspace_parent)

        # Workspace holding this ImageLabel instance
        self._parent = workspace_parent

        # Shapes holds all geometric points marked on screen by user
        self._shapes = Shapes()

        # numpy array, list of images
        self.standard_frames = frames
        self.contrasted_frames = contrasted_frames

        # contains the set of images which will be displayed
        self.frames = self.standard_frames

        # index of current frame displayed
        self.frame_displayed_index = 0

        # if using square tool, store here first corner clicked with mouse
        self._square_corner = None

        self._zoom = MIN_ZOOM

        # store image size, changed upon zoom
        self._image_size = self._initial_image_size()

        # set view size
        self.setContentsMargins(0, 0, 0, 0)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setFixedSize(1000, 1000)
        self.setMinimumSize(1000, 1000)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.set_image(self.frames[self.frame_displayed_index])

        # decide what to do with point clicks (paint/square/erase)
        self._tool_chosen = USE_PAINTBRUSH
        self._parent.tool_chosen.connect(self._update_tool_in_use)

    @QtCore.pyqtSlot(bool)
    def change_view(self, contrast_view):
        '''
        Set whether frames shown are regular or contrasted.
        :param contrast_view: [bool] if True, show contrasted frames.
        '''
        if contrast_view:
            self.frames = self.contrasted_frames
        else:
            self.frames = self.standard_frames

        self.set_image(self.frames[self.frame_displayed_index])

    @QtCore.pyqtSlot(int)
    def _update_tool_in_use(self, tool_chosen):
        self._tool_chosen = tool_chosen

    def sizeHint(self):
        # TODO: set label minimum size
        return QtCore.QSize(1000, 1000)

    def mouseMoveEvent(self, QMouseEvent):
        pos = QMouseEvent.pos()
        if self._tool_chosen == USE_PAINTBRUSH:
            self._shapes.add_point(self.frame_displayed_index, pos)
        elif self._tool_chosen == USE_ERASER:
            self._shapes.remove_points(pos, self.frame_displayed_index)

        # update so that paintEvent will be called
        self.update()

    def mousePressEvent(self, QMouseEvent):
        if self._tool_chosen in [OUTER_SQUARE, INNER_SQUARE]:
            self._square_corner = QMouseEvent.pos()

    def mouseReleaseEvent(self, cursor_event):
        print(self._tool_chosen, OUTER_SQUARE, INNER_SQUARE)
        if self._tool_chosen in [OUTER_SQUARE, INNER_SQUARE] and self._square_corner:
            print('square')
            # using square tool
            self._shapes.add_square(self.frame_displayed_index, self._square_corner, cursor_event.pos(), self._tool_chosen)
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
        try:
            painter = QtGui.QPainter(self)

            # draw image first so that points will be on top of image
            painter.drawPixmap(self.rect(), self._displayed_pixmap)

            pen = QtGui.QPen()
            pen.setWidth(5)

            # inner squares
            pen.setColor(QtGui.QColor('purple'))
            painter.setPen(pen)
            for square in self._shapes.inner_squares[self.frame_displayed_index]:
                for point in square.points:
                    painter.drawPoint(point)

            # outer squares
            pen.setColor(QtGui.QColor('red'))
            painter.setPen(pen)
            for square in self._shapes.outer_squares[self.frame_displayed_index]:
                for point in square.points:
                    painter.drawPoint(point)

            # points
            pen.setColor(QtGui.QColor('blue'))
            painter.setPen(pen)
            for point in self._shapes.chosen_points[self.frame_displayed_index]:
                painter.drawPoint(point)

            # call update / setPalette(painter)
        except Exception as ex:
            print('paintEvent', ex)

    def _initial_image_size(self):
        ''':return Original size of images.'''
        image = qimage2ndarray.array2qimage(self.frames[0])
        if image.isNull():
            image = QtGui.QImage('images\\unavailable.jpg')
        qimg = QtGui.QPixmap.fromImage(image)
        return QtGui.QPixmap(qimg).size()

    def set_image(self, img_numpy_array):

        image = qimage2ndarray.array2qimage(img_numpy_array)
        if image.isNull():
            image = QtGui.QImage('images\\unavailable.jpg')
        image = image.scaled(self._image_size)
        qimg = QtGui.QPixmap.fromImage(image)
        self._displayed_pixmap = QtGui.QPixmap(qimg)
        # scale image to fit label
        self._displayed_pixmap.scaled(image.width(), image.height(), QtCore.Qt.KeepAspectRatio)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setScaledContents(True)
        self.setMinimumSize(512, 512)
        self.show()
        self.update()

    def _zoom_image(self, zoom_factor):
        try:
            self._zoom = self._zoom + zoom_factor / 1200.0
            if self._zoom < MIN_ZOOM:
                self._zoom = MIN_ZOOM

            image_size = self._displayed_pixmap.size()
            image_size.setWidth(image_size.width() * 0.9)
            image_size.setHeight(image_size.height() * 0.9)
            self._image_size = image_size
            self._displayed_pixmap = self._displayed_pixmap.scaled(image_size, QtCore.Qt.KeepAspectRatio)
            print(self._displayed_pixmap.size(), self._zoom)
        except Exception as ex:
            print(ex)

    def wheelEvent(self, event):
        '''Change frames when user uses wheel scroll, or zoom in if CTRL is pressed.'''
        modifiers = QtWidgets.QApplication.keyboardModifiers()

        # zoom in\out of images
        if modifiers == QtCore.Qt.ControlModifier:
            self._zoom_image(event.angleDelta().y())

        # scroll through images
        else:
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

