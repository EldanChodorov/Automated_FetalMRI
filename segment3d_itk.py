import SimpleITK as sitk
import nibabel as nib
from matplotlib import pyplot as plt
import numpy as np
from scipy import ndimage as nd
from skimage import morphology
from skimage import measure
# import pysegbase.pycut as pspc
# import sitk_show
from sklearn.cluster import KMeans
import chan_vese
from multiprocessing import Pool, Lock
# from segmentation_code import chan_vese_3d

MORPH_NUM_ITERS = 3
LABEL_SEGMENTED_COLOR = 1

# global dictionary to hold segmentations performed by threads
segmentations_container = dict()
segmentations_lock = Lock()


def sitk_show(img, title=None, margin=0.05, dpi=40):
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

    # plt.show()


def remove_keymap_conflicts(new_keys_set):
    for prop in plt.rcParams:
        if prop.startswith('keymap.'):
            keys = plt.rcParams[prop]
            remove_list = set(keys) & new_keys_set
            for key in remove_list:
                keys.remove(key)


def multi_slice_viewer(volume):
    remove_keymap_conflicts({'j', 'k'})
    fig, ax = plt.subplots()
    ax.volume = volume
    ax.index = volume.shape[0] // 2
    ax.imshow(volume[ax.index], cmap='gray')
    fig.canvas.mpl_connect('key_press_event', process_key)


def process_key(event):
    fig = event.canvas.figure
    ax = fig.axes[0]
    if event.key == 'j':
        previous_slice(ax)
    elif event.key == 'k':
        next_slice(ax)
    fig.canvas.draw()


def previous_slice(ax):
    volume = ax.volume
    ax.index = (ax.index - 1) % volume.shape[0]  # wrap around using %
    ax.images[0].set_array(volume[ax.index])


def next_slice(ax):
    volume = ax.volume
    ax.index = (ax.index + 1) % volume.shape[0]
    ax.images[0].set_array(volume[ax.index])


def get_correct_order(min_axis):
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


def get_display_axis(min_axis):
    if min_axis == 0:
        return (0, 1, 2)
    elif min_axis == 1:
        return (1, 0, 2)
    else:
        return (2, 0, 1)


# def segmentation_graph_cut(data_array, seeds):
#     igc = pspc.ImageGraphCut(data_array, voxelsize=[1, 1, 1])
#     seeds = igc.interactivity()
#     print(seeds)


def segmentation_sitk_connect_threshold(image, seeds, lower_intensity, upper_intensity):
    '''
    Perform sitk.ConnectedThreshold
    :param image: sitk.Image
    :param seeds: list of tuples
    :return: Image with segmentation
    '''
    return sitk.ConnectedThreshold(image1=image, seedList=seeds,
                                   lower=float(lower_intensity),
                                   upper=float(upper_intensity),
                                   replaceValue=LABEL_SEGMENTED_COLOR)


def close_holes_opening_closing(data_array):
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


def segmentation_sitk_vector_confidence(sitk_image, seeds):
    sitk_image = sitk.Cast(sitk_image, sitk.sitkVectorFloat64)
    CC_image = sitk.VectorConfidenceConnected(image1=sitk_image,
                                              seedList=seeds,
                                              numberOfIterations=1,
                                              multiplier=0.1,
                                              replaceValue=LABEL_SEGMENTED_COLOR)
    return sitk.GetImageFromArray(CC_image)


def get_intrinsic_component(image, seed_list):
    data_array = sitk.GetArrayFromImage(image)

    image1 = nd.morphology.binary_erosion(data_array, iterations=1).astype(np.int32)
    image1 = find_conected_comp(image1, seed_list).astype(np.int)
    image1 = nd.morphology.binary_dilation(image1, iterations=1).astype(np.int32)

    # display_image = image1.transpose(get_display_axis(np.argmin(image1.shape)))
    # multi_slice_viewer(display_image)
    # plt.show()
    return sitk.GetImageFromArray(image1)


