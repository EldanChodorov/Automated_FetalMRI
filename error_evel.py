import argparse
from segment3d_itk import *

def confidence_evaluation(alg_nifti_path, gt_nifti_path):
    import nibabel as nib
    seg_tool = Brain_segmant()
    seg_alg = np.array(nib.load(alg_nifti_path).get_data())
    seg_gt = np.array(nib.load(gt_nifti_path).get_data())
    seg_alg = np.flip(seg_alg.transpose(seg_tool.get_display_axis(np.argmin(seg_alg.shape))),axis=0)
    seg_gt = seg_gt.transpose(seg_tool.get_display_axis(np.argmin(seg_gt.shape))).transpose((0,2,1))
    if False:
        print(seg_alg.shape)
        print(seg_gt.shape)
        display_image = seg_alg
        seg_tool.multi_slice_viewer(display_image, do_gray=True)
        display_image = seg_gt
        seg_tool.multi_slice_viewer(display_image, do_gray=True)
        plt.show()


    sum_num = np.count_nonzero(seg_alg) + np.count_nonzero(seg_gt)
    smaller_count = np.min(np.count_nonzero(seg_alg),np.count_nonzero(seg_gt))
    union_num = np.count_nonzero(seg_alg +seg_gt)
    intersection_seg = seg_alg * seg_gt
    intersection_num = np.count_nonzero(intersection_seg)
    print('VOE co:',(2*intersection_num) / sum_num)
    print('dice co:',(intersection_num) / union_num)
    print("Overlap coefficient:",intersection_num/smaller_count )
    return (2*intersection_num) / union_num





def plot_graph_and_error():
    x = np.array([0,3,5,7,9,11,14])
    y = np.array([0.8322,0.8599,0.8751,0.8844,0.9028,0.9312,0.9532])
    # y = np.array([0.7384,0.7711,0.7907,0.8182,0.8253,0.8512,0.8832])
    y = 1-y
    # error = np.array([0.05558971491,0.03789671077,0.04453618808,0.04501453043,0.05650192874,0.04650192874,0.03650192874])
    plt.errorbar(x,y, fmt='-o')
    plt.ylim([0, 0.4])
    plt.xlim([-0.5, 15])
    plt.title("Volume Overlap Error Vs Time Spent on Corrections")
    plt.xlabel("Time [min]")
    plt.ylabel("Error")
    plt.locator_params(axis='y', nbins=10)
    plt.locator_params(axis='x', nbins=15)
    plt.rcParams.update({'font.size': 24})
    plt.rc('xtick', labelsize=60)
    plt.rc('ytick', labelsize=70)
    for i,j in zip(x,y):
        plt.annotate(str("{0:.3f}".format(round(j,3))),xy=(i,j))
    plt.show()


if __name__ == '__main__':

    # parser = argparse.ArgumentParser(description='Process the pathe to get dice co')
    # parser.add_argument('--alg',type=str,
    #                     help='an integer for the accumulator')
    # parser.add_argument('--gt', type=str,
    #                     help='an integer for the accumulator')
    #
    # args = parser.parse_args()
    # alg_path = args.alg
    # gt_path = args.gt
    # import os
    # from os import listdir
    # from os.path import isfile, join
    # onlyfiles = [f for f in listdir(alg_path) if isfile(join(alg_path, f))]
    #
    # for file in onlyfiles:
    #     full_name = os.path.abspath(os.path.join(alg_path, file))
    #     print(full_name)
    #     print(gt_path)
    #     confidence_evaluation(full_name,gt_path)
    plot_graph_and_error()
