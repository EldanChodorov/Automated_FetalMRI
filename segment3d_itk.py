import SimpleITK as sitk
import nibabel as nib
from matplotlib import pyplot as plt
import numpy as np
from scipy import ndimage as nd
from skimage import measure
# import pysegbase.pycut as pspc
# import sitk_show

SHOW_PLOTS = True

MORPH_NUM_ITERS = 3
LABEL_SEGMENTED_COLOR = 1


def sitk_show(img, title=None, margin=0.05, dpi=40):
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

    plt.show()

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
    ax.imshow(volume[ax.index],cmap='gray')
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
        return (1,2,0)
    elif min_axis == 1:
        return (0,2,1)
    else:
        return (0,1,2)


def get_display_axis(min_axis):
    if min_axis == 0:
        return (0,1,2)
    elif min_axis == 1:
        return (1,0,2)
    else:
        return (2,0,1)



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
    fixed_again_image = sitk.VotingBinaryHoleFilling(image1=data_array, radius=[3,3,3],
                                               majorityThreshold=1,
                                               backgroundValue=0,
                                               foregroundValue=LABEL_SEGMENTED_COLOR)
    fixed_again_image = sitk.VotingBinaryHoleFilling(image1=fixed_again_image, radius=[3, 3, 3],
                                                     majorityThreshold=1,
                                                     backgroundValue=0,
                                                     foregroundValue=LABEL_SEGMENTED_COLOR)
    fixed_again_image = sitk.VotingBinaryHoleFilling(image1=fixed_again_image, radius=[2, 2, 2],
                                                     majorityThreshold=1,
                                                     backgroundValue=0,
                                                     foregroundValue=LABEL_SEGMENTED_COLOR)
    fixed_again_image = sitk.VotingBinaryHoleFilling(image1=fixed_again_image, radius=[2, 2, 2],
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
    display_image = image1.transpose(get_display_axis(np.argmin(image1.shape)))
    if SHOW_PLOTS:
        multi_slice_viewer(display_image)
        plt.show()
    # display_image = image1.transpose(get_display_axis(np.argmin(image1.shape)))
    # multi_slice_viewer(display_image)
    # plt.show()
    image1 = find_conected_comp(image1,seed_list).astype(np.int)
    display_image = image1.transpose(get_display_axis(np.argmin(image1.shape)))
    if SHOW_PLOTS:
        multi_slice_viewer(display_image)
        plt.show()
    image1 = nd.morphology.binary_dilation(image1, iterations=1).astype(np.int32)
    display_image = image1.transpose(get_display_axis(np.argmin(image1.shape)))
    if SHOW_PLOTS:
        multi_slice_viewer(display_image)
        plt.show()
    return sitk.GetImageFromArray(image1)



def find_conected_comp(seg_image, seed_list):
    '''

    :param seg_image:
    :param seed_list:
    :return:
    '''
    blobs, num_blobs = measure.label(seg_image, return_num=True, connectivity=1)

    new_seg_imag = np.zeros(seg_image.shape)
    labels = [blobs[seed[1],seed[2],seed[0]] for seed in seed_list if blobs[seed[1],seed[2],seed[0]]>0]
    labels = np.unique(labels)
    for label in labels:
        new_seg_imag[np.where(blobs == label)] = 1

    return new_seg_imag

def cut_image_out(image,seed_list):
    seed_vector = np.array([[seed[1],seed[2]]for seed in seed_list]).reshape((len(seed_list),2))
    x_size = image.shape[0]
    y_size = image.shape[1]
    r_bot = np.max(seed_vector[:,0])
    r_top = np.min(seed_vector[:,0])
    c_right = np.max(seed_vector[:, 1])
    c_left = np.min(seed_vector[:, 1])

    r_points_dis = r_bot - r_top
    c_points_dis = c_right - c_left
    r_bot_cut = r_bot + int((x_size/3 - r_points_dis) / 2) if r_bot + (x_size/2 - r_points_dis) / 2 < \
                                                              x_size else x_size
    r_top_cut = r_top - int((x_size/3 - r_points_dis) / 2) if r_top - (x_size/2 - r_points_dis) /2 > 0 \
        else 0
    c_right_cut = c_right + int((y_size/3 - c_points_dis) / 2) if c_right + (y_size/2 - c_points_dis) / 2\
                                                                    < \
                                                                y_size else y_size
    c_left_cut = c_left - int((y_size/3 - c_points_dis) / 2) if c_left - (y_size/2 - c_points_dis) / 2 > 0 \
        else 0
    new_cut_imag = np.zeros(image.shape)
    new_cut_imag[r_top_cut: r_bot_cut,c_left_cut:c_right_cut,:] = image[r_top_cut: r_bot_cut,
                                                                 c_left_cut:c_right_cut,:]
    return new_cut_imag

def label_overlap(image,segmentation):
    image = sitk.Cast(sitk.RescaleIntensity(image),segmentation.GetPixelID())
    i = sitk.LabelOverlay(image,segmentation)
    return i


def segmentation_3d(array_data, seed_list):
    '''
    :param array_data: [numpy array] shape: (frame_num, x, y)
    :param seed_list: list of tuples (frame_num, x, y)
    :return: np array of 3d segmentation (frame_num,X,Y)
    '''
    try:
        array_data = array_data.transpose(1,2,0)
        sitk_image = sitk.GetImageFromArray(array_data) # (x, y,frame_num)


        #smoothing of the image while it keeps edges and borders
        sitk_image = sitk.CurvatureFlow(image1=sitk_image, timeStep=0.12, numberOfIterations=5)
        array_smoothed = sitk.GetArrayFromImage(sitk_image)
        intens_list = [array_smoothed[seed[1], seed[2], seed[0]] for seed in seed_list]

        upper_int, lower_int = np.min(intens_list), np.max(intens_list)

        # Attempt several segmentation techniques

        connected_threshold_segmented_image = segmentation_sitk_connect_threshold(sitk_image, seed_list,
                                                                                  upper_int, lower_int)
        # vector_segmented_image = segmentation_sitk_vector_confidence(sitk_image, seed_list)

        segmented_image_to_use = connected_threshold_segmented_image

        segmented_image_to_use = get_intrinsic_component(segmented_image_to_use,seed_list)

        # segmented_array = sitk.GetArrayFromImage(segmented_image_to_use)

        ##### hole filling - time consuming ##########################
        closed_holes_image = close_holes_opening_closing(segmented_image_to_use)
        ##### hole filling - time consuming ##########################


        final_array = sitk.GetArrayFromImage(closed_holes_image)
        final_array = final_array.transpose(2,0,1)

        return final_array

    except Exception as ex:
        print('segmentation Error', type(ex), ex)
        return None
#
# if __name__ == '__main__':
#     nifti_path = 'C:\\Users\\Eldan\\Dropbox\\University\\Final  Project - joint dir\\engineer\\Final ' \
#                  'Project\\FetalBrainSegTool\\Nifti Files\\St08_Se09_Sag  T2 FRFSE ARC\\9_fetal.nii.gz'
#     nifti_path = 'C:\\Users\\Eldan\\Dropbox\\University\\Final  Project - joint dir\\engineer\\Final ' \
#            'Project\\FetalBrainSegToolNifti Files\\5_fetal.nii.gz'
#     nifti_path='C:\\Users\\Eldan\\Documents\\Final Project\\FetalBrainSegToolNifti Files\\5_fetal.nii.gz'
#
#
#     # array_data_sitk = sitk.GetImageFromArray(array_data)
#     list_seeds = [(5,230,230),(8,230,230),(10,230,230),(7,230,230)]
#
#     segmentation_3d(nifti,list_seeds)
    nifti_path = 'C:\\Users\\Keren Meron\\Documents\\School Work\\Fetal MRI\\FetalBrainSegTool\\Nifti ' \
                 'Files\\St08_Se04_Cor  T2 FRFSE ARC\\4_fetal.nii.gz'
    nifti = nib.load(nifti_path)
    array_data = nifti.get_data()
    segmentation_graph_cut(array_data, None)