def find_conected_comp(seg_image, seed_list):
    '''

    :param seg_image:
    :param seed_list:
    :return:
    '''
    blobs, num_blobs = measure.label(seg_image, return_num=True, connectivity=1)

    new_seg_imag = np.zeros(seg_image.shape)
    labels = [blobs[seed[1], seed[2], seed[0]] for seed in seed_list if blobs[seed[1], seed[2], seed[0]] > 0]
    labels = np.unique(labels)
    for label in labels:
        # print((np.where(blobs == label)[0]).size)
        new_seg_imag[np.where(blobs == label)] = 1

    return new_seg_imag


def cut_image_out(image, seed_list):
    seed_vector = np.array([[seed[1], seed[2]] for seed in seed_list]).reshape((len(seed_list), 2))
    x_size = image.shape[0]
    y_size = image.shape[1]
    r_bot = np.max(seed_vector[:, 0])
    r_top = np.min(seed_vector[:, 0])
    c_right = np.max(seed_vector[:, 1])
    c_left = np.min(seed_vector[:, 1])

    r_points_dis = r_bot - r_top
    c_points_dis = c_right - c_left
    r_bot_cut = r_bot + int((x_size / 3 - r_points_dis) / 2) if r_bot + (x_size / 2 - r_points_dis) / 2 < \
                                                                x_size else x_size
    r_top_cut = r_top - int((x_size / 3 - r_points_dis) / 2) if r_top - (x_size / 2 - r_points_dis) / 2 > 0 \
        else 0
    c_right_cut = c_right + int((y_size / 3 - c_points_dis) / 2) if c_right + (y_size / 2 - c_points_dis) / 2 \
                                                                    < \
                                                                    y_size else y_size
    c_left_cut = c_left - int((y_size / 3 - c_points_dis) / 2) if c_left - (y_size / 2 - c_points_dis) / 2 > 0 \
        else 0
    new_cut_imag = np.zeros(image.shape)
    new_cut_imag[r_top_cut: r_bot_cut, c_left_cut:c_right_cut, :] = image[r_top_cut: r_bot_cut,
                                                                    c_left_cut:c_right_cut, :]
    return new_cut_imag


def worker_chanvese(index, cur_img, cur_mask):
    '''
    Worker method for threading, performs chan vese.
    Save fixed segmentation_mat in global variable.
    :param index: [int] index of slice performing on
    :param cur_img: image to perform algorithm on
    :param cur_mask: mask for chan vese algorithm
    '''
    print('start %d' % index)
    if np.any(cur_mask == 1):
        result, _, _ = chan_vese.chanvese(I=cur_img, init_mask=cur_mask, max_its=1000, display=False, alpha=0.1)
        segmentation_mat = result
    else:
        segmentation_mat = cur_mask

    print('finish %d' % index)
    return (segmentation_mat, index)
    # # store in global container
    # segmentations_lock.acquire()
    # global segmentations_container
    # segmentations_container[index] = segmentation_mat
    # segmentations_lock.release()


