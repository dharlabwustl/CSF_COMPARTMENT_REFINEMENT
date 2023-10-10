def mask_mirror_image(niftifilename,npyfiledirectory,mirror_image_mask_filename): #niftifilename,npyfiledirectory,niftifilenamedir):
    grayfilename_base=os.path.basename(niftifilename) 
    grayfilename=niftifilename 
    npyfileextension="REGISMethodOriginalRF_midline.npy"
    niftifilename_nib=nib.load(niftifilename)
    filename_gray_data_np=resizeinto_512by512(niftifilename_nib.get_fdata()) 
    filename_gray_data_np_copy=np.copy(filename_gray_data_np)
    file_gray=niftifilename
    filename_gray_data_np=contrast_stretch_np(filename_gray_data_np,1) 
    filename_gray_data_np_1=contrast_stretch_np(resizeinto_512by512(nib.load(grayfilename).get_fdata()),1)*255 
    numpy_image=normalizeimage0to1(filename_gray_data_np)*255
    output_mask_file_np=filename_gray_data_np*0
    for img_idx in range(numpy_image.shape[2]):
        if img_idx>0 and img_idx < numpy_image.shape[2] and  filename_gray_data_np_copy.shape==csf_seg_np.shape:
            method_name="REGIS"

            slice_number="{0:0=3d}".format(img_idx)
            filename_tosave=re.sub('[^a-zA-Z0-9 \n\_]', '', os.path.basename(niftifilename).split(".nii")[0])
            this_npyfile=os.path.join(npyfiledirectory,filename_tosave+method_name+str(slice_number)+  ".npy")

            if os.path.exists(this_npyfile):
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
                I_t_r_f_gray=cv2.flip(I_t_r_gray,0)
                I_t_r_f_mask=cv2.flip(I_t_r_mask,0)
                I_t_r_f_rinv_gray=rotate_image(I_t_r_f_gray,(255,255),-angle)
                I_t_r_f_rinv_mask=rotate_image(I_t_r_f_mask,(255,255),-angle)
                p1x,p1y= rotate_around_point_highperf(np.array([points1[0][0],points1[0][1]]), -angleRad, origin=(255,255))
                p2x,p2y= rotate_around_point_highperf(np.array([points1[1][0],points1[1][1]]), -angleRad, origin=(255,255))
                points1=np.array([[p1x,p1y],[p2x,p2y]])
                M = np.float32([[1,0,-translation_delta[0]],[0,1,-translation_delta[1]]])
                I_t_r_f_rinv_tinv_gray = cv2.warpAffine(I_t_r_f_rinv_gray,M,(512,512) , flags= cv2.INTER_NEAREST)
                I_t_r_f_rinv_tinv_mask = cv2.warpAffine(I_t_r_f_rinv_mask,M,(512,512), flags= cv2.INTER_NEAREST )
                output_mask_file_np[:,:,img_idx]=I_t_r_f_rinv_tinv_mask
                output_mask_file_np[:,:,img_idx][output_mask_file_np[:,:,img_idx]>0]=1
                output_mask_file_np[:,:,img_idx][output_mask_file_np[:,:,img_idx]<1]=0
    
    array_mask = nib.Nifti1Image(output_mask_file_np, affine=niftifilename_nib.affine, header=niftifilename_nib.header)
    # niigzfilenametosave2=os.path.join(OUTPUT_DIRECTORY,os.path.basename(levelset_file)) #.split(".nii")[0]+"RESIZED.nii.gz")
    nib.save(array_mask, mirror_image_mask_filename)

def call_mask_mirror_image():
    returnvalue=0
    try:
        niftifilename=args.stuff[1]
        npyfiledirectory=args.stuff[2]
        mirror_image_mask_filename=args.stuff[3]
        mask_mirror_image(niftifilename,npyfiledirectory,mirror_image_mask_filename)
        command="echo successful at :: {} ::ventricle_mask_filename::  {} >> error.txt".format(inspect.stack()[0][3],inspect.stack()[0][3])
        subprocess.call(command,shell=True)
        returnvalue=1
    except:
        command="echo failed at :: {} >> error.txt".format(inspect.stack()[0][3])
        subprocess.call(command,shell=True)
    return  returnvalue