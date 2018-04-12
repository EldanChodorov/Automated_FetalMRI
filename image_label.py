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
from consts import *


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
        QtWidgets.QLabel.__init__(self)

        # Workspace holding this ImageLabel instance
        self._parent = workspace_parent

        # Shapes holds all geometric points marked on screen by user
        self.shapes = Shapes()

        # size of brushes
        self.paintbrush_size = BRUSH_WIDTH_MEDIUM
        self.eraser_size = BRUSH_WIDTH_MEDIUM

        # numpy array, list of images
        self.standard_frames = frames
        self.contrasted_frames = contrasted_frames

        self._original_cursor = self.cursor()

        # contains the set of images which will be displayed
        self.frames = self.standard_frames

        # index of current frame displayed
        self.frame_displayed_index = 0

        # if using square tool, store here first corner clicked with mouse
        self._square_corner = None

        self._zoom = INITIAL_ZOOM

        # store image size, changed upon zoom
        self._image_size = self._initial_image_size()

        # alpha channel of painter
        self.alpha_channel = 255

        # set view size
        self.setContentsMargins(0, 0, 0, 0)
        self.setAlignment(QtCore.Qt.AlignCenter)
        # self.setFixedSize(1000, 1000)
        # self.setMinimumSize(1000, 1000)
        self.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)

        # decide what to do with point clicks (paint/square/erase)
        self._tool_chosen = USE_PAINTBRUSH

        # whether to paint segmentation over scan or not
        self.show_segmentation = True

    def activate_image(self):
        '''Set image to be displayed. Deactivated until image should be shown.'''
        self.set_image(self.frames[self.frame_displayed_index])

        # connect signal to be used only when image is displayed
        self._parent.tool_chosen.connect(self._update_tool_in_use)

        # set frame number shown
        self.change_frame_number(1)

    @QtCore.pyqtSlot(bool)
    def change_view(self, contrast_view):
        '''
        Set whether frames shown are regular or contrasted.
        :param contrast_view: [bool] if True, show contrasted frames.
        '''
        try:
            if contrast_view:
                self.frames = self.contrasted_frames
            else:
                self.frames = self.standard_frames

            self.set_image(self.frames[self.frame_displayed_index])
        except Exception as ex:
            print(ex)

    @QtCore.pyqtSlot(int)
    def _update_tool_in_use(self, tool_chosen):
        try:
            self._tool_chosen = tool_chosen
            if self._tool_chosen == USE_ERASER:
                self._update_eraser_icon()
            else:
                self.setCursor(self._original_cursor)
        except Exception as ex:
            print(ex)

    def _update_eraser_icon(self):
        # display eraser icon in place of mouse cursor
        cursor = QtGui.QPixmap('images/erase_icon.png')
        if self.eraser_size == BRUSH_WIDTH_SMALL:
            cursor = cursor.scaled(5, 5, QtCore.Qt.KeepAspectRatio)
        elif self.eraser_size == BRUSH_WIDTH_LARGE:
            cursor = cursor.scaled(15, 15, QtCore.Qt.KeepAspectRatio)
        self.setCursor(QtGui.QCursor(cursor))

    def sizeHint(self):
        # this will be the initial label size
        return QtCore.QSize(785, 785)

    def mouseMoveEvent(self, QMouseEvent):
        pos = self.widget2image_coord(QMouseEvent.pos())
        if self._tool_chosen == USE_PAINTBRUSH:
            self.shapes.add_point(self.frame_displayed_index, pos)
        elif self._tool_chosen == USE_ERASER:
            self.shapes.remove_points(pos, self.frame_displayed_index)

        # update so that paintEvent will be called
        self.update()

    def mousePressEvent(self, QMouseEvent):
        if self._tool_chosen in [OUTER_SQUARE, INNER_SQUARE]:
            self._square_corner = self.widget2image_coord(QMouseEvent.pos())

    def widget2image_coord(self, pos):
        img_pos = pos
        scroll_height = self._parent.scroll_area.verticalScrollBar().value()
        scroll_width = self._parent.scroll_area.horizontalScrollBar().value()
        moved_pos = img_pos #- QtCore.QPoint(scroll_width, scroll_height)
        return moved_pos / self._zoom

    def image2widget_coord(self, pos):
        widget_pos = pos
        scroll_height = self._parent.scroll_area.verticalScrollBar().value()
        scroll_width = self._parent.scroll_area.horizontalScrollBar().value()
        moved_pos = widget_pos #+ QtCore.QPoint(scroll_width, scroll_height)
        return moved_pos * self._zoom

    def mouseReleaseEvent(self, cursor_event):
        if self._tool_chosen in [OUTER_SQUARE, INNER_SQUARE] and self._square_corner:
            # using square tool
            pos = self.widget2image_coord(cursor_event.pos())
            self.shapes.add_square(self.frame_displayed_index, self._square_corner, pos, self._tool_chosen)
            self._square_corner = None
            self.update()
        else:
            # using eraser or paintbrush tool
            self.mouseMoveEvent(cursor_event)
            # update() is called in mouseMoveEvent

    def _image_to_QPoint(self, image):
        '''
        Translate binary image to list of white points.
        :param image: [numpy.ndarray] binary image, shape (num_images, row, col)
        :return: [default dict of lists of QPoints] translated 1 pixels from image
        '''
        indices = np.where((image == 1) | (image == 255))  # todo stick to one
        transformed_x = (indices[2] / image.shape[2]) * self.width()
        transformed_y = (indices[1] / image.shape[1]) * self.height()

        points = defaultdict(list)
        for frame, x, y in zip(indices[0], transformed_x, transformed_y):
            points[frame].append(QtCore.QPoint(x, y))
        return points

    def label_to_image_pos(self, label_pos):
        # image is of size 512x512 pixels
        label_x, label_y = float(label_pos.x()), float(label_pos.y())
        image_x = (label_x / self.width()) * 512
        image_y = (label_y / self.height()) * 512
        return QtCore.QPoint(image_x, image_y)

    def points_to_image(self):
        '''
        Convert all points in Shapes object to a binary 3d image.
        :return: [numpy.ndarray] size of frames
        '''
        try:
            all_points = self.shapes.all_points()
            image = np.zeros(self.frames.shape)
            for frame, points_list in all_points.items():
                for point in points_list:
                    point /= self._zoom
                    label_x, label_y = float(point.x()), float(point.y())
                    image_x = (label_x / self.width()) * 512
                    image_y = (label_y / self.height()) * 512  # TODO: make modular, might not be 512 (in all code)
                    image[frame, image_x, image_y] = 1
            return image
        except Exception as ex:
            print(ex)

    def set_segmentation(self, segmentation_array):
        '''
        Draw transparent points of segmentation on top of image.
        :param segmentation_array: [numpy.ndarray] binary image
        '''
        marked_points = self._image_to_QPoint(segmentation_array)
        for frame_num, points_list in marked_points.items():
            self.shapes.add_points(frame_num, points_list, self._zoom)

        # draw points transparently
        self.alpha_channel = ALPHA_TRANSPARENT

    def paintEvent(self, paint_event):
        try:
            painter = QtGui.QPainter(self)

            # draw image first so that points will be on top of image
            painter.drawPixmap(self.rect(), self._displayed_pixmap)

            # draw segmentation and markings only if 'show segmentation' is defined
            if self.show_segmentation:

                pen = QtGui.QPen()
                pen.setWidth(self.paintbrush_size)

                # inner squares
                pen.setColor(QtGui.QColor(138, 43, 226, self.alpha_channel))
                painter.setPen(pen)
                for square in self.shapes.inner_squares[self.frame_displayed_index]:
                    for point in square.points:
                        painter.drawPoint(self.image2widget_coord(point))

                # outer squares
                pen.setColor(QtGui.QColor(255, 0, 0, self.alpha_channel))
                painter.setPen(pen)
                for square in self.shapes.outer_squares[self.frame_displayed_index]:
                    for point in square.points:
                        painter.drawPoint(self.image2widget_coord(point))

                # points
                pen.setColor(QtGui.QColor(0, 0, 255, self.alpha_channel))
                painter.setPen(pen)
                for point in self.shapes.chosen_points[self.frame_displayed_index]:
                    painter.drawPoint(self.image2widget_coord(point))

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
        if zoom_factor > 0:
            # zoom in
            if self._zoom >= 5.0:
                return
            factor = 1.05
        else:
            # zoom out
            if self._zoom < 0.1:
                return
            factor = 0.952381

        self._zoom *= factor
        self.resize(self._zoom * self.sizeHint())
        self._adjust_scroll_bar(self._parent.scroll_area.horizontalScrollBar(), factor)
        self._adjust_scroll_bar(self._parent.scroll_area.verticalScrollBar(), factor)

    @staticmethod
    def _adjust_scroll_bar(scroll_bar, factor):
        # TODO setMax & setPageStep should be set upon intialization
        scroll_bar.setMaximum(int(512 * 1.5))
        scroll_bar.setPageStep(4)
        new_value = factor * scroll_bar.value() + (factor - 1) * scroll_bar.pageStep()
        scroll_bar.setValue(int(new_value))

    def change_frame_number(self, frame_number):
        if 0 < frame_number <= len(self.frames):
            self.frame_displayed_index = frame_number - 1
            self.set_image(self.frames[self.frame_displayed_index])
            self._parent.frame_number.setText(str(self.frame_displayed_index + 1) + "/" + str(len(self.frames)))

    def wheelEvent(self, event):
        '''Change frames when user uses wheel scroll, or zoom in if CTRL is pressed.'''

        # zoom in\out of images
        if QtWidgets.QApplication.keyboardModifiers() == QtCore.Qt.ControlModifier:
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