def segmentation_3d(array_data, seed_list):
    '''
    :param array_data: [numpy array] shape: (frame_num, x, y)
    :param seed_list: list of tuples (frame_num, x, y)
    :return: np array of 3d segmentation (frame_num,X,Y)
    '''
    try:
        num_frame, x, y = array_data.shape
        array_data = array_data.transpose(1, 2, 0)
        zero_mat = np.zeros(array_data.shape)
        seg_mat = np.zeros(array_data.shape)
        for seed in seed_list:
            zero_mat[seed[1], seed[2], seed[0]] = 1
        image_data = measure.regionprops(zero_mat.astype(np.int32))
        BB_object = image_data[0].bbox
        # CH_object = morphology.convex_hull_image(image_data)
        zero_mat[BB_object[0]:BB_object[3], BB_object[1]:BB_object[4], BB_object[2]:BB_object[5]] = 1

        images = []
        masks = []

        for j in range(num_frame):
            images.append(array_data[:, :, j])
            masks.append(zero_mat[:, :, j])

        pool = Pool()
        results = pool.starmap(worker_chanvese, zip(range(num_frame), images, masks))
        pool.close()
        pool.join()
        print('pool done.')

        assert len(results) == num_frame

        # extract segmentation slices and place into one matrix
        for mat, idx in results:
            seg_mat[:, :, idx] = mat

        sitk_image = sitk.GetImageFromArray(seg_mat)  # (x, y,frame_num)

        segmented_image_to_use = get_intrinsic_component(sitk_image, seed_list)

        # vector_segmented_image = segmentation_sitk_vector_confidence(sitk_image, seed_list)


        # segmented_array = sitk.GetArrayFromImage(segmented_image_to_use)
        # closed_holes_image = close_holes_opening_closing(segmented_image_to_use)
        closed_holes_image = sitk.GetArrayFromImage(segmented_image_to_use)
        display_image = closed_holes_image.transpose(get_display_axis(np.argmin(closed_holes_image.shape)))
        multi_slice_viewer(display_image)
        # plt.show()
        img = nib.Nifti1Image(closed_holes_image, np.eye(4))
        nib.save(img, 'result_seg\\new_result_chan_vase9.nii.gz')

        # cut_out_image = array_data * closed_holes_image
        # bins = int(np.max(cut_out_image)) - int(np.min(cut_out_image)) + 1

        # d, h, w = cut_out_image.shape
        # regulize_data = (cut_out_image.flatten()).reshape((d * h * w, 1))
        # kmean = KMeans(n_clusters=3).fit(regulize_data)
        # lable = kmean.predict(regulize_data).reshape((d, h, w))
        # hist = np.bincount(cut_out_image.flatten().astype(np.int32))
        # plt.scatter(range(len(hist) - 1), hist[1:])
        # lable_ramove = 1 if hist[1] < hist[2] else 2
        # lable[np.where(lable == lable_ramove)] = 0
        # lable[np.where(lable > 0)] = 1
        # convex_image = morphology.convex_hull_image(lable).astype(np.int32)
        # residual_image = convex_image - lable
        # display_image = lable.transpose(get_display_axis(np.argmin(lable.shape)))
        # multi_slice_viewer(display_image)

        #
        # img = nib.Nifti1Image(residual_image, np.eye(4))
        # nib.save(img, 'result_seg\\residual_convex_im9.nii.gz')

        # img = nib.Nifti1Image(lable, np.eye(4))
        # nib.save(img, 'result_seg\\new_result9.nii.gz')
        # final_array = sitk.GetArrayFromImage(lable * 100)
        # final_array = lable.transpose(2, 0, 1)
        # plt.show()
        return closed_holes_image.transpose(2, 0, 1)

    except Exception as ex:
        print('segmentation', type(ex), ex)
        return None


#
def segmentation_3d_1(array_data, seed_list):
    '''
    :param array_data: [numpy array] shape: (frame_num, x, y)
    :param seed_list: list of tuples (frame_num, x, y)
    :return: np array of 3d segmentation (frame_num,X,Y)
    '''
    try:
        array_data = array_data.transpose(1, 2, 0)
        sitk_image = sitk.GetImageFromArray(array_data)  # (x, y,frame_num)
        intens_list = [array_data[seed[1], seed[2], seed[0]] for seed in seed_list]

        # smoothing of the image while it keeps edges and borders
        sitk_image = sitk.CurvatureFlow(image1=sitk_image, timeStep=0.12, numberOfIterations=5)
        upper_int, lower_int = np.min(intens_list), np.max(intens_list)

        # Attempt several segmentation techniques

        connected_threshold_segmented_image = segmentation_sitk_connect_threshold(sitk_image, seed_list,
                                                                                  upper_int, lower_int)
        # vector_segmented_image = segmentation_sitk_vector_confidence(sitk_image, seed_list)

        segmented_image_to_use = connected_threshold_segmented_image

        segmented_image_to_use = get_intrinsic_component(segmented_image_to_use, seed_list)

        # segmented_array = sitk.GetArrayFromImage(segmented_image_to_use)
        closed_holes_image = close_holes_opening_closing(segmented_image_to_use)
        closed_holes_image = sitk.GetArrayFromImage(closed_holes_image)
        cut_out_image = array_data * closed_holes_image
        # bins = int(np.max(cut_out_image)) - int(np.min(cut_out_image)) + 1
        hist = np.bincount(cut_out_image.flatten().astype(np.int32))
        plt.scatter(range(len(hist)), hist)
        # plt.show()
        d, h, w = cut_out_image.shape
        regulize_data = (cut_out_image.flatten()).reshape((d * h * w, 1))
        kmean = KMeans(n_clusters=3).fit(regulize_data)
        lable = kmean.predict(regulize_data).reshape((d, h, w))

        # final_array = sitk.GetArrayFromImage(lable * 100)
        final_array = lable.transpose(2, 0, 1)

        return final_array

    except Exception as ex:
        print('segmentation', type(ex), ex)
        return None


