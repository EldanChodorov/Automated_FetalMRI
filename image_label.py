
"""
ImageLabel class holds the image currently displayed.
This class is used as singleton by ScanFile.
Holds all the different frames of a scan, both regular and contrasted.
"""

import math
import numpy as np
import qimage2ndarray
from collections import defaultdict
from PyQt5 import QtGui, QtCore, QtWidgets
from Shapes import Shapes
from consts import *


class ImageLabel(QtWidgets.QLabel):

    def __init__(self, frames, contrasted_frames, workspace_parent):
        '''
        :param frames: [numpy.ndarray] list of images
        :param contrasted_frames: different levels of contrast performed on frames, shape (10, frames.shape)
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

        # numpy array, shape (10, standard_frames.shape)
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

        # set view size
        self.setContentsMargins(0, 0, 0, 0)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)

        # decide what to do with point clicks (paint/square/erase)
        self._tool_chosen = USE_PAINTBRUSH

        # whether to paint markings and segmentation over image or not
        self.paint_over = True

        # whether to show scan at all or not (independent of segmentation showing)
        self.show_scan = True

        # whether segmentation has been added to the image yet
        self._segmentation_added = False

        # points chosen as vertices for a polygon, by user with paintbrush
        # contains frame_num: list of vertices
        self._polygon_vertices = defaultdict(list)

    def activate_image(self):
        '''Set image to be displayed. Deactivated until image should be shown.'''
        self.set_image(self.frames[self.frame_displayed_index])

        # connect signal to be used only when image is displayed
        self._parent.tool_chosen.connect(self._update_tool_in_use)

        # set frame number shown
        self.change_frame_number(1)

    @QtCore.pyqtSlot(int)
    def change_view(self, contrast_index=-1):
        '''
        Set whether frames shown are regular or contrasted.
        :param contrast_index: [int] contrast level to show. if -1, show regular frames.
        '''
        if contrast_index == -1:
            self.frames = self.standard_frames
        else:
            self.frames = self.contrasted_frames[contrast_index]

        self.set_image(self.frames[self.frame_displayed_index])

    @QtCore.pyqtSlot(int)
    def _update_tool_in_use(self, tool_chosen):
        self._tool_chosen = tool_chosen
        if self._tool_chosen == USE_ERASER:
            self._update_eraser_icon()
        else:
            self.setCursor(self._original_cursor)

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
        return pos / self._zoom

    def image2widget_coord(self, pos):
        return pos * self._zoom

    def mouseReleaseEvent(self, cursor_event):

        pos = self.widget2image_coord(cursor_event.pos())
        if self._tool_chosen in [OUTER_SQUARE, INNER_SQUARE] and self._square_corner:
            self.shapes.add_square(self.frame_displayed_index, self._square_corner, pos, self._tool_chosen)
            self._square_corner = None
            self.update()
        elif self._tool_chosen == POLYGON:
            self._polygon_vertices[self.frame_displayed_index].append(pos)
            self.update()
        else:
            # using eraser or paintbrush tool
            self.mouseMoveEvent(cursor_event)
            # update() is called in mouseMoveEvent

    def submit_polygon(self):
        if self._tool_chosen == POLYGON:
            self.shapes.add_polygon(self.frame_displayed_index, self._polygon_vertices[self.frame_displayed_index])
            self._polygon_vertices[self.frame_displayed_index] = []
            self.update()

    def _image_to_QPoint(self, image):
        '''
        Translate binary image to list of white points.
        :param image: [numpy.ndarray] binary image, shape (num_images, row, col)
        :return: [default dict of lists of QPoints] translated 1 pixels from image
        '''
        # width, height = self.width(), self.height()
        width, height = self.sizeHint().width(), self.sizeHint().height()

        indices = np.where((image == 1) | (image == 255))  # todo stick to one
        transformed_x = (indices[2] / image.shape[2]) * width
        transformed_y = (indices[1] / image.shape[1]) * height
        points = defaultdict(list)
        for frame, x, y in zip(indices[0], transformed_x, transformed_y):
            points[frame].append(QtCore.QPoint(x, y))
        return points

    def label_to_image_pos(self, label_pos):
        # image is of size 512x512 pixels
        label_x, label_y = float(label_pos.x()), float(label_pos.y())

        # width, height = self.width(), self.height()
        width, height = self.sizeHint().width(), self.sizeHint().height()

        image_x = (label_x / width) * 512
        image_y = (label_y / height) * 512
        return QtCore.QPoint(image_x, image_y)

    def points_to_image(self, brain_halves=False):
        '''
        Convert all points in Shapes object to a binary 3d image.
        :param brain_halves: [bool] extract only points from brain_halves if True
        :return: [numpy.ndarray] size of frames
        '''
        # width, height = self.width(), self.height()
        width, height = self.sizeHint().width(), self.sizeHint().height()

        def p2i_helper(all_points):
            image = np.zeros(self.frames.shape)
            for frame, points_list in all_points.items():
                for point in points_list:
                    label_x, label_y = float(point.x()), float(point.y())
                    # TODO: make modular, might not be 512 (in all code)
                    image_x = math.ceil((label_x / width) * 512)
                    image_y = math.ceil((label_y / height) * 512)
                    image[frame, image_y, image_x] = 1
            return image

        if not brain_halves:
            return p2i_helper(self.shapes.all_points())
        else:
            half1, half2 = self.shapes.brain_halves()
            return p2i_helper(half1), p2i_helper(half2)

    def set_brain_halves(self, half1, half2):
        self.shapes.clear_points()
        points_half1 = self._image_to_QPoint(half1)
        points_half2 = self._image_to_QPoint(half2)
        self.shapes.set_brain_halves(points_half1, points_half2)
        self.update()

    def set_segmentation(self, segmentation_array):
        '''
        Draw transparent points of segmentation on top of image.
        :param segmentation_array: [numpy.ndarray] binary image
        '''
        self.shapes.clear_points()
        marked_points = self._image_to_QPoint(segmentation_array)
        for frame_num, points_list in marked_points.items():
            self.shapes.add_points(frame_num, points_list, True)
        self._segmentation_added = True
        self.update()

    def paintEvent(self, paint_event):

        painter = QtGui.QPainter(self)

        # draw image first so that points will be on top of image
        if self.show_scan:
            painter.drawPixmap(self.rect(), self._displayed_pixmap)
        else:
            # black background
            painter.fillRect(self.rect(), QtGui.QColor(0, 0, 0))

        if not self.paint_over:
            return

        pen = QtGui.QPen()
        pen.setWidth(self.paintbrush_size)

        # on zoom, draw in between points, to fill in gaps
        offset = int(np.ceil((self._zoom * 2) - 2))

        try:

            # brain halves
            if self.shapes.brain_halves_set:
                first_half, second_half = self.shapes.brain_halves()

                # first half
                pen.setColor(QtGui.QColor(138, 43, 226, ALPHA_TRANSPARENT))
                painter.setPen(pen)
                self._paint_points(first_half[self.frame_displayed_index], painter, offset)

                # second half
                pen.setColor(QtGui.QColor(50, 205, 50, ALPHA_TRANSPARENT))
                painter.setPen(pen)
                self._paint_points(second_half[self.frame_displayed_index], painter, offset)

                # don't draw over brain halves
                return

            # inner squares
            pen.setColor(QtGui.QColor(138, 43, 226, ALPHA_NON_TRANSPARENT))
            painter.setPen(pen)
            for square in self.shapes.inner_squares[self.frame_displayed_index]:
                for point in square.points:
                    painter.drawPoint(self.image2widget_coord(point))

            # outer squares
            pen.setColor(QtGui.QColor(255, 0, 0, ALPHA_NON_TRANSPARENT))
            painter.setPen(pen)
            for square in self.shapes.outer_squares[self.frame_displayed_index]:
                for point in square.points:
                    painter.drawPoint(self.image2widget_coord(point))

            # points
            pen.setColor(QtGui.QColor(PAINT_COLOR[0], PAINT_COLOR[1], PAINT_COLOR[2], ALPHA_NON_TRANSPARENT))
            painter.setPen(pen)
            self._paint_points(self.shapes.chosen_points[self.frame_displayed_index], painter, offset)

            # segmentation points
            transparency = ALPHA_TRANSPARENT if self.show_scan else ALPHA_NON_TRANSPARENT
            pen.setColor(QtGui.QColor(PAINT_COLOR[0], PAINT_COLOR[1], PAINT_COLOR[2], transparency))
            painter.setPen(pen)
            self._paint_points(self.shapes.segmentation_points[self.frame_displayed_index], painter, offset)

            # polygon vertices
            if self._tool_chosen == POLYGON:
                pen.setColor(QtGui.QColor(30, 144, 255, ALPHA_NON_TRANSPARENT))
                painter.setPen(pen)
                for pos in self._polygon_vertices[self.frame_displayed_index]:
                    painter.drawPoint(self.image2widget_coord(pos))

        except Exception as ex:
            print('paintEvent', ex)

    def _paint_points(self, points, painter, offset):
        '''
        sub method from overridden paintEvent, paint given points.
        :param points: [list] of QtCore.QPoints
        :param painter: [QtGui.QPainter] with already set color & thickness
        :param offset: [int] how many extra points to draw per each given point
        '''
        for point in points:
            real_point = self.image2widget_coord(point)
            painter.drawPoint(real_point)
            # on zoom, draw in between points, to fill in gaps
            for i in range(offset):
                painter.drawPoint(real_point + QtCore.QPoint(i+1, i+1))

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
            if self._zoom < 0.9:
                return
            factor = 0.952381

        self._zoom *= factor
        self.resize(self._zoom * self.sizeHint())

        # adjust both scroll bars
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
