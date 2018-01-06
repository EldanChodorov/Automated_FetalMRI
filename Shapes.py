'''
Class to holds squares, points, etc. marked by user.
These polygons may have missing points, if erased by user.
'''

from collections import defaultdict
from PyQt5 import QtCore
from consts import OUTER_SQUARE, INNER_SQUARE, ERASER_WIDTH


class Shapes:

    def __init__(self):

        # dict of frame number: points chosen manually by user per each frame
        self.chosen_points = defaultdict(list)

        # dict of frame number: squares chosen manually by user per each frame
        # inner - contained in brain, outer - enclosing the brain
        self.inner_squares = defaultdict(list)
        self.outer_squares = defaultdict(list)

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

    def add_points(self, frame_number, points):
        '''
        Add given points to list of points.
        :param frame_number: [int] frame points were selected from.
        :param points: [list of QtCore.QPoint]
        '''
        for point in points:
            self.add_point(frame_number, point)

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
        for i in range(-ERASER_WIDTH, ERASER_WIDTH):
            for j in range(-ERASER_WIDTH, ERASER_WIDTH):
                pos.setX(orig_x + i)
                pos.setY(orig_y + j)

                # erase points
                if pos in self.chosen_points[frame]:
                    self.chosen_points[frame].remove(pos)

                # erase squares
                squares = self.inner_squares[frame] + self.outer_squares[frame]
                for square in squares:
                    if pos in square.points:
                        square.points.remove(pos)


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


if __name__ == '__main__':
    sq1 = Square(QtCore.QPoint(0,0), QtCore.QPoint(4,4))
    sq2 = Square(QtCore.QPoint(2,1), QtCore.QPoint(5,4))
    sq3 = Square(QtCore.QPoint(5,5), QtCore.QPoint(6,7))
    sh = Shapes()
    sh.add_square(0, QtCore.QPoint(0,0), QtCore.QPoint(4,4), INNER_SQUARE)
    sh.add_square(0, QtCore.QPoint(2,1), QtCore.QPoint(5,5), INNER_SQUARE)
    sh.add_square(1, QtCore.QPoint(5,5), QtCore.QPoint(6,7), OUTER_SQUARE)
    print(sh)
    sh.remove_points(QtCore.QPoint(5,4), 0)
    print(sh)