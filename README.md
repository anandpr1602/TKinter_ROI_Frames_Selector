# ROI Frames Selector
is a Tkinter-based GUI to select rectangular ROI and choose a set of frames for further image inalysis on Python. 

# Requirements:
## Tkinter:
### From Python 3.1 - Tkinter is included with all standard Python distribution.
### NB: for Python 3.x use:
'<import tkinter.Tk()>' and NOT '<import Tkinter.Tk()>'

## Numpy:
'<pip install numpy>' or
'<python -m pip install numpy>'

## PIL:
'<pip install Pillow>' or
'<python -m pip install Pillow>'

## ImageIO:
'<pip install imageio>' or
'<python -m pip install imageio>'
For file formats: see https://imageio.readthedocs.io/en/stable/formats.html or
use '<imageio.formats.show()>'

## Use the FFMPEG plugin to open a variety of video formats:
'<pip install imageio-ffmpeg>' or
'<python -m pip install imageio-ffmpeg>'
See https://imageio.readthedocs.io/en/stable/format_ffmpeg.html#ffmpeg

## Use the FreeImage plugin to open a variety of image formats such as .RAW, .HDR, etc.:
On Python '<imageio.plugins.freeimage.download()>' or
On Command line '<imageio_download_bin freeimage>'
See http://freeimage.sourceforge.net/

## Use the ITK plugin to open a variety of image formats such as .HDF5, .HDR, .NHDR, etc.:
'<pip install itk>' or
'<python -m pip install itk>'
See https://imageio.readthedocs.io/en/stable/format_ffmpeg.html#ffmpeg

# Example Usage:

## Run the ROI_Frames_Selector.py directly:
On the command line or a Python console run:
'<ROI_Frames_Selector.VideoBrowser(<path_to_my_video>)>'

# To get the selected frames and ROIs returned to <my_var>
IN: <my_var> = ROI_Frames_Selector.VideoBrowser(<path_to_my_video>).results()

# For multi-frame datasets
IN: <my_var>
OUT: (First frame of interest, Lastframe of interest, ROI_X1, ROI_Y1, ROI_X2, ROI_Y2)

# For single-frame images
IN: <my_var>
OUT: (ROI_X1, ROI_Y1, ROI_X2, ROI_Y2)
