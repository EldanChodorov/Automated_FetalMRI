'''
ScanFile class represents a nifti file holding its scan files, segmentation, user marks, and status.
'''

from PyQt5 import QtWidgets, QtCore
from image_label import ImageLabel
from threading import Thread
import Shapes
from consts import *
import nibabel as nib
import numpy as np
from segment3d_itk import Brain_segmant


class ScanFile:

    def __init__(self, nifti_path, parent):

        self._nifti_path = nifti_path
        self._workspace_parent = parent
        try:
            self._nifti = nib.load(self._nifti_path)
        except FileNotFoundError:
            print('Error in path %s' % nifti_path)
            return
        self._array_data = self._nifti.get_data()

        # Nifti file does not show stable shape, sometimes as (num,x,y) and at times as (x,y,num) or (x,num,y)
        num_frames_index = self._nifti.shape.index(min(self._nifti.shape))
        x_orig_index, y_orig_index = 1, 2
        if num_frames_index == 1:
            x_orig_index, y_orig_index = 0, 2
        elif num_frames_index == 2:
            x_orig_index, y_orig_index = 0, 1
        self._array_data = self._array_data.transpose(num_frames_index, x_orig_index, y_orig_index)

        # normalize images
        self.frames = (self._array_data.astype(np.float64) / np.max(self._array_data)) * 255

        # TODO: perform in separate thread somehow
        self._contrasted_frames = histogram_equalization(self.frames)

        # index of current frame displayed
        self.frame_displayed_index = 0

        # numpy array of frames with segmentation as binary images
        self._segmentation_array = None

        # perform segmentation algorithm in separate thread so that gui is not frozen
        self._segmentation_thread = Thread(target=self._workspace_parent.perform_segmentation)
        self._segmentation_thread.setDaemon(True)

        self.image_label = ImageLabel(self.frames, self._contrasted_frames, self._workspace_parent)

        # text representing scan's status: in Queue \ Processing \ Ready \ etc.
        self.status = ''

        # class which performs the segmentation process
        self._segment_worker = Brain_segmant()

    def load_image_label(self):
        try:
            self.image_label.activate_image()
        except Exception as ex:
            print(ex)

    def run_segmentation(self):
        print('run_segmentation!  %s' % self._nifti_path)
        self.status = 'Processing'
        self._segmentation_thread.start()

    def perform_segmentation(self):
        all_points = self.image_label.shapes.all_points()
        if not all_points:
            return

        seeds = []
        for frame_idx, frame_points in all_points.items():
            if frame_points:
                for pos in frame_points:
                    translated_pos = self.image_label.label_to_image_pos(pos)
                    seeds.append((frame_idx, translated_pos.y(), translated_pos.x()))

        segmentation_array = self._segment_worker.segmentation_3d(self.frames, seeds) * 255

        if segmentation_array is not None:
            self.set_segmentation(segmentation_array)

        return segmentation_array

    def volume(self, segmentation_array):
        '''
        Calculate volume of segmentation, based on the vixel spacing of the nifti file.
        :param segmentation_array: [numpy.ndarray]
        :return: [float] volume in mm.
        '''
        pixel_dims = self._nifti._header['pixdim']
        if len(pixel_dims) == 8:
            num_pixels = np.sum(segmentation_array)
            return num_pixels * pixel_dims[1] * pixel_dims[2] * pixel_dims[3]

    def get_quantization_segmentation(self, level):
        '''
        Get segmentation after applying quantization stage with different quantum values.
        :param level: [int] the quantum value to be used, in proportion.
        :return: [numpy.ndarray] same shape as array returned from perform_segmentation()
        '''
        try:
            print(level)
            return self._segment_worker.get_quant_segment(level)
        except Exception as ex:
            print("quantization", ex)

    def set_segmentation(self, segmentation_array):
        self._segmentation_array = segmentation_array
        self.image_label.set_segmentation(segmentation_array)
        self.image_label.set_image(self.image_label.frames[self.image_label.frame_displayed_index])
        self.status = 'Segmented'

    def __str__(self):
        return self._nifti_path.split('/')[-1].split('.')[0]


def histogram_equalization(frames):
    '''
    Perform histogram equalization on the given images to improve contrast.
    :param frames: [numpy.ndarray] list of images
    :return: equalized frames, same type and shape of input.
    '''
    equalized_frames = np.zeros(frames.shape)
    for i in range(frames.shape[0]):
        hist, bins = np.histogram(frames[i].flatten(), bins=256, normed=True)
        cdf = hist.cumsum()  # cumulative distribution function
        cdf = 255 * cdf / cdf[-1]  # normalize

        # use linear interpolation of cdf to find new pixel values
        image_equalized = np.interp(frames[i].flatten(), bins[:-1], cdf)
        equalized_frames[i] = image_equalized.reshape(frames[i].shape)

    return equalized_frames
