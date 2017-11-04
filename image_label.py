from collections import defaultdict
import numpy as np
from threading import Thread
from PyQt5 import QtWidgets
from PyQt5 import QtGui, QtCore
import qimage2ndarray
import segment3d_itk


class ImageLabel(QtWidgets.QLabel):

    # emits (frame idx, pos) of point chosen from images
    point_chosen = QtCore.pyqtSignal(tuple)

    def __init__(self, frames, image_display_parent):
        '''
        :param frames: [numpy.ndarray] list of images
        :param image_display: [ImageDisplay]
        '''
        QtWidgets.QLabel.__init__(self)

        # ImageDisplay holding this ImageLabel instance
        self._parent = image_display_parent

        # numpy array, list of images
        self.frames = frames

        # index of current frame displayed
        self.frame_displayed_index = 0

        # dict of frame#: points chosen manually by user per each frame
        self.chosen_points = defaultdict(list)

        self._zoom = 1.0

        self.setContentsMargins(0, 0, 0, 0)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setFixedSize(1000,1000)
        self.set_image(self.frames[self.frame_displayed_index])

        # numpy array of binary frames containing segmentation
        self.segmented_frames = None

    def sizeHint(self):
        # TODO: set label minimum size
        return QtCore.QSize(512, 512)

    def mouseReleaseEvent(self, cursor_event):
        pos = cursor_event.pos()
        self.chosen_points[self.frame_displayed_index].append(pos)

        # signal to parent so that will add button of point chosen
        self.point_chosen.emit((self.frame_displayed_index, pos))

        # update so that paintEvent will be called
        self.update()

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

        # if exists, draw segmentation frame over image
        if self.segmented_frames:
            segmented_img = self.set_image(self.segmented_frames, True)
            painter.drawPixmap(self.rect(), segmented_img)

        pen = QtGui.QPen()
        pen.setWidth(10)
        pen.setColor(QtGui.QColor('blue'))
        painter.setPen(pen)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        for pos in self.chosen_points[self.frame_displayed_index]:
            painter.drawPoint(pos)

    def set_image(self, img_numpy_array, get_image_only=False):
        image = qimage2ndarray.array2qimage(img_numpy_array)
        if image.isNull():
            image = QtGui.QImage('images\\unavailable.jpg')
        if get_image_only:
            return image
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

    def __init__(self, frames, nifti_obj):
        '''
        :param frames: array data of shape (num_images, x, y) 
        :param nifti_obj: [Nifti]
        '''
        QtWidgets.QWidget.__init__(self)

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
        text_layout = QtWidgets.QHBoxLayout()
        user_initial_explanation = QtWidgets.QLabel(
            'Scroll through frames, and mark four corners of the brain.')
        user_initial_explanation.setStyleSheet('color: black; font-size: 18pt; '
                                               'font-family: Courier;')
        self.frame_number = QtWidgets.QLabel(str(self.frame_displayed_index + 1) + "/" + str(len(self.frames)))
        self.frame_number.setStyleSheet('color: solid purple;'
                                         'font-weight: bold; font-size: 18pt; '
                                         'font-family: Courier;  border-style : outset;'
                                         'border-width 2px; border-radius: 10px; border-color: beige;'
                                         'min-width: 10em; padding: 6px')
        text_layout.addWidget(user_initial_explanation)
        text_layout.addWidget(self.frame_number)

        self._main_layout.setContentsMargins(0,0,0,0)

        self._main_layout.addStretch()
        self._main_layout.addLayout(text_layout)
        self._main_layout.addStretch()

        # Label with ImageDisplay
        self._image_label = ImageLabel(self.frames, self)

        self._main_layout.addWidget(self._image_label)

        self._main_layout.addStretch()

        # bottom layout with 'segment' button
        bottom_layout = QtWidgets.QHBoxLayout()
        self._segment_button = QtWidgets.QPushButton('Perform Segmentation')
        self._segment_button.setIcon(QtGui.QIcon('images/buttons_PNG103.png'))
        self._segment_button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self._segment_button.resize(200, 20)
        self._segment_button.clicked.connect(self._perform_segmentation_wrapper)
        button_style_sheet = 'background-color:#88abdb; color: black; font-weight: regular; font-size: 12pt;' \
                             'border-radius: 15px; border-color: black; border-width: 3px; ' \
                             'border-style: outset;'
        self._segment_button.setStyleSheet(button_style_sheet)

        chosen_points_label = ChosenPointsLabel()
        self._image_label.point_chosen.connect(lambda t: chosen_points_label.add_point(t[0], t[1]))

        bottom_layout.addStretch()
        bottom_layout.addWidget(chosen_points_label)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self._segment_button)
        bottom_layout.addStretch()

        self._main_layout.addLayout(bottom_layout)
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
            self._segmentation_array = segment3d_itk.segmentation_3d(self.frames, seeds) * 255
            self._image_label.segmented_frames = self._segmentation_array

            self._remove_progress_bar()

            if self._segmentation_array is None:
                self._segment_button.setEnabled(True)
                return

            # set images to image label
            self._image_label.frames = self._segmentation_array
            self._image_label.frame_displayed_index = 0
            self._image_label.set_image(self._segmentation_array[0])
            self._image_label.update()
        except Exception as ex:
            print(ex, type(ex))


class ChosenPointsLabel(QtWidgets.QLabel):

    def __init__(self):
        QtWidgets.QLabel.__init__(self)

        # dict with key=(frame, x, y), value=(button layout)
        self._button_layouts = {}

        self._layout = QtWidgets.QHBoxLayout()
        # self._scroll_area = QtWidgets.QScrollArea()
        # self._scroll_layout = QtWidgets.QHBoxLayout()
        # self._scroll_area.setLayout(self._scroll_layout)
        self.setLayout(self._layout)

    @QtCore.pyqtSlot()
    def add_point(self, frame, pos):
        ''' Add button to label representing a point at QPos, from frame index.'''
        # TODO: points are not being added, fix.
        try:
            # point was already added
            if (frame, pos.y(), pos.x()) in self._button_layouts:
                return
            new_label = QtWidgets.QLabel('Frame #{}\n({},{})'.format(frame, pos.y(), pos.x()))
            remove_button = QtWidgets.QPushButton('Remove Point')
            new_layout = QtWidgets.QVBoxLayout()
            new_layout.addWidget(new_label)
            new_layout.addWidget(remove_button)
            self._layout.addLayout(new_layout)
            self._button_layouts[(frame, pos.y(), pos.x())] = new_layout
            self.update()
        except Exception as ex:
            print(ex, type(ex))
