# ROI Frames Selector
is a Tkinter-based GUI to select rectangular ROI and choose a set of frames for further image inalysis on Python. 

# Requirements:
"""Tkinter:
  From Python 3.1 - Tkinter is included with all standard Python distribution.
  NB: for Python 3.x use""" 
  import tkinter.Tk() "and NOT" import Tkinter.Tk()

"""Numpy:"""
pip install numpy #or
python -m pip install numpy

"""PIL:"""
pip install Pillow #or
python -m pip install Pillow

"""ImageIO:"""
pip install imageio #or
python -m pip install imageio

""" To open videos ImageIO needs the FFMPEG plugin:"""
pip install imageio-ffmpeg




 Install imageio-ffmpeg, ITK packages for opening a wide range of image datasets including movies, HDF, etc. See - https://imageio.readthedocs.io/en/stable/formats.html

# To see the selected frames and ROIs printed on the screen
IN: ROI_Frames_Selector.VideoBrowser(<path_to_my_video>)

# To get the selected frames and ROIs returned to <my_var>
IN: <my_var> = ROI_Frames_Selector.VideoBrowser(<path_to_my_video>).results()

# For multi-frame datasets
IN: <my_var>
OUT: (First frame of interest, Lastframe of interest, ROI_X1, ROI_Y1, ROI_X2, ROI_Y2)

# For single-frame images
IN: <my_var>
OUT: (ROI_X1, ROI_Y1, ROI_X2, ROI_Y2)
