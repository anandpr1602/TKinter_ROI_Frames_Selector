# ROI Frames Selector
is a Tkinter-based GUI to select rectangular ROI and choose a set of frames for further image inalysis on Python. 

Requires Tkinter, Numpy, PIL, ImageIO. Install imageio-ffmpeg, ITK packages for opening a wide range of image datasets including movies, HDF, etc.

# To see the selected frames and ROIs printed on the screen.
IN: ROI_Frames_Selector.VideoBrowser(<path_to_my_video>)

# To get the selected frames and ROIs returned to <my_var>.
IN: <my_var> = ROI_Frames_Selector.VideoBrowser(<path_to_my_video>).results()

# For multi-frame datasets.
IN: <my_var>
OUT: (First frame of interest, Lastframe of interest, ROI_X1, ROI_Y1, ROI_X2, ROI_Y2)

# For single-frame images.
IN: <my_var>
OUT: (ROI_X1, ROI_Y1, ROI_X2, ROI_Y2)