def segmentation_3d_3d(array_data, seed_list):
    '''
    :param array_data: [numpy array] shape: (frame_num, x, y)
    :param seed_list: list of tuples (frame_num, x, y)
    :return: np array of 3d segmentation (frame_num,X,Y)
    '''
    try:
        num_frame, x, y = array_data.shape
        array_data = array_data.transpose(1, 2, 0)
        zero_mat = np.zeros(array_data.shape)
        seg_mat = np.zeros(array_data.shape)
        for seed in seed_list:
            zero_mat[seed[1], seed[2], seed[0]] = 1
        image_data = measure.regionprops(zero_mat.astype(np.int32))
        BB_object = image_data[0].bbox
        # CH_object = morphology.convex_hull_image(image_data)
        zero_mat[BB_object[0]:BB_object[3], BB_object[1]:BB_object[4], BB_object[2]:BB_object[5]] = 1

        result_3d = chan_vese_3d.chanvese3d(I=array_data, init_mask=zero_mat, max_its=1000, display=False,
                                                  alpha=0.1)

        sitk_image_3d = sitk.GetImageFromArray(result_3d)  # (x, y,frame_num)

        segmented_image_to_use_3d = get_intrinsic_component(sitk_image_3d, seed_list)
        display_image = segmented_image_to_use_3d.transpose(get_display_axis(np.argmin(segmented_image_to_use_3d.shape)))
        multi_slice_viewer(display_image)
        # plt.show()
        img = nib.Nifti1Image(segmented_image_to_use_3d, np.eye(4))
        nib.save(img, 'result_seg\\new_result_chan_vase_3d.nii.gz')
        for j in range(num_frame):
            cur_img = array_data[:, :, j]
            cur_mask = zero_mat[:, :, j]
            if np.any(cur_mask == 1):
                result, _, _ = chan_vese.chanvese(I=cur_img, init_mask=cur_mask, max_its=1000, display=True,
                                                  alpha=0.1)
                seg_mat[:, :, j] = result
            else:
                seg_mat[:, :, j] = cur_mask
        sitk_image = sitk.GetImageFromArray(seg_mat)  # (x, y,frame_num)

        segmented_image_to_use = get_intrinsic_component(sitk_image, seed_list)

        # vector_segmented_image = segmentation_sitk_vector_confidence(sitk_image, seed_list)


        # segmented_array = sitk.GetArrayFromImage(segmented_image_to_use)
        # closed_holes_image = close_holes_opening_closing(segmented_image_to_use)
        closed_holes_image = sitk.GetArrayFromImage(segmented_image_to_use)
        display_image = closed_holes_image.transpose(get_display_axis(np.argmin(closed_holes_image.shape)))
        multi_slice_viewer(display_image)
        # plt.show()
        img = nib.Nifti1Image(closed_holes_image, np.eye(4))
        nib.save(img, 'result_seg\\new_result_chan_vase_2d.nii.gz')

        return closed_holes_image.transpose(2, 0, 1)

    except Exception as ex:
        print('segmentation', type(ex), ex)
        return None



if __name__ == '__main__':
    pass
#_chan_vase_2d