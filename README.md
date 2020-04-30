# TKinter_ROI_Frames_Selector
Tkinter GUI to select ROI and set of frames for further Image Analysis on Python. Requires Tkinter, Numpy, PIL, ImageIO.  Install imageio-ffmpeg, ITK packages for opening a wide range of image datasets including movies, HDF, etc.


# To see the selected Frames and ROIs printed on the screen.
IN: ROI_Frames_Selector.VideoBrowser(<path_to_my_video>)

# To get the selected Frames and ROIs returned to <my_var>.
IN: <my_var> = ROI_Frames_Selector.VideoBrowser(<path_to_my_video>).results() 
IN: <my_var>

# For multi-frame datasets.
OUT: (First frame of interest, Lastframe of interest, ROI_X1, ROI_Y1, ROI_X2, ROI_Y2)
# For single-frame images.
OUT: (ROI_X1, ROI_Y1, ROI_X2, ROI_Y2)
