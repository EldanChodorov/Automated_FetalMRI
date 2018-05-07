'''
ScanFile class represents a nifti file holding its scan files, segmentation, user marks, and status.
'''

from PyQt5 import QtWidgets, QtCore
from image_label import ImageLabel
from threading import Thread
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
        self._contrasted_frames = np.zeros((10, self.frames.shape[0], self.frames.shape[1], self.frames.shape[2]))
        for i in range(1, 11):
            self._contrasted_frames[i-1] = contrast_change(i, self.frames)

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
        self._segment_worker = Brain_segmant(self.frames)

        # what is currently displayed: USER MARKS / SEGMENTATION / CONVEX / BRAIN HALVES
        self.display_state = ''

    def load_image_label(self):
        self.image_label.activate_image()

    def run_segmentation(self):
        self.status = PROCESSING
        self._segmentation_thread.start()

    def perform_segmentation(self):

        # collect points marked by user
        all_points = self.image_label.shapes.all_points()

        # do not attempt segmentation if user did not mark enough frames
        frames_marked = 0
        for items_list in all_points.values():
            if items_list:
                frames_marked += 1
        if frames_marked < 3:
            return None

        seeds = []
        for frame_idx, frame_points in all_points.items():
            if frame_points:
                for pos in frame_points:
                    translated_pos = self.image_label.label_to_image_pos(pos)
                    seeds.append((frame_idx, translated_pos.y(), translated_pos.x()))
        segmentation_array = self._segment_worker.segmentation_3d(self.frames, seeds)

        if segmentation_array is None:
            self.status = ''
        else:
            # store marks aside before setting segmentation
            self.image_label.shapes.store_marks()

            segmentation_array *= 255
            self.set_segmentation(segmentation_array)

        return segmentation_array

    def volume(self, segmentation_array=None):
        '''
        Calculate volume of segmentation, based on the voxel spacing of the nifti file.
        :param segmentation_array [numpy.ndarray] to calculate volume
        :return: [float] volume in mm.
        '''
        if segmentation_array is None:
            segmentation_array = self.image_label.points_to_image()
        pixel_dims = self._nifti._header['pixdim']
        if len(pixel_dims) == 8:
            num_pixels = np.sum(segmentation_array)
            return (num_pixels * pixel_dims[1] * pixel_dims[2] * pixel_dims[3]) / 1000
        else:
            print('Error in calculating volume from Nifti Header.')
            return 0

    def show_brain_halves(self):
        if self._segment_worker:
            if self.display_state == SEGMENTATION:
                # TODO maybe wasteful and unnecessary to calculate this each time? think about it
                self._segmentation_array = self.image_label.points_to_image()
            try:
                left_half, right_half = self._segment_worker.separate_to_two_brains(self._segmentation_array)
                self.image_label.set_brain_halves(left_half, right_half)
                left_brain, right_brain = self.image_label.points_to_image(True)
                left_volume, right_volume = self.volume(left_brain), self.volume(right_brain)
                self._workspace_parent.set_brain_halves_volume(left_volume, right_volume)
                self.display_state = HALVES
            except Exception as ex:
                print('error in separate_to_two_brains', ex)

    def show_segmentation(self):
        '''Show current segmentation over image label.'''
        if self.display_state == MARKS:
            return
        if self.display_state == SEGMENTATION:
            self._segmentation_array = self.image_label.points_to_image()
        if self.status == SEGMENTED:
            self.display_state = SEGMENTATION
            self.image_label.set_segmentation(self._segmentation_array)

    def show_convex(self):
        '''
        Calculate convex for given segmentation of brain, and display it.
        :param segmentation_array: [numpy.ndarray]
        '''
        # save aside the given segmentation as the most updated one
        if self._segment_worker:
            if self.display_state == SEGMENTATION:
                self._segmentation_array = self.image_label.points_to_image()
            convex = self._segment_worker.flood_fill_hull(self._segmentation_array)
            self.image_label.set_segmentation(convex)
            self.display_state = CONVEX

    def show_quantization_segmentation(self, level):
        '''
        Get segmentation after applying quantization stage with different quantum values, and display it.
        :param level: [int] the quantum value to be used, in proportion.
        '''
        if self.display_state == SEGMENTATION:
            updated_seg = self.image_label.points_to_image()
            segmentation_array = self._segment_worker.get_quant_segment(level, updated_seg)
            self.set_segmentation(segmentation_array)

    def set_segmentation(self, segmentation_array):
        self.display_state = SEGMENTATION
        self.status = SEGMENTED
        self._segmentation_array = segmentation_array
        self.image_label.set_segmentation(segmentation_array)
        self.image_label.set_image(self.image_label.frames[self.image_label.frame_displayed_index])
        self._workspace_parent.set_brain_volume(self.volume())

    def __str__(self):
        return self._nifti_path.split('/')[-1].split('.')[0]


def contrast_change(index, image):
    '''
    Change contrast of a given image.
    :param index: [int] 1 <= index <= 10, affects level of contrast. 5 leaves image unchanged.
    :param image: [numpy.ndarray]
    :return: contrasted image [numpy.ndarray]
    '''
    max_intens = 255.0 if np.max(image) <= 255.0 else 1024.0
    new_image = max_intens * ((image / max_intens) ** ((index/10) * 2))
    return new_image

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
