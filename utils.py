'''
Methods used by the FetalSegBrainTool project.
'''


from PyQt5 import QtWidgets


def shape_nifti_2_segtool(array_data):
    '''
    Convert given array data's shape to adapt to the SegTool, i.e. (num_frames, x, y)
    :param array_data: given numpy array of unknown shape
    :return: same array_data, with shape (num_frames, x, y)
    '''
    num_frames_index, x_orig_index, y_orig_index = _assign_shape_indices(array_data.shape)
    return array_data.transpose(num_frames_index, x_orig_index, y_orig_index)


def shape_segtool_2_nifti(array_data):
    '''
    Convert given array data's shape to adapt to the Nifti global format, i.e. (x, num_frames, y)
    :param array_data: given numpy array of unknown shape
    :return: same array_data, with shape (x, num_frames, y)
    '''
    num_frames_index, x_orig_index, y_orig_index = _assign_shape_indices(array_data.shape)
    return array_data.transpose(num_frames_index, x_orig_index, y_orig_index)


def _assign_shape_indices(shape):
    '''
    Assign each index in given shape to one of three: (num_frames_index, x_orig_index, y_orig_index)
    :param shape: [tuple] of length 3 
    :return: (num_frames_index, x_orig_index, y_orig_index)
    '''
    num_frames_index = shape.index(min(shape))
    x_orig_index, y_orig_index = 1, 2
    if num_frames_index == 1:
        x_orig_index, y_orig_index = 0, 2
    elif num_frames_index == 2:
        x_orig_index, y_orig_index = 0, 1
    return num_frames_index, x_orig_index, y_orig_index


def warn(main_msg):
    '''
    Pop up a warning message box.
    '''
    # TODO: sometimes when this box shows, it causes the whole program to freeze and crash.
    msg_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, main_msg, main_msg, QtWidgets.QMessageBox.Ok)
    msg_box.setWindowTitle('Seg Tool Warning')
    msg_box.setMinimumSize(100, 200)
    msg_box.exec_()
