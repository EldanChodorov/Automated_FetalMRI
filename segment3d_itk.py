import time

from scipy import spatial
from skimage import feature
import SimpleITK as sitk
import nibabel as nib
from matplotlib import pyplot as plt
import numpy as np
from scipy import ndimage as nd
from skimage import segmentation
from skimage import measure
# import pysegbase.pycut as pspc
# import sitk_show
from sklearn.cluster import KMeans
from sklearn.cluster import k_means
import chan_vese
from multiprocessing import Pool, Lock
import chan_vese_3d

MORPH_NUM_ITERS = 3
LABEL_SEGMENTED_COLOR = 1

# global dictionary to hold segmentations performed by threads
segmentations_container = dict()
segmentations_lock = Lock()

class Brain_segmant:


    def __init__(self, brain_image = None,display_work = False):
        self.init_points = []
        self.prev_segmantation = []
        self.brain_image = brain_image
        self.seed_vec = []
        self.display_work = display_work
        self.convex_segment = 0


    def add_init_points(self,seed_list ):
        for seed in seed_list:
            self.seed_vec.append([seed[1], seed[2], seed[0]])
        pass


    def sitk_show(self,img, title=None, margin=0.05, dpi=40):
        print(type(img))
        nda = sitk.GetArrayFromImage(img)
        spacing = img.GetSpacing()
        figsize = (1 + margin) * nda.shape[0] / dpi, (1 + margin) * nda.shape[1] / dpi
        extent = (0, nda.shape[1] * spacing[1], nda.shape[0] * spacing[0], 0)
        fig = plt.figure(figsize=figsize, dpi=dpi)
        ax = fig.add_axes([margin, margin, 1 - 2 * margin, 1 - 2 * margin])

        plt.set_cmap("gray")
        ax.imshow(nda, extent=extent, interpolation=None)

        if title:
            plt.title(title)

        # #plt.show()


    def remove_keymap_conflicts(self,new_keys_set):
        for prop in plt.rcParams:
            if prop.startswith('keymap.'):
                keys = plt.rcParams[prop]
                remove_list = set(keys) & new_keys_set
                for key in remove_list:
                    keys.remove(key)


    def multi_slice_viewer(self,volume, do_gray = True):
        self.remove_keymap_conflicts({'j', 'k'})
        fig, ax = plt.subplots()
        ax.volume = volume
        ax.index = volume.shape[0] // 2
        if do_gray:
            ax.imshow(volume[ax.index],cmap = 'gray')
        else:
            ax.imshow(volume[ax.index])
        fig.canvas.mpl_connect('key_press_event', self.process_key)


    def process_key(self,event):
        fig = event.canvas.figure
        ax = fig.axes[0]
        if event.key == 'j':
            self.previous_slice(ax)
        elif event.key == 'k':
            self.next_slice(ax)
        fig.canvas.draw()


    def previous_slice(self,ax):
        volume = ax.volume
        ax.index = (ax.index - 1) % volume.shape[0]  # wrap around using %
        ax.images[0].set_array(volume[ax.index])


    def next_slice(self,ax):
        volume = ax.volume
        ax.index = (ax.index + 1) % volume.shape[0]
        ax.images[0].set_array(volume[ax.index])


    def get_correct_order(self,min_axis):
        '''
        returns the order of the image matrix according as required, frame and then X Y
        :param min_axis: The smallest axis
        :return: tuple with the correct order
        '''
        if min_axis == 0:
            return (1, 2, 0)
        elif min_axis == 1:
            return (0, 2, 1)
        else:
            return (0, 1, 2)


    def get_display_axis(self,min_axis):
        if min_axis == 0:
            return (0, 1, 2)
        elif min_axis == 1:
            return (1, 0, 2)
        else:
            return (2, 0, 1)


    def close_holes_opening_closing(self,data_array):
        '''
        Close holes in image by using morphological operations.
        :param data_array: numpy array
        :return: sitk Image
        '''
        # for i in range(MORPH_NUM_ITERS):
        # data_array = nd.morphology.binary_erosion(data_array, iterations=1).astype(np.int32)
        # data_array = nd.morphology.binary_dilation(data_array, iterations=1).astype(np.int32)

        # fixed_image = sitk.GetImageFromArray(data_array)
        fixed_again_image = sitk.VotingBinaryHoleFilling(image1=data_array, radius=[3, 3, 3],
                                                         majorityThreshold=1,
                                                         backgroundValue=0,
                                                         foregroundValue=LABEL_SEGMENTED_COLOR)
        return fixed_again_image


    def segmentation_sitk_vector_confidence(self,sitk_image, seeds):
        sitk_image = sitk.Cast(sitk_image, sitk.sitkVectorFloat64)
        CC_image = sitk.VectorConfidenceConnected(image1=sitk_image,
                                                  seedList=seeds,
                                                  numberOfIterations=1,
                                                  multiplier=0.1,
                                                  replaceValue=LABEL_SEGMENTED_COLOR)
        return sitk.GetImageFromArray(CC_image)


    def get_intrinsic_component(self,image, seed_list,with_care = True):
        data_array = sitk.GetArrayFromImage(image)
        print('finding inteinsic')
        image1 = data_array.copy()
        if with_care:
            image1 = nd.morphology.binary_opening(data_array, iterations=1).astype(np.int32)
            image1 = nd.morphology.binary_erosion(image1 , iterations=2).astype(np.int32)

        image1 = self.find_conected_comp(image1, seed_list).astype(np.int)
        image1 = nd.morphology.binary_dilation(image1, iterations=2).astype(np.int32)
        print('finding inteinsic 2')
        if self.display_work:
            display_image = image1.transpose(self.get_display_axis(np.argmin(image1.shape)))
            self.multi_slice_viewer(display_image)
            plt.show()
        return sitk.GetImageFromArray(image1)


    def find_conected_comp(self,seg_image, seed_list):
        '''

        :param seg_image:
        :param seed_list:
        :return:
        '''
        blobs, num_blobs = measure.label(seg_image, return_num=True, connectivity=1)

        new_seg_imag = np.zeros(seg_image.shape)
        labels = [blobs[seed[0], seed[1],  seed[2]] for seed in seed_list if blobs[seed[0], seed[1],  seed[2]] > 0]
        labels = np.unique(labels)
        for label in labels:
            # print((np.where(blobs == label)[0]).size)
            if label != 0:
                new_seg_imag[np.where(blobs == label)] = 1

        return new_seg_imag


    def cut_image_out(self,image, BB_object):
        '''

        :param image:
        :param bounding_box_list: array of four corners of the bbx
        :return:
        '''
        # seed_vector = np.array([[seed[1], seed[2]] for seed in dict_bounding_box['outside']])

        x_size = image.shape[0]
        y_size = image.shape[1]

        r_points_dis = BB_object[3] - BB_object[0]
        c_points_dis = BB_object[4] -  BB_object[1]
        r_bot_cut = BB_object[3] + int((x_size / 2 - r_points_dis) / 2) if BB_object[3] + (x_size / 2 -
                                                                                           r_points_dis) / 2 < \
                                                                    x_size else x_size
        r_top_cut = BB_object[0] - int((x_size / 2 - r_points_dis) / 2) if BB_object[0] - (x_size / 2 -
                                                                                           r_points_dis) / 2 > 0 \
            else 0
        c_right_cut = BB_object[4] + int((y_size / 2 - c_points_dis) / 2) if BB_object[4] + (y_size / 2 -
                                                                                             c_points_dis) / 2 \
                                                                        < \
                                                                        y_size else y_size
        c_left_cut = BB_object[1] - int((y_size / 2 - c_points_dis) / 2) if BB_object[1] - (y_size / 2 -
                                                                                            c_points_dis) / 2 > 0 \
            else 0

        return image[r_top_cut: r_bot_cut ,c_left_cut:c_right_cut, :], r_top_cut,r_bot_cut-r_top_cut, \
               c_left_cut,c_right_cut-c_left_cut


    def worker_chanvese(self,index, cur_img, cur_mask):
        '''
        Worker method for threading, performs chan vese.
        Save fixed segmentation_mat in global variable.
        :param index: [int] index of slice performing on
        :param cur_img: image to perform algorithm on
        :param cur_mask: mask for chan vese algorithm
        '''
        print('start %d' % index)
        if np.any(cur_mask == 1):
            result, _, _ = chan_vese.chanvese(I=cur_img, init_mask=cur_mask, max_its=1500, display=False,thresh=0.6,
                                              alpha=0.15)
            segmentation_mat = result
        else:
            segmentation_mat = cur_mask

        print('finish %d' % index)
        return (segmentation_mat, index)


    def worker_contur(self,index, cur_img, snake,cur_mask):
        '''
        Worker method for threading, performs chan vese.
        Save fixed segmentation_mat in global variable.
        :param index: [int] index of slice performing on
        :param cur_img: image to perform algorithm on
        :param cur_mask: mask for chan vese algorithm
        '''
        print('start %d' % index)
        if snake[0].shape[0] > 1:
            new_snake = segmentation.active_contour(cur_img,snake[0],alpha=0.005, beta=5, gamma=0.01).astype(np.int32)
            if new_snake.shape[0] > 0:
                new_image = np.zeros(cur_img.shape)
                new_image[new_snake[:,0],new_snake[:,1]] = 1
                segmentation_mat = new_image
            else:
                segmentation_mat = cur_mask
        else:
            segmentation_mat = cur_mask

        print('finish %d' % index)
        return (segmentation_mat, index)
        # # store in global container
        # segmentations_lock.acquire()
        # global segmentations_container
        # segmentations_container[index] = segmentation_mat
        # segmentations_lock.release()

    def kmeans_clean_up(self,cut_out_image):
        d, h, w = cut_out_image.shape
        print('before')
        print(np.unique(cut_out_image).shape)
        if self.display_work:
            display_image = cut_out_image.transpose(self.get_display_axis(np.argmin(cut_out_image.shape)))
            self.multi_slice_viewer(display_image,do_gray=True)
            plt.show()

        after_quant = np.zeros((cut_out_image.shape))
        for i,slice in enumerate(cut_out_image):
            after_quant[i,:,:] = self.quantize(slice,levels=20,maxCount=255)
        if self.display_work:
            display_image = after_quant.transpose(self.get_display_axis(np.argmin(after_quant.shape)))
            self.multi_slice_viewer(display_image,do_gray=True)
            plt.show()
        print('after')
        print(np.unique(after_quant).shape)
        for i in np.unique(after_quant):
            print(i)




        return after_quant

    def flood_fill_hull(self,image):
        points = np.transpose(np.where(image))
        hull = spatial.ConvexHull(points)
        deln = spatial.Delaunay(points[hull.vertices])
        idx = np.stack(np.indices(image.shape), axis=-1)
        out_idx = np.nonzero(deln.find_simplex(idx) + 1)
        out_img = np.zeros(image.shape)
        out_img[out_idx] = 1
        return out_img, hull



    def segmentation_3d(self,array_data,seed_list):
        '''
        :param array_data: [numpy array] shape: (frame_num, x, y)
        :param seed_list: list of tuples (frame_num, x, y)
        :return: np array of 3d segmentation (frame_num,X,Y)
        '''
        try:
            seed_vec = np.array([np.array([seed[1], seed[2], seed[0]])for seed in seed_list])
            # for i,seed in enumerate(seed_list):
            #     seed_vec[i,:] = np.array([seed[1], seed[2], seed[0]])
            num_frame, x, y = array_data.shape
            array_data = array_data.transpose(1, 2, 0)
            zero_mat = np.zeros(array_data.shape)
            zero_mat[seed_vec[:,0],seed_vec[:,1],seed_vec[:,2]] = 1

            image_data = measure.regionprops(zero_mat.astype(np.int32))
            BB_object = image_data[0].bbox
            zero_mat, _ = self.flood_fill_hull(zero_mat)



            small_image_1, X_top,X_size, Y_top, Y_size = self.cut_image_out(array_data,BB_object)
            mask_image = np.zeros(small_image_1.shape)
            mask_image[BB_object[0]- X_top:BB_object[3]-X_top, BB_object[1]-Y_top:BB_object[4]-Y_top, BB_object[
                2]:BB_object[5]] = zero_mat[BB_object[0]:BB_object[3], BB_object[1]:BB_object[4], BB_object[2]:BB_object[5]]
            # contour = [measure.find_contours(mask_image[:,:,i], 0.8) for i in range(mask_image.shape[2])]

            seg_mat = np.zeros(small_image_1.shape)
            images = []
            masks = []
            a = time.time()
            sitk_image = sitk.GetImageFromArray(small_image_1)
            sitk_image_1 = sitk.CurvatureFlow(image1=sitk_image, timeStep=0.3, numberOfIterations=1)
            small_image = sitk.GetArrayFromImage(sitk_image_1)
            # results = []
            for j in range(num_frame):
                # results.append(worker_chanvese(j,small_image[:, :, j],mask_image[:, :, j]))
                # new_image = self.worker_contur(j,small_image[:, :, j],contour[j],mask_image[:, :, j])
                images.append(small_image[:, :, j])
                masks.append(mask_image[:, :, j])
            # results = np.array(results)
            #
            pool = Pool()
            results = pool.starmap(self.worker_chanvese, zip(range(num_frame), images, masks))
            pool.close()
            b = time.time()
            print(b - a)
            pool.join()
            print('pool done.')


            assert len(results) == num_frame
            # # extract segmentation slices and place into one matrix
            for mat, idx in results:
                seg_mat[:, :, idx] = mat

            if self.display_work:
                display_image = seg_mat.transpose(self.get_display_axis(np.argmin(seg_mat.shape)))
                self.multi_slice_viewer(display_image, do_gray=True)
                plt.show()

            sitk_image = sitk.GetImageFromArray(seg_mat.astype(np.int32))  # (x, y,frame_num)
            nurm_seed_vec = seed_vec.copy()
            nurm_seed_vec[:,0] -= X_top
            nurm_seed_vec[:,1] -= Y_top

            segmented_image_to_use = self.get_intrinsic_component(sitk_image, nurm_seed_vec)
            closed_holes_image = sitk.GetArrayFromImage(segmented_image_to_use)
            convex_holes_image,_ = self.flood_fill_hull(closed_holes_image)
            cut_out_image = small_image * convex_holes_image

            # canny_image = np.zeros(cut_out_image.shape)
            # for j in range(num_frame):
            #     canny_image[:, :, j] = feature.canny(cut_out_image[:, :, j], sigma=0.5).astype(np.int32)

            if self.display_work:
                display_image = closed_holes_image.transpose(self.get_display_axis(np.argmin(closed_holes_image.shape)))
                self.multi_slice_viewer(display_image, do_gray=True)
                plt.show()


            #clean up with kmeans
            lables = self.kmeans_clean_up(cut_out_image)

            # cut_out_image = cut_out_image * lables


            closed_holes_image[np.where(lables == np.max(lables))] = 0
            lables[np.where(lables == np.max(lables))] = 0
            if self.display_work:
                display_image = closed_holes_image.transpose(self.get_display_axis(np.argmin(closed_holes_image.shape)))
                self.multi_slice_viewer(display_image, do_gray=True)
                plt.show()
            closed_holes_image[np.where(lables == np.max(lables))] = 0
            lables[np.where(lables == np.max(lables))] = 0
            if self.display_work:
                display_image = closed_holes_image.transpose(self.get_display_axis(np.argmin(closed_holes_image.shape)))
                self.multi_slice_viewer(display_image, do_gray=True)
                plt.show()
            closed_holes_image[np.where(lables == np.max(lables))] = 0
            # avg_colores = range(avg_color-int(2*std),avg_color)
            # print(avg_colores)
            # convex_labe , _ = self.flood_fill_hull(lables)
            #
            # smaller_images = np.zeros(small_image_1.shape)
            # smaller_images[np.where(convex_labe == 1)] = small_image[np.where(convex_labe == 1)]
            # smaller_images = smaller_images.astype(np.int32)
            # for color in avg_colores:
            #     lables[np.where(smaller_images == color)] = 1
            lables = nd.morphology.binary_closing(closed_holes_image)
            mask = np.ones((3,3))
            big_mask = np.zeros((3,3,3))
            big_mask[:,:,1] = mask
            diated_image = []
            # for j in range(lables.shape[2]):
            #     diated_image.append(nd.morphology.binary_dilation(lables[:,:,j]))
            # diated_image = np.array(diated_image)
            # lables = nd.morphology.binary_fill_holes(lables,structure=mask)
            final_image = np.zeros(array_data.shape)
            h,w, z = closed_holes_image.shape
            final_image[X_top:X_top + h,Y_top:Y_top + w,:] = lables
            print(np.max(final_image))
            return final_image.transpose(2, 0, 1)

        except Exception as ex:
            print('segmentation', type(ex), ex)
            return None



    def quantize(self,im, levels, qtype='uniform', maxCount=255, displayLevels=None):
        """
        Function to run uniform gray-level and improved gray-scale Quantization.
        This takes in an image, and buckets the gray values depending on the params.
        Args:
            im (array): image to be quantized as an array of values from 0 to 255
            levels (int): number of levels to quantize to.
                This should be a positive integer, and smaller than the maxCount.
            qtype (optional[string]): the type of quantization to perform.
                Can be either 'uniform' or 'igs'; Defaults to 'uniform'.
            maxCount (optional[int]): the maximum value for a digital count
            displayLevels (optional[int]): the number of gray levels to expand to.
                By default this value is None and will shrink the range of greys.
                This value should be a positive integer when provided.
        Return:
            the quantized image
        """
        # default value if we need to return early
        returnImage = im

        # get int type
        dtype = im.dtype

        if (displayLevels == None):
            # by default don't re-expand the image
            displayCount = levels
        elif displayLevels > 0:
            displayCount = displayLevels-1
        else:
            print("displayLevels is an invalid value")
            return returnImage

        # we're getting one more level than we should be, so minus 1
        if ((levels > 0) and (levels < maxCount)):
            levels = levels - 1
        else:
            print("levels needs to be a positive value, and smaller than the maxCount")
            return returnImage

        if (qtype == 'uniform'):
            # uniform method from lecture
            returnImage = np.floor((im/((maxCount+1)/float(levels))))*(displayCount/levels)

        elif (qtype == 'igs'):
            # error diffusion method from lecture

            # default error as 0 for the first pixel
            error = 0

            # the list of rows that will be turned into an image
            returnList = []
            for i in range(len(im)):
                returnRow = []
                for j in range(len(im[i])):
                    # get a new digital count with the error
                    errDC = im[i][j] + error
                    # save the error for the next pixel
                    error = errDC % (maxCount/levels)

                    # calculate the new digital count, and append it to the row
                    newDC = np.floor((errDC)/(maxCount/levels))
                    returnRow.append(newDC*(displayCount/levels))
                # append the row to the final image
                returnList.append(np.array(returnRow))

            returnImage = np.array(returnList, dtype)

        else:
            # invalid qtype
            print('qtype is an invalid value, please use "uniform", or "igs"')

        print(returnImage)
        return np.array(returnImage, dtype)










def confidance_evaluation(alg_seg, gt_seg):
    union_seg = alg_seg + gt_seg
    union_seg[np.where(union_seg  > 0 )] = 1
    union_num = np.count_nonzero(union_seg)

    intersection_seg = alg_seg * gt_seg
    intersection_num = np.count_nonzero(intersection_seg)

    return intersection_num / union_num

if __name__ == '__main__':
    pass
#_chan_vase_2d
