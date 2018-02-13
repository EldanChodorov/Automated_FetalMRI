
from collections import defaultdict
import numpy as np
from threading import Thread
from PyQt5 import QtGui, QtCore, QtWidgets
import qimage2ndarray
from skimage import color
import cv2
import segment3d_itk
import nibabel as nib


USE_PAINTBRUSH = 1
USE_OUTER_SQUARE = 2
USE_INNER_SQUARE = 3
USE_ERASER = 4
ERASER_WIDTH = 5
MIN_ZOOM = 0


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


class ImageLabel(QtWidgets.QGraphicsView):

    # emits (frame idx, pos) of point chosen from images
    point_chosen = QtCore.pyqtSignal(tuple)

    def __init__(self, frames, workspace_parent):
        '''
        :param frames: [numpy.ndarray] list of images
        :param workspace_parent: [WorkSpace]
        '''
        QtWidgets.QGraphicsView.__init__(self, workspace_parent)

        # Workspace holding this ImageLabel instance
        self._parent = workspace_parent

        # numpy array, list of images
        self.frames = frames

        # index of current frame displayed
        self.frame_displayed_index = 0

        # dict of frame#: points chosen manually by user per each frame
        self.chosen_points = defaultdict(list)

        # if using square tool, store here first corner clicked with mouse
        self._square_corner = None

        self._zoom = MIN_ZOOM

        # set view size
        self.setContentsMargins(0, 0, 0, 0)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setFixedSize(1000, 1000)
        self.setMinimumSize(1000, 1000)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        # set up image
        self._scene = QtWidgets.QGraphicsScene(self)
        self.set_image(self.frames[self.frame_displayed_index])

        # decide what to do with point clicks (paint/square/erase)
        self._tool_chosen = USE_PAINTBRUSH
        self._parent.tool_chosen.connect(self._update_tool_in_use)

    @QtCore.pyqtSlot(int)
    def _update_tool_in_use(self, tool_chosen):
        self._tool_chosen = tool_chosen

    def sizeHint(self):
        # TODO: set label minimum size
        return QtCore.QSize(1000, 1000)

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
                    pos.setY(orig_y+j)
                    if pos in self.chosen_points[self.frame_displayed_index]:
                        self.chosen_points[self.frame_displayed_index].remove(pos)

        # update so that paintEvent will be called
        self.update()

    def fitInView(self):
        rect = QtCore.QRectF(self._displayed_pixmap.rect())
        if not rect.isNull():
            unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
            self.scale(1 / unity.width(), 1 / unity.height())
            viewrect = self.viewport().rect()
            scenerect = self.transform().mapRect(rect)
            factor = min(viewrect.width() / scenerect.width(),
                         viewrect.height() / scenerect.height())
            self.scale(factor, factor)
            self.centerOn(rect.center())
            self._zoom = 0

    def mousePressEvent(self, QMouseEvent):
        if self._tool_chosen in [USE_OUTER_SQUARE, USE_INNER_SQUARE]:
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
        if self._tool_chosen in [USE_OUTER_SQUARE, USE_INNER_SQUARE] and self._square_corner:
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
        try:
            QtWidgets.QGraphicsView.paintEvent(self, paint_event)

            painter = QtGui.QPainter(self)

            # draw image first so that points will be on top of image
            painter.drawPixmap(self.rect(), self._displayed_pixmap)
            # self._photo.setPixmap(self._displayed_pixmap)

            pen = QtGui.QPen()
            pen.setWidth(5)
            pen.setColor(QtGui.QColor('blue'))
            painter.setPen(pen)
            painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
            for pos in self.chosen_points[self.frame_displayed_index]:
                painter.drawPoint(pos)
                self._scene.addEllipse(pos.x(), pos.y(), 5, 5, pen, QtGui.QBrush())
            self._scene.render(painter)
            self.setScene(self._scene)

        except Exception as ex:
            print('paintEvent', ex)

    def set_image(self, img_numpy_array):
        try:
            image = qimage2ndarray.array2qimage(img_numpy_array)
            if image.isNull():
                image = QtGui.QImage('images\\unavailable.jpg')
            qimg = QtGui.QPixmap.fromImage(image)
            qimg = qimg.scaled(self.sceneRect().width(), self.sceneRect().height(), QtCore.Qt.KeepAspectRatio)
            self._displayed_pixmap = QtGui.QPixmap(qimg)
            # self._photo.setPixmap(self._displayed_pixmap)

            # scale image to fit label
            self._displayed_pixmap.scaled(self.width(), self.height(), QtCore.Qt.KeepAspectRatio)
            self.setAlignment(QtCore.Qt.AlignCenter)
            # self.setScaledContents(True)
            self.setMinimumSize(512, 512)

            # self._scene.clear()
            pixmap = self._scene.addPixmap(self._displayed_pixmap)
            print(pixmap)
            # self.fitInView(pixmap)
            self.setScene(self._scene)

            # self.show()
        except Exception as ex:
            print('set image', ex)

    def wheelEvent(self, event):
        '''Change frames when user uses wheel scroll, or zoom in if CTRL is pressed.'''
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ControlModifier:
            print('zoom:  %.4f' % self._zoom)
            self._zoom = self._zoom + event.angleDelta().y() / 1200.0
            if self._zoom < MIN_ZOOM:
                self._zoom = MIN_ZOOM
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

