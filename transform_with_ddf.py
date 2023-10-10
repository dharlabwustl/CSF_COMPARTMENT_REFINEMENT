"""
A DeepReg Demo for classical nonrigid iterative pairwise registration algorithms
"""
import argparse
import os,sys
import shutil

import h5py
import tensorflow as tf

import deepreg.model.layer as layer
import deepreg.util as util
from deepreg.registry import REGISTRY
import nibabel as nib

# parser = argparse.ArgumentParser()
# parser.add_argument("thisfilename",
#                    help="The name of the current file to be used for registration")
# parser.add_argument("thisdirectoryname",
#                    help="The name of the current file to be used for registration")
# parser.add_argument(
#     "--test",
#     help="Execute the script with reduced image size for test purpose.",
#     dest="test",
#     action="store_true",
# )
# parser.add_argument(
#     "--full",
#     help="Execute the script with full configuration.",
#     dest="test",
#     action="store_false",
# )
# parser.set_defaults(test=False)
# args = parser.parse_args()

# def transform_with_a_ddf(h5filename,var_ddf_filename):
# parser.set_defaults(test=False)
# args = parser.parse_args()
h5filename=sys.argv[1]
filename_prefix=os.path.basename(h5filename).split('_resaved_levelset')[0]+"_T_APPLIED_"
var_ddf_filename=sys.argv[2]
SAVE_PATH=sys.argv[3]
MAIN_PATH = os.getcwd()
PROJECT_DIR ="./" # "demos/classical_mr_prostate_nonrigid"
os.chdir(PROJECT_DIR)

# DATA_PATH = "dataset"

FILE_PATH = h5filename #os.path.join(DATA_PATH, h5filename ) #"demo2.h5")

# registration parameters
image_loss_config = {"name": "lncc"}
deform_loss_config = {"name": "bending"}
weight_deform_loss = 1
learning_rate = 0.1
total_iter = 3000 ##int(10) if args.test else int(3000)

# # load images
# if not os.path.exists(DATA_PATH):
#     raise ValueError("Download the data using demo_data.py script")
# if not os.path.exists(FILE_PATH):
#     raise ValueError("Download the data using demo_data.py script")

fid = h5py.File(FILE_PATH, "r")
moving_image = tf.cast(tf.expand_dims(fid["image0"], axis=0), dtype=tf.float32)
fixed_image = tf.cast(tf.expand_dims(fid["image1"], axis=0), dtype=tf.float32)




# ddf as trainable weights
fixed_image_size = fixed_image.shape

var_ddf = nib.load(var_ddf_filename).get_fdata() #tf.Variable(initializer(fixed_image_size + [3]), name="ddf", trainable=True)

warping = layer.Warping(fixed_image_size=fixed_image_size[1:4])

warped_moving_image = warping(inputs=[var_ddf, moving_image])

# warp the moving label using the optimised affine transformation
moving_label = tf.cast(tf.expand_dims(fid["label0"], axis=0), dtype=tf.float32)
fixed_label = tf.cast(tf.expand_dims(fid["label1"], axis=0), dtype=tf.float32)
warped_moving_label = warping(inputs=[var_ddf, moving_label])

# save output to files
# SAVE_PATH = "logs_reg_1"
if os.path.exists(SAVE_PATH):
    shutil.rmtree(SAVE_PATH)
os.mkdir(SAVE_PATH)

arrays = [
    tf.squeeze(a)
    for a in [
        moving_image,
        fixed_image,
        warped_moving_image,
        moving_label,
        fixed_label,
        warped_moving_label,
        var_ddf,
    ]
]
# arr_names = [
#     "moving_image",
#     "fixed_image",
#     "warped_moving_image",
#     "moving_label",
#     "fixed_label",
#     "warped_moving_label",
#     "ddf",
# ]
arr_names = [
    filename_prefix+"moving_image",
    filename_prefix+"fixed_image",
    filename_prefix+"warped_moving_image",
    filename_prefix+"moving_label",
    filename_prefix+"fixed_label",
    filename_prefix+"warped_moving_label",
    filename_prefix+"ddf",
]
for arr, arr_name in zip(arrays, arr_names):
    util.save_array(
        save_dir=SAVE_PATH, arr=arr, name=arr_name, normalize=True, save_png=False
    )

os.chdir(MAIN_PATH)
# h5filename="SAH_1_01052014_2003_2_resaved_levelset_brain_fscct_strippedResampled1_onlyventricle_lin1_1_h5data.h5"   
# var_ddf_filename='/storage1/fs1/dharr/Active/ATUL/PROJECTS/DeepReg/demos/classical_mr_prostate_nonrigid/logs_reg/ddf.nii.gz'    
# transform_with_a_ddf(h5filename,var_ddf_filename)