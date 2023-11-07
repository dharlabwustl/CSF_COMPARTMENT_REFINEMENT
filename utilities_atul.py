"""
get the extent of ventricles
"""
import nibabel as nib
import os,sys,inspect,argparse
import numpy as np
import pandas as pd
import os,glob,subprocess,sys
import h5py,re
from utilities_simple_trimmed import *
# def resizeinto_512by512(image_nib_nii_file_data):
#     print('I am in utilities_simple_trimmed.py')
#     size_diff_x=np.abs(image_nib_nii_file_data.shape[0]-512)
#     size_diff_y=np.abs(image_nib_nii_file_data.shape[1]-512)
#     temp_array=np.copy(image_nib_nii_file_data)

#     if image_nib_nii_file_data.shape[0] <512:
#         if (size_diff_x % 2 )== 0 :
#             size_diff_x=int(size_diff_x/2)
#             npad = ((size_diff_x-1, size_diff_x+1), (0, 0), (0, 0))
#         else :
#             size_diff_x=int(size_diff_x/2)
#             npad = ((size_diff_x, size_diff_x+1), (0, 0), (0, 0))  #abs(np.min(image_levelset_data)
#         temp_array=np.pad(temp_array, pad_width=npad, mode='constant', constant_values=np.min(temp_array))
#     if image_nib_nii_file_data.shape[1] <512:
#         if (size_diff_y % 2 )== 0 :
#             size_diff_y=int(size_diff_y/2)
#             npad = ((0, 0),(size_diff_y-1, size_diff_y+1),  (0, 0))
#         else :
#             size_diff_y=int(size_diff_y/2)
#             npad = ( (0, 0),(size_diff_y, size_diff_y+1), (0, 0))  #abs(np.min(image_levelset_data)
#         temp_array=np.pad(temp_array, pad_width=npad, mode='constant', constant_values=np.min(temp_array))

#     if image_nib_nii_file_data.shape[0] > 512:
#         if (size_diff_x % 2 )== 0 :
#             size_diff_x=int(size_diff_x/2)
#             temp_array=temp_array[size_diff_x:temp_array.shape[0]-size_diff_x,0:temp_array.shape[1],0:temp_array.shape[2]]
#         else :
#             size_diff_x=int(size_diff_x/2)
#             temp_array=temp_array[size_diff_x:temp_array.shape[0]-size_diff_x-1,0:temp_array.shape[1],0:temp_array.shape[2]]

#     if image_nib_nii_file_data.shape[1] > 512:
#         if (size_diff_y % 2 )== 0 :
#             size_diff_y=int(size_diff_y/2)
#             temp_array=temp_array[0:temp_array.shape[0],size_diff_y:temp_array.shape[1]-size_diff_y,0:temp_array.shape[2]]
#         else :
#             size_diff_x=int(size_diff_x/2)
#             temp_array=temp_array[0:temp_array.shape[0],size_diff_y:temp_array.shape[1]-size_diff_y-1,0:temp_array.shape[2]]

#     image_nib_nii_file_data=temp_array
#     return image_nib_nii_file_data

def gray2binary(filename,filename_mask_output):
#     filename_template='/home/atul/Documents/DEEPREG/DeepReg/demos/classical_mr_prostate_nonrigid/dataset/brain/scct_strippedResampled1.nii.gz'
    I=nib.load(filename) 
    I_data=I.get_fdata()
    min_val=0 #np.min(I_data)
    print(min_val)
    I_data[I_data>0.9]=1
    I_data[I_data<=0.9]=0
    array_mask = nib.Nifti1Image(I_data, affine=I.affine, header=I.header)
#     niigzfilenametosave2=filename_template.split('.nii')[0]+ '_BET.nii.gz' #os.path.join(OUTPUT_DIRECTORY,os.path.basename(levelset_file)) #.split(".nii")[0]+"RESIZED.nii.gz")
    nib.save(array_mask, filename_mask_output)
    return niigzfilenametosave2
def call_gray2binary(args):
    returnvalue=0
    try:
        filename=args.stuff[1]
        filename_mask_output=args.stuff[2]
        gray2binary(filename,filename_mask_output)
        command="echo successful at :: {} ::ventricle_mask_filename::  {} >> error.txt".format(inspect.stack()[0][3],filename_template)
        subprocess.call(command,shell=True)
        returnvalue=1
    except:
        command="echo failed at :: {} >> error.txt".format(inspect.stack()[0][3])
        subprocess.call(command,shell=True)
    return  returnvalue
def createh5file(image0_file,image1_file,label0_file,label1_file,output_dir="./"):
    image0=nib.load(image0_file).get_fdata() #'/home/atul/Documents/DEEPREG/DeepReg/demos/classical_mr_prostate_nonrigid/dataset/fixed_images/case_001.nii.gz').get_fdata()

    ## import gray 1
    image1=nib.load(image1_file).get_fdata() #nib.load('/home/atul/Documents/DEEPREG/DeepReg/demos/classical_mr_prostate_nonrigid/dataset/fixed_images/case_009.nii.gz').get_fdata()
    # import label 0
    label0=nib.load(label0_file).get_fdata() # nib.load('/home/atul/Documents/DEEPREG/DeepReg/demos/classical_mr_prostate_nonrigid/dataset/fixed_labels/case_001.nii.gz').get_fdata()
    # import label 1
    label0[label0>0]=1
    label0[label0<1]=0
    image0=image0*label0
    label1=nib.load(label1_file).get_fdata() #nib.load('/home/atul/Documents/DEEPREG/DeepReg/demos/classical_mr_prostate_nonrigid/dataset/fixed_labels/case_009.nii.gz').get_fdata()
    label1[label1>0]=1
    label1[label1<1]=0
    image1=image1*label1
    h5filename=os.path.join(output_dir,os.path.basename(image0_file).split('.nii')[0] + '_h5data.h5')
    print("{}:{}".format('h5filename',h5filename))
    hf = h5py.File(h5filename, 'w')
    hf.create_dataset('image0',data=image0,dtype='i2') # moving image
    hf.create_dataset('image1',data=image1,dtype='i2') # fixed image
    hf.create_dataset('label0',data=label0,dtype='i') # moving mask
    hf.create_dataset('label1',data=label1,dtype='i') # fixed mask
def call_createh5file(args):
    returnvalue=0
    try:
        image0_file=args.stuff[1]
        image1_file=args.stuff[2]
        label0_file=args.stuff[3]
        label1_file=args.stuff[4]
        output_dir=args.stuff[5]
        createh5file(image0_file,image1_file,label0_file,label1_file,output_dir=output_dir)
        command="echo successful at :: {} ::ventricle_mask_filename::  {} >> error.txt".format(inspect.stack()[0][3],image0_file)
        subprocess.call(command,shell=True)
        returnvalue=1
    except:
        command="echo failed at :: {} >> error.txt".format(inspect.stack()[0][3])
        subprocess.call(command,shell=True)
    return  returnvalue
    
def ventricle_boundingbox_zaxis(ventricle_mask_filename,outputfilename):
    try:
        ventricle_mask_filename_nib=nib.load(ventricle_mask_filename)
        ventricle_mask_filename_nib_fdata=ventricle_mask_filename_nib.get_fdata()
        ventricle_mask_filename_nib_fdata_copy=np.copy(ventricle_mask_filename_nib_fdata)*0
        # for each_slice_num_z in range(ventricle_mask_filename_nib_fdata.shape[2]):
        #     this_slice=ventricle_mask_filename_nib_fdata[:,:,each_slice_num_z]
        #     non_zero_slices_x=[]
        #     if np.sum(this_slice)>0:
        #         for each_slice_num in range(this_slice.shape[0]):
        #             if np.sum(this_slice[each_slice_num,:]) > 0 :
        #                 non_zero_slices_x.append(each_slice_num)
        #                 command="echo slice num at :: {} >> error.txt".format(each_slice_num)
        #                 subprocess.call(command,shell=True)
        #         non_zero_slices_x_np=np.array(non_zero_slices_x)
        #         print('non_zero_slices_np::{}'.format(non_zero_slices_x_np))
        #
        #         non_zero_slices_x_np_min=np.min(non_zero_slices_x_np)
        #         non_zero_slices_x_np_max=np.max(non_zero_slices_x_np)
        #
        #         non_zero_slices_y=[]
        #         for each_slice_num in range(this_slice.shape[1]):
        #             if np.sum(this_slice[:,each_slice_num]) > 0 :
        #                 non_zero_slices_y.append(each_slice_num)
        #                 command="echo slice num at :: {} >> error.txt".format(each_slice_num)
        #                 subprocess.call(command,shell=True)
        #         non_zero_slices_y_np=np.array(non_zero_slices_y)
        #         print('non_zero_slices_np::{}'.format(non_zero_slices_y_np))
        #
        #         non_zero_slices_y_np_min=np.min(non_zero_slices_y_np)
        #         non_zero_slices_y_np_max=np.max(non_zero_slices_y_np)
        #         ventricle_mask_filename_nib_fdata_copy[non_zero_slices_x_np_min:non_zero_slices_x_np_max,non_zero_slices_y_np_min:non_zero_slices_y_np_max,each_slice_num_z]=1
        #
                    
    ###########################################################################################################
        non_zero_slices=[]
        for each_slice_num in range(ventricle_mask_filename_nib_fdata.shape[2]):
            if np.sum(ventricle_mask_filename_nib_fdata[:,:,each_slice_num]) > 0 :
                non_zero_slices.append(each_slice_num)
                command="echo slice num at :: {} >> error.txt".format(each_slice_num)
                subprocess.call(command,shell=True)
        non_zero_slices_np=np.array(non_zero_slices)
        print('non_zero_slices_np::{}'.format(non_zero_slices_np))

        ventricle_lowest_slice_num=np.min(non_zero_slices_np)
        ventricle_highest_slice_num=np.max(non_zero_slices_np)
##################
        non_zero_slices_x=[]
        for each_slice_num in range(ventricle_mask_filename_nib_fdata.shape[0]):
            if np.sum(ventricle_mask_filename_nib_fdata[each_slice_num,:,:]) > -1000 :
                non_zero_slices_x.append(each_slice_num)
                command="echo slice num at :: {} >> error.txt".format(each_slice_num)
                subprocess.call(command,shell=True)
        non_zero_slices_x_np=np.array(non_zero_slices_x)
        print('non_zero_slices_x_np::{}'.format(non_zero_slices_x_np))

        ventricle_lowest_slice_num_x=np.min(non_zero_slices_x_np)
        ventricle_highest_slice_num_x=np.max(non_zero_slices_x_np)
#####################

##################
        non_zero_slices_y=[]
        for each_slice_num in range(ventricle_mask_filename_nib_fdata.shape[0]):
            if np.sum(ventricle_mask_filename_nib_fdata[:,each_slice_num,:]) > -1000 :
                non_zero_slices_y.append(each_slice_num)
                command="echo slice num at :: {} >> error.txt".format(each_slice_num)
                subprocess.call(command,shell=True)
        non_zero_slices_y_np=np.array(non_zero_slices_y)
        print('non_zero_slices_y_np::{}'.format(non_zero_slices_y_np))

        ventricle_lowest_slice_num_y=np.min(non_zero_slices_y_np)
        ventricle_highest_slice_num_y=np.max(non_zero_slices_y_np)
#####################
        ventricle_extent_vertical = pd.DataFrame(columns=['Lowest','Highest'])
        ventricle_extent_vertical.loc[0] = [ventricle_lowest_slice_num,ventricle_highest_slice_num]
        ventricle_extent_vertical.loc[1] = [ventricle_lowest_slice_num_x,ventricle_highest_slice_num_x]
        ventricle_extent_vertical.loc[2] = [ventricle_lowest_slice_num_y,ventricle_highest_slice_num_y]
#         ventricle_extent_vertical=pd.DataFrame(np.array([ventricle_lowest_slice_num,ventricle_highest_slice_num]))
#         ventricle_extent_vertical.columns=
        ventricle_extent_vertical.to_csv(outputfilename,index=False)
        command="echo successful at :: {} >> error.txt".format(inspect.stack()[0][3])
        subprocess.call(command,shell=True)
        # ventricle_mask_filename_nib_fdata_copy[ventricle_lowest_slice_num_x:ventricle_highest_slice_num_x,ventricle_lowest_slice_num_y:ventricle_highest_slice_num_y,ventricle_lowest_slice_num:ventricle_highest_slice_num]=1
        ventricle_mask_filename_nib_fdata_copy[:,:,ventricle_lowest_slice_num:ventricle_highest_slice_num]=1
        array_mask = nib.Nifti1Image(ventricle_mask_filename_nib_fdata_copy, affine=ventricle_mask_filename_nib.affine, header=ventricle_mask_filename_nib.header)
        mirror_image_mask_filename=outputfilename #ventricle_mask_filename.split('.nii')[0]+'_bounding_box.nii.gz'
        # niigzfilenametosave2=os.path.join(OUTPUT_DIRECTORY,os.path.basename(levelset_file)) #.split(".nii")[0]+"RESIZED.nii.gz")
        nib.save(array_mask, mirror_image_mask_filename)
        returnvalue=1
    except:
        command="echo failed at :: {} >> error.txt".format(inspect.stack()[0][3])
        subprocess.call(command,shell=True)
    # print(returnvalue)
    return  returnvalue

def call_ventricle_boundingbox_zaxis(args):
    returnvalue=0
    try:
        ventricle_mask_filename=args.stuff[1]
        outputfilename=args.stuff[2]
        ventricle_boundingbox_zaxis(ventricle_mask_filename,outputfilename)
        command="echo successful at :: {} ::ventricle_mask_filename::  {} >> error.txt".format(inspect.stack()[0][3],ventricle_mask_filename)
        subprocess.call(command,shell=True)
        returnvalue=1
    except:
        command="echo failed at :: {} >> error.txt".format(inspect.stack()[0][3])
        subprocess.call(command,shell=True)
    # print(returnvalue)
    return  returnvalue
def call_rotate_reverse_image(args):
    returnvalue=0
    try:
        niftifilename=args.stuff[1]
        originalfilename=args.stuff[2]
        npyfiledirectory=args.stuff[3]
        mirror_image_mask_filename=args.stuff[4]        
        rotate_reverse_image(niftifilename,originalfilename,npyfiledirectory,mirror_image_mask_filename)
        command="echo successful at :: {} ::ventricle_mask_filename::  {} >> error.txt".format(inspect.stack()[0][3],inspect.stack()[0][3])
        subprocess.call(command,shell=True)
        returnvalue=1
    except:
        command="echo failed at :: {} >> error.txt".format(inspect.stack()[0][3])
        subprocess.call(command,shell=True)
    # print(returnvalue)
    return  returnvalue
def rotate_reverse_image(niftifilename,originalfilename,npyfiledirectory,mirror_image_mask_filename): #niftifilename,npyfiledirectory,niftifilenamedir):
    returnvalue=0
    try:    
        grayfilename_base=os.path.basename(niftifilename) 
        grayfilename=niftifilename 
        npyfileextension="REGISMethodOriginalRF_midline.npy"
        niftifilename_nib=nib.load(niftifilename)
        filename_gray_data_np=resizeinto_512by512(niftifilename_nib.get_fdata()) 
        filename_gray_data_np_copy=np.copy(filename_gray_data_np)
        file_gray=niftifilename
#         filename_gray_data_np=contrast_stretch_np(filename_gray_data_np,1) 
        filename_gray_data_np_1=filename_gray_data_np* 255 ##contrast_stretch_np(resizeinto_512by512(nib.load(grayfilename).get_fdata()),1)*255 
        numpy_image=filename_gray_data_np*255
        numpy_image_mask=numpy_image
        output_mask_file_np=filename_gray_data_np *0

        
        for img_idx in range(numpy_image.shape[2]):
            if img_idx>0 and img_idx < numpy_image.shape[2]: # and  filename_gray_data_np_copy.shape==csf_seg_np.shape:
                method_name="REGIS"

                slice_number="{0:0=3d}".format(img_idx)
                filename_tosave=re.sub('[^a-zA-Z0-9 \n\_]', '', os.path.basename(originalfilename).split("_T_APPLIED")[0]+'_resaved_levelset')
                this_npyfile=os.path.join(npyfiledirectory,filename_tosave+method_name+"_"+str(slice_number)+  "_V2.npy")
                command="echo successful at :: {} ::this_npyfile::  {} >> error.txt".format(inspect.stack()[0][3],this_npyfile)
                subprocess.call(command,shell=True)
                if os.path.exists(this_npyfile):
                    command="echo successful at :: {} ::this_npyfile exists::  {} >> error.txt".format(inspect.stack()[0][3],this_npyfile)
                    subprocess.call(command,shell=True)
#                     array_mask = nib.Nifti1Image(output_mask_file_np, affine=niftifilename_nib.affine, header=niftifilename_nib.header)
#                     # niigzfilenametosave2=os.path.join(OUTPUT_DIRECTORY,os.path.basename(levelset_file)) #.split(".nii")[0]+"RESIZED.nii.gz")
#                     nib.save(array_mask, mirror_image_mask_filename)   
                    
                    calculated_midline_points=np.load(this_npyfile,allow_pickle=True)
                    x_points2=calculated_midline_points.item().get('x_axis') #,y_points2=points_on_line(extremepoints)
                    y_points2=calculated_midline_points.item().get('y_axis')
                    #                            slice_3_layer= np.zeros([numpy_image.shape[0],numpy_image.shape[1],3])
                    x_points2=x_points2[:,0]
                    y_points2=y_points2[:,0]

                    #################################################
                    ######################################################################
                    img_with_line_nonzero_id = np.transpose(np.nonzero(np.copy(numpy_image_mask[:,:,img_idx])))

                    lineThickness = 2
                    #                            lineThickness = 2
                    img_with_line=filename_gray_data_np_1[:,:,img_idx] #np.int8(numpy_image[:,:,img_idx])

                    v1=np.array([512,0]) ## point from the image
                    v2_1=np.array([x_points2[0],y_points2[0]]) ## point 1 from the midline
                    v2_2=np.array([x_points2[1],y_points2[1]]) ## point 2 from the midline
                    v2=v2_2-v2_1

                    angle=  angle_bet_two_vector(v1,v2)
                    angleRad=angle_bet_two_vectorRad(v1,v2)
                    ## translation:
                    points=np.array([[x_points2[0],y_points2[0]],[x_points2[511],y_points2[511]]])
                    mid_point_line=np.mean(points,axis=0)
                    # delta translation:
                    image_midpoint=np.array([int(filename_gray_data_np_1[:,:,img_idx].shape[0]/2),int(filename_gray_data_np_1[:,:,img_idx].shape[1]/2)]) #np.array([255,255])
                    translation_delta=image_midpoint-mid_point_line
#                     M = np.float32([[1,0,translation_delta[0]],[0,1,translation_delta[1]]])
#                     I_t_gray =cv2.warpAffine(np.copy(numpy_image[:,:,img_idx]),M,(filename_gray_data_np_1[:,:,img_idx].shape[0],filename_gray_data_np_1[:,:,img_idx].shape[1]), flags= cv2.INTER_NEAREST) 
#                     I_t_mask =cv2.warpAffine(np.copy(numpy_image_mask[:,:,img_idx]),M,(filename_gray_data_np_1[:,:,img_idx].shape[0],filename_gray_data_np_1[:,:,img_idx].shape[1]) , flags= cv2.INTER_NEAREST)

                    #########################################################################


                    translate_points= points+translation_delta
                    #                    show_slice_withaline(I_t_mask,translate_points)
                    points=translate_points
                    ## translation matrix
                    p1x,p1y= rotate_around_point_highperf(np.array([points[0][0],points[0][1]]), angleRad, origin=(255,255))
                    p2x,p2y= rotate_around_point_highperf(np.array([points[1][0],points[1][1]]), angleRad, origin=(255,255))
                    points1=np.array([[p1x,p1y],[p2x,p2y]])

#                     I_t_r_gray=rotate_image(I_t_gray,(255,255),angle)
#                     I_t_r_mask=rotate_image(I_t_mask,(255,255),angle)
                    I_t_r_f_gray=filename_gray_data_np_1[:,:,img_idx] #cv2.flip(I_t_r_gray,0)
#                     I_t_r_f_mask=cv2.flip(I_t_r_mask,0)
                    I_t_r_f_rinv_gray=rotate_image(I_t_r_f_gray,(255,255),-angle)
#                     I_t_r_f_rinv_mask=rotate_image(I_t_r_f_mask,(255,255),-angle)
                    p1x,p1y= rotate_around_point_highperf(np.array([points1[0][0],points1[0][1]]), -angleRad, origin=(255,255))
                    p2x,p2y= rotate_around_point_highperf(np.array([points1[1][0],points1[1][1]]), -angleRad, origin=(255,255))
                    points1=np.array([[p1x,p1y],[p2x,p2y]])
                    M = np.float32([[1,0,-translation_delta[0]],[0,1,-translation_delta[1]]])
                    I_t_r_f_rinv_tinv_gray = cv2.warpAffine(I_t_r_f_rinv_gray,M,(512,512) , flags= cv2.INTER_NEAREST)
#                     I_t_r_f_rinv_tinv_mask = cv2.warpAffine(I_t_r_f_rinv_mask,M,(512,512), flags= cv2.INTER_NEAREST )
                    output_mask_file_np[:,:,img_idx]=I_t_r_f_rinv_tinv_gray #I_t_r_f_rinv_tinv_mask
#                     output_mask_file_np[:,:,img_idx][output_mask_file_np[:,:,img_idx]>0]=1
#                     output_mask_file_np[:,:,img_idx][output_mask_file_np[:,:,img_idx]<1]=0

        array_mask = nib.Nifti1Image(output_mask_file_np, affine=niftifilename_nib.affine, header=niftifilename_nib.header)
        # niigzfilenametosave2=os.path.join(OUTPUT_DIRECTORY,os.path.basename(levelset_file)) #.split(".nii")[0]+"RESIZED.nii.gz")
        nib.save(array_mask, mirror_image_mask_filename)
        command="echo successful at :: {} ::ventricle_mask_filename::  {} >> error.txt".format(inspect.stack()[0][3],inspect.stack()[0][3])
        subprocess.call(command,shell=True)

        returnvalue=1
    except:
        command="echo failed at :: {} >> error.txt".format(inspect.stack()[0][3])
        subprocess.call(command,shell=True)
    return  returnvalue    


def first_rotation_image(niftifilename,npyfiledirectory,mirror_image_mask_filename,csffile_complete): #niftifilename,npyfiledirectory,niftifilenamedir):
    returnvalue=0
    try:    
        grayfilename_base=os.path.basename(niftifilename) 
        grayfilename=niftifilename 
        npyfileextension="REGISMethodOriginalRF_midline.npy"
        csffile_complete_nib=nib.load(csffile_complete)
        niftifilename_nib=nib.load(niftifilename)
        filename_gray_data_np=resizeinto_512by512(niftifilename_nib.get_fdata()) 
        filename_gray_data_np_copy=np.copy(filename_gray_data_np)
        file_gray=niftifilename
#         filename_gray_data_np=contrast_stretch_np(filename_gray_data_np,1) 
        filename_gray_data_np_1=filename_gray_data_np* 255 ##contrast_stretch_np(resizeinto_512by512(nib.load(grayfilename).get_fdata()),1)*255 
        numpy_image=filename_gray_data_np*255
        numpy_image_mask=numpy_image
        output_mask_file_np=filename_gray_data_np *0

        
        for img_idx in range(numpy_image.shape[2]):
            if img_idx>0 and img_idx < numpy_image.shape[2]: # and  filename_gray_data_np_copy.shape==csf_seg_np.shape:
                method_name="REGIS"

                slice_number="{0:0=3d}".format(img_idx)
                filename_tosave=re.sub('[^a-zA-Z0-9 \n\_]', '', os.path.basename(niftifilename).split("_T_APPLIED")[0]+'_resaved_levelset')
                this_npyfile=os.path.join(npyfiledirectory,filename_tosave+method_name+"_"+str(slice_number)+  "_V2.npy")
                command="echo successful at :: {} ::this_npyfile::  {} >> error.txt".format(inspect.stack()[0][3],this_npyfile)
                subprocess.call(command,shell=True)
                if os.path.exists(this_npyfile):
                    command="echo successful at :: {} ::this_npyfile exists::  {} >> error.txt".format(inspect.stack()[0][3],this_npyfile)
                    subprocess.call(command,shell=True)
#                     array_mask = nib.Nifti1Image(output_mask_file_np, affine=niftifilename_nib.affine, header=niftifilename_nib.header)
#                     # niigzfilenametosave2=os.path.join(OUTPUT_DIRECTORY,os.path.basename(levelset_file)) #.split(".nii")[0]+"RESIZED.nii.gz")
#                     nib.save(array_mask, mirror_image_mask_filename)   
                    
                    calculated_midline_points=np.load(this_npyfile,allow_pickle=True)
                    x_points2=calculated_midline_points.item().get('x_axis') #,y_points2=points_on_line(extremepoints)
                    y_points2=calculated_midline_points.item().get('y_axis')
                    #                            slice_3_layer= np.zeros([numpy_image.shape[0],numpy_image.shape[1],3])
                    x_points2=x_points2[:,0]
                    y_points2=y_points2[:,0]

                    #################################################
                    ######################################################################
                    img_with_line_nonzero_id = np.transpose(np.nonzero(np.copy(numpy_image_mask[:,:,img_idx])))

                    lineThickness = 2
                    #                            lineThickness = 2
                    img_with_line=filename_gray_data_np_1[:,:,img_idx] #np.int8(numpy_image[:,:,img_idx])

                    v1=np.array([512,0]) ## point from the image
                    v2_1=np.array([x_points2[0],y_points2[0]]) ## point 1 from the midline
                    v2_2=np.array([x_points2[1],y_points2[1]]) ## point 2 from the midline
                    v2=v2_2-v2_1

                    angle=  angle_bet_two_vector(v1,v2)
                    angleRad=angle_bet_two_vectorRad(v1,v2)
                    ## translation:
                    points=np.array([[x_points2[0],y_points2[0]],[x_points2[511],y_points2[511]]])
                    mid_point_line=np.mean(points,axis=0)
                    # delta translation:
                    image_midpoint=np.array([int(filename_gray_data_np_1[:,:,img_idx].shape[0]/2),int(filename_gray_data_np_1[:,:,img_idx].shape[1]/2)]) #np.array([255,255])
                    translation_delta=image_midpoint-mid_point_line
                    M = np.float32([[1,0,translation_delta[0]],[0,1,translation_delta[1]]])
                    I_t_gray =cv2.warpAffine(np.copy(numpy_image[:,:,img_idx]),M,(filename_gray_data_np_1[:,:,img_idx].shape[0],filename_gray_data_np_1[:,:,img_idx].shape[1]), flags= cv2.INTER_NEAREST) 
                    I_t_mask =cv2.warpAffine(np.copy(numpy_image_mask[:,:,img_idx]),M,(filename_gray_data_np_1[:,:,img_idx].shape[0],filename_gray_data_np_1[:,:,img_idx].shape[1]) , flags= cv2.INTER_NEAREST)

                    #########################################################################


                    translate_points= points+translation_delta
                    #                    show_slice_withaline(I_t_mask,translate_points)
                    points=translate_points
                    ## translation matrix
                    p1x,p1y= rotate_around_point_highperf(np.array([points[0][0],points[0][1]]), angleRad, origin=(255,255))
                    p2x,p2y= rotate_around_point_highperf(np.array([points[1][0],points[1][1]]), angleRad, origin=(255,255))
                    points1=np.array([[p1x,p1y],[p2x,p2y]])

                    I_t_r_gray=rotate_image(I_t_gray,(255,255),angle)
                    I_t_r_mask=rotate_image(I_t_mask,(255,255),angle)
#                     I_t_r_f_gray=cv2.flip(I_t_r_gray,0)
#                     I_t_r_f_mask=cv2.flip(I_t_r_mask,0)
#                     I_t_r_f_rinv_gray=rotate_image(I_t_r_f_gray,(255,255),-angle)
#                     I_t_r_f_rinv_mask=rotate_image(I_t_r_f_mask,(255,255),-angle)
#                     p1x,p1y= rotate_around_point_highperf(np.array([points1[0][0],points1[0][1]]), -angleRad, origin=(255,255))
#                     p2x,p2y= rotate_around_point_highperf(np.array([points1[1][0],points1[1][1]]), -angleRad, origin=(255,255))
#                     points1=np.array([[p1x,p1y],[p2x,p2y]])
#                     M = np.float32([[1,0,-translation_delta[0]],[0,1,-translation_delta[1]]])
#                     I_t_r_f_rinv_tinv_gray = cv2.warpAffine(I_t_r_f_rinv_gray,M,(512,512) , flags= cv2.INTER_NEAREST)
#                     I_t_r_f_rinv_tinv_mask = cv2.warpAffine(I_t_r_f_rinv_mask,M,(512,512), flags= cv2.INTER_NEAREST )
                    output_mask_file_np[:,:,img_idx]=I_t_r_gray #I_t_r_f_rinv_tinv_mask
#                     output_mask_file_np[:,:,img_idx][output_mask_file_np[:,:,img_idx]>0]=1
#                     output_mask_file_np[:,:,img_idx][output_mask_file_np[:,:,img_idx]<1]=0

        # array_mask = nib.Nifti1Image(output_mask_file_np, affine=niftifilename_nib.affine, header=niftifilename_nib.header)
        array_mask = nib.Nifti1Image(output_mask_file_np, affine=csffile_complete_nib.affine, header=csffile_complete_nib.header)

        # niigzfilenametosave2=os.path.join(OUTPUT_DIRECTORY,os.path.basename(levelset_file)) #.split(".nii")[0]+"RESIZED.nii.gz")
        nib.save(array_mask, mirror_image_mask_filename)
        command="echo successful at :: {} ::ventricle_mask_filename::  {} >> error.txt".format(inspect.stack()[0][3],inspect.stack()[0][3])
        subprocess.call(command,shell=True)
#         ventricle_boundingbox_zaxis(mirror_image_mask_filename,mirror_image_mask_filename.split(".nii")[0]+"_extent_reverse_rot_n_t.csv")
#         originalfilename=niftifilename
#         rotate_reverse_image(mirror_image_mask_filename.split('.nii')[0]+'_bounding_box.nii.gz',originalfilename,npyfiledirectory,mirror_image_mask_filename.split('nii')[0]+'_bounding_box_inv_r_t.nii.gz')
#         ventricle_boundingbox_zaxis(mirror_image_mask_filename,mirror_image_mask_filename.split(".nii")[0]+"_extent_reverse_rot_n_t.csv")
        returnvalue=1
    except:
        command="echo failed at :: {} >> error.txt".format(inspect.stack()[0][3])
        subprocess.call(command,shell=True)
    return  returnvalue    
def copy_im_parameter_to_a_matrix_nifti(input_matrix_file,niftifilename,output_nifti_filename):
    niftifilename_nib=nib.load(niftifilename)
    input_matrix_file_np=nib.load(input_matrix_file).get_fdata()
    array_mask = nib.Nifti1Image(input_matrix_file_np, affine=niftifilename_nib.affine, header=niftifilename_nib.header)
    # niigzfilenametosave2=os.path.join(OUTPUT_DIRECTORY,os.path.basename(levelset_file)) #.split(".nii")[0]+"RESIZED.nii.gz")
    nib.save(array_mask, output_nifti_filename)    

def call_copy_im_parameter_to_a_matrix_nifti(args):
    returnvalue=0
    try:
        input_matrix_file=args.stuff[1]
        niftifilename=args.stuff[2]
        output_nifti_filename=args.stuff[3]
        copy_im_parameter_to_a_matrix_nifti(input_matrix_file,niftifilename,output_nifti_filename)
        command="echo successful at :: {} ::ventricle_mask_filename::  {} >> error.txt".format(inspect.stack()[0][3],inspect.stack()[0][3])
        subprocess.call(command,shell=True)
        returnvalue=1
    except:
        command="echo failed at :: {} >> error.txt".format(inspect.stack()[0][3])
        subprocess.call(command,shell=True)
    return  returnvalue

def call_first_rotation_image(args):
    returnvalue=0
    try:
        niftifilename=args.stuff[1]
        npyfiledirectory=args.stuff[2]
        mirror_image_mask_filename=args.stuff[3]
        csffile_complete=args.stuff[4]
        first_rotation_image(niftifilename,npyfiledirectory,mirror_image_mask_filename,csffile_complete)
        command="echo successful at :: {} ::ventricle_mask_filename::  {} >> error.txt".format(inspect.stack()[0][3],inspect.stack()[0][3])
        subprocess.call(command,shell=True)
        returnvalue=1
    except:
        command="echo failed at :: {} >> error.txt".format(inspect.stack()[0][3])
        subprocess.call(command,shell=True)
    return  returnvalue
def vertical_extent_ventricle(args):
    returnvalue=0
    try:
        niftifilename=args.stuff[1]
        npyfiledirectory=args.stuff[2]
        mirror_image_mask_filename=args.stuff[3]
        csffile_complete=args.stuff[4]
        first_rotation_image(niftifilename,npyfiledirectory,mirror_image_mask_filename,csffile_complete)
        command="echo successful at :: {} ::ventricle_mask_filename::  {} >> error.txt".format(inspect.stack()[0][3],inspect.stack()[0][3])
        subprocess.call(command,shell=True)
        returnvalue=1
    except:
        command="echo failed at :: {} >> error.txt".format(inspect.stack()[0][3])
        subprocess.call(command,shell=True)
    return  returnvalue
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('stuff', nargs='+')
    args = parser.parse_args()
    name_of_the_function=args.stuff[0]
    return_value=0
    if name_of_the_function == "call_ventricle_boundingbox_zaxis":
        return_value=call_ventricle_boundingbox_zaxis(args) 
    if name_of_the_function == "call_createh5file": 
        return_value=call_createh5file(args)        
    if name_of_the_function == "call_gray2binary": 
        return_value=call_gray2binary(args)        
    if name_of_the_function == "call_first_rotation_image": 
        return_value=call_first_rotation_image(args)    
    if name_of_the_function == "call_copy_im_parameter_to_a_matrix_nifti": 
        return_value=call_copy_im_parameter_to_a_matrix_nifti(args)   
    if name_of_the_function == "call_rotate_reverse_image": 
        return_value=call_rotate_reverse_image(args)        
    return return_value
if __name__ == '__main__':
    main()

