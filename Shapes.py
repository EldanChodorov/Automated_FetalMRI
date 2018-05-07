'''
Class to holds squares, points, etc. marked by user.
These polygons may have missing points, if erased by user.
'''

from collections import defaultdict
import pickle
import copy
from PyQt5 import QtCore, QtWidgets
from consts import OUTER_SQUARE, INNER_SQUARE, BRUSH_WIDTH_MEDIUM


class Shapes:

    def __init__(self):

        # dict of frame number: points chosen manually by user per each frame
        self.chosen_points = defaultdict(list)

        # dict of frame number: points included in segmentation
        self.segmentation_points = defaultdict(list)

        # save aside points marked by user, same type as chosen_points
        self._marked_points = None

        # dict of frame number: squares chosen manually by user per each frame
        # inner - contained in brain, outer - enclosing the brain
        self.inner_squares = defaultdict(list)
        self.outer_squares = defaultdict(list)

        # size of brushes
        self.eraser_width = BRUSH_WIDTH_MEDIUM

        # store brain halves separately
        self._brain_half1 = defaultdict(list)
        self._brain_half2 = defaultdict(list)
        self.brain_halves_set = False

    def __repr__(self):
        return str(self.chosen_points) + '\n' + str(self.inner_squares) + '\n' + str(self.outer_squares)

    def add_square(self, frame_number, corner1, corner2, square_type):
        '''
        Add points in square formed by given parameter.
        :param frame_number: [int] frame square was marked in.
        :param corner1: QtCore.QPoint
        :param corner2: QtCore.QPoint
        :param square_type: [int] type of square (inner/outer)
        '''
        if square_type == INNER_SQUARE:
            self.inner_squares[frame_number].append(Square(corner1, corner2))
        if square_type == OUTER_SQUARE:
            self.outer_squares[frame_number].append(Square(corner1, corner2))

    def clear_points(self):
        # clear all points, assume new segmentation was found and will be set
        self.chosen_points = defaultdict(list)
        self.segmentation_points = defaultdict(list)
        self._brain_half1 = defaultdict(list)
        self._brain_half2 = defaultdict(list)
        self.brain_halves_set = False

    def add_points(self, frame_number, points, segmentation=False):
        '''
        Add given points to list of points.
        :param frame_number: [int] frame points were selected from.
        :param points: [list of QtCore.QPoint]
        :param segmentation: [bool] If True, added points belong to segmentation and not user marks
        '''
        # use two different function for segmentation/regular points, for speed
        # faster than using one function + checking (if) on a boolean for every point in points
        if segmentation:
            for point in points:
                self.add_segmentation_point(frame_number, point)
        else:
            for point in points:
                self.add_point(frame_number, point)

    def add_segmentation_point(self, frame_number, point):
        '''
        Add given point to existing points container.
        :param frame_number: [int] frame points were selected from.
        :param point: [QtCore.QPoint]
        '''
        self.segmentation_points[frame_number].append(point)

    def store_marks(self):
        '''
        Save aside all points present, to be used later.
        '''
        self._marked_points = self.chosen_points
        self.chosen_points = defaultdict(list)

    def add_point(self, frame_number, point):
        '''
        Add given point to existing points container.
        :param frame_number: [int] frame points were selected from.
        :param point: [QtCore.QPoint]
        '''
        self.chosen_points[frame_number].append(point)

    def remove_points(self, pos, frame):
        '''
        Remove points in the vicinity of given position.
        :param pos: [QtCore.QPoint]
        :param frame: [int] remove points from this frame only
        '''
        orig_x = pos.x()
        orig_y = pos.y()
        for i in range(-self.eraser_width, self.eraser_width):
            for j in range(-self.eraser_width, self.eraser_width):
                pos.setX(orig_x + i)
                pos.setY(orig_y + j)

                # erase points
                if pos in self.chosen_points[frame]:
                    self.chosen_points[frame].remove(pos)

                # erase segmentation
                if pos in self.segmentation_points[frame]:
                    self.segmentation_points[frame].remove(pos)

                # erase squares
                squares = self.inner_squares[frame] + self.outer_squares[frame]
                for square in squares:
                    if pos in square.points:
                        square.points.remove(pos)

    def save(self, original_nifti_path):
        '''
        Open dialog for user to pick directory in which to Shapes objects (points marked).
        :param original_nifti_path: [str] path of nifti originally opened in workspace.
        '''
        try:
            file_dialog = QtWidgets.QFileDialog()
            file_dialog.setDefaultSuffix('.pickle')
            options = QtWidgets.QFileDialog.Options()
            options |= QtWidgets.QFileDialog.DontUseNativeDialog
            file_name, _ = QtWidgets.QFileDialog.getSaveFileName(file_dialog, "Save points PICKLE file", "",
                                        "Pickle Files (*.pickle)", options=options)
            if file_name:
                if not file_name.endswith('.pickle'):
                    file_name += '.pickle'
                try:
                    with open(file_name, 'wb') as f:
                        pickle.dump(self, f)
                    print('Points marked saved to %s' % file_name)
                except pickle.PickleError:
                    print('Error saving file.')
        except Exception as ex:
            print(ex)

    def set_brain_halves(self, half1, half2):
        self._brain_half1, self._brain_half2 = half1, half2
        self.brain_halves_set = True

    def brain_halves(self):
        ''':return: two dictionaries: default dicts of all points in each brain half.'''
        return self._brain_half1, self._brain_half2

    def all_points(self):
        ''':return: default dict of all points in shapes, without distinction to shape. '''
        all_points = defaultdict(list)
        for frame, points_list in self.chosen_points.items():
            all_points[frame] = copy.deepcopy(points_list)
            # add extra point to fill in gaps created
            all_points[frame] += [QtCore.QPoint(point.x()+1, point.y()+1) for point in points_list]
            all_points[frame] += [QtCore.QPoint(point.x()+1, point.y()-1) for point in points_list]
            all_points[frame] += [QtCore.QPoint(point.x()+1, point.y()) for point in points_list]
            all_points[frame] += [QtCore.QPoint(point.x(), point.y()+1) for point in points_list]
            all_points[frame] += [QtCore.QPoint(point.x(), point.y()-1) for point in points_list]
            all_points[frame] += [QtCore.QPoint(point.x(), point.y()) for point in points_list]
            all_points[frame] += [QtCore.QPoint(point.x()-1, point.y()-1) for point in points_list]
            all_points[frame] += [QtCore.QPoint(point.x()-1, point.y()+1) for point in points_list]
            all_points[frame] += [QtCore.QPoint(point.x()-1, point.y()) for point in points_list]
        for frame, squares_list in self.inner_squares.items():
            for square in squares_list:
                all_points[frame] += copy.deepcopy(square.points)
        for frame, squares_list in self.outer_squares.items():
            for square in squares_list:
                all_points[frame] += copy.deepcopy(square.points)
        for frame, seg_points_list in self.segmentation_points.items():
            all_points[frame] += seg_points_list
        return all_points


