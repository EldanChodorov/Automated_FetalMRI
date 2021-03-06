
"""
ScanFile class represents a nifti file holding its scan files, 
segmentation, user marks, and status.
"""

import os
from logging import warning
from threading import Thread
import nibabel as nib
import numpy as np
import utils
from consts import *
from image_label import ImageLabel
from segment3d_itk import BrainSegment


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
        self._array_data = utils.shape_nifti_2_segtool(self._array_data)

        # normalize images
        self.frames = (self._array_data.astype(np.float64) / np.max(self._array_data)) * 255

        # TODO: perform in separate thread
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
        self._segment_worker = BrainSegment(self.frames)

        # what is currently displayed: USER MARKS / SEGMENTATION / CONVEX / BRAIN HALVES / CSF
        self.display_state = ''

        # volume calculated of different parts of the scan
        self._full_brain_volume = 0
        self._brain_halves_volume = [0, 0]
        self._csf_volume = 0

    def save_numpy_polygon(self, dest_dir):
        '''
        Save each marked point as a numpy array. All frames will be saved in a folder for this scan.
        :param dest_dir: folder to place sub-folder inside.
        '''
        polygon_numpy = self.image_label.points_to_image()
        self.save_numpy_files_handler(polygon_numpy, dest_dir)

    def save_numpy_slices(self, dest_dir):
        '''
        Save each frame as a numpy array. All frames will be saved in a folder for this scan.
        :param dest_dir: folder to place sub-folder inside.
        '''
        self.save_numpy_files_handler(self.frames, dest_dir)

    def save_numpy_files_handler(self, array_data, dest_dir):
        base_nifti_name = self._nifti_path[self._nifti_path.rfind('\\')+1:]
        base_nifti_name = base_nifti_name.rstrip('.gz').rstrip('.nii')
        a = self._nifti_path[:self._nifti_path.rfind('\\')]

        b = a[a.rfind('\\')+1:]
        extra = b[:b.rfind('_')]

        filename = os.path.join(dest_dir, base_nifti_name) + '_' + extra + '_frame' + '1'
        tmp_filename = filename
        suffix = 0
        while os.path.exists(tmp_filename + '.npz'):
            tmp_filename = filename + '_' + str(suffix)
            suffix += 1
        suffix = ('_' + tmp_filename[tmp_filename.rfind('_')+1:]) if tmp_filename != filename else ''

        for i in range(1, array_data.shape[0] - 1):
            filename = os.path.join(dest_dir, base_nifti_name) + '_' + extra + '_frame' + str(i) + suffix

            # if os.path.exists(filename + '.npz'):
            #     warning('{} was not saved, already exists.'.format(base_nifti_name))
            #     break
            np.savez(filename, array_data[i-1], array_data[i], array_data[i+1])
            print("Saved file at {}".format(filename))

    def load_image_label(self):
        self.image_label.activate_image()

    def run_segmentation(self):
        # do not run if status is not initial, cannot start a thread more than once
        # TODO: solve for a case one wants to remark and reperform segmentation
        if self.status == '':
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
                self._brain_halves_volume = [left_volume, right_volume]
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
        '''
        # save aside the given segmentation as the most updated one
        if self._segment_worker:
            if self.display_state == SEGMENTATION:
                self._segmentation_array = self.image_label.points_to_image()
            convex = self._segment_worker.flood_fill_hull(self._segmentation_array)
            self.image_label.set_segmentation(convex)
            self.display_state = CONVEX

    def show_csf(self):
        '''
        Display segmentation of brain CSF only.
        '''
        if self._segment_worker:
            if self.display_state == SEGMENTATION:
                self._segmentation_array = self.image_label.points_to_image()
            try:
                # todo need to send copy so that _segmentation_array is not changed?
                csf = self._segment_worker.get_csf_seg(self._segmentation_array)
            except Exception as ex:
                print("CSF computation error", ex)
            else:
                self.image_label.set_segmentation(csf)
                self._csf_volume = self.volume(csf)
                self._workspace_parent.set_csf_volume(self._csf_volume)
                self.display_state = CSF

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
        self._full_brain_volume = self.volume()
        self._workspace_parent.set_brain_volume(self._full_brain_volume)

    def __str__(self):
        return self._nifti_path.split('/')[-1].split('.')[0]

    @property
    def brain_volume(self):
        return self._full_brain_volume


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