class Polygon:

    def __init__(self, vertices):

        # vertices defining the polygon boundary
        self._vertices = vertices

        # all points inside polygon
        self.points = []

    def __contains__(self, item):
        raise NotImplementedError

    def _set_all_points(self):

        # define bounding box of polygon

        # get all points inside the bounding box

        # check per point if it is inside the polygon

        pass


class Square:

    def __init__(self, corner1, corner2):

        # all points in boundary of square
        self.points = []
        self._set_all_points(corner1, corner2)

    def __contains__(self, item):
        if type(item) == QtCore.QPoint:
            for point in self.points:
                if point.x() == item.x() and point.y() == item.y():
                    return True
        return False

    def __repr__(self):
        return str(self.points)

    def _set_all_points(self, corner1, corner2):
        '''
        Calculate all points inside square.
        :param corner1: QtCore.QPoint
        :param corner2: QtCore.QPoint
        '''

        first_x, first_y = corner1.x(), corner1.y()
        second_x, second_y = corner2.x(), corner2.y()

        # square is actually a point
        if first_x == second_x or first_y == second_y:
            return

        # position corners
        if first_x < second_x:
            start_x, end_x = first_x, second_x
        else:
            start_x, end_x = second_x, first_x
        if first_y < second_y:
            start_y, end_y = first_y, second_y
        else:
            start_y, end_y = second_y, first_y

        # fill in points in boundary
        for x in range(start_x, end_x):
            self.points.append(QtCore.QPoint(x, start_y))
            self.points.append(QtCore.QPoint(x, end_y))
        for y in range(start_y, end_y):
            self.points.append(QtCore.QPoint(start_x, y))
            self.points.append(QtCore.QPoint(end_x, y))

