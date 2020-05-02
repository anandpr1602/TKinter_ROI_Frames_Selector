# ROI Frames Selector
is a Tkinter-based GUI to select rectangular ROI and choose a set of frames for further image inalysis on Python. 

# Requirements:
## Tkinter:
### From Python 3.1 - Tkinter is included with all standard Python distribution.
### For Python 3.x use:
`import tkinter.Tk()` and NOT `import Tkinter.Tk()`

## Numpy:
`pip install numpy` or `python -m pip install numpy`

## PIL:
`pip install Pillow` or `python -m pip install Pillow`

## ImageIO:
`pip install imageio` or `python -m pip install imageio`
* For compatible file formats: see https://imageio.readthedocs.io/en/stable/formats.html or use `imageio.formats.show()`

## Use the FFMPEG plugin to open a variety of video formats:
`pip install imageio-ffmpeg` or
`python -m pip install imageio-ffmpeg`
* See https://imageio.readthedocs.io/en/stable/format_ffmpeg.html#ffmpeg

## Use the FreeImage plugin to open a variety of image formats such as .RAW, .HDR, etc.:
On Python `imageio.plugins.freeimage.download()` or on command line `imageio_download_bin freeimage`
* See http://freeimage.sourceforge.net/

## Use the ITK plugin to open a variety of image formats such as .HDF5, .HDR, .NHDR, etc.:
`pip install itk` or `python -m pip install itk`
* See https://imageio.readthedocs.io/en/stable/format_ffmpeg.html#ffmpeg

# Example Usage:
## Run the ROI_Frames_Selector.py directly:
* On the command line or in a Python console run:

`python ROI_Frames_Selector.py` or `ROI_Frames_Selector.py`

## Call the ROI_Frames_Selector.py from a different Python file:
* In your Python file, include:

`import ROI_Frames_Selector` (**NB:** the ROI_Frames_Selector.py must be in the same working directoy as your Python file.)

* Then call the `VideoBrowser` class directly:

`ROI_Frames_Selector.VideoBrowser('<path_to_my_video>')`

* To get the selected frames and ROIs returned to `<my_var>`:

`<my_var> = ROI_Frames_Selector.VideoBrowser('<path_to_my_video>').results()`

### Outputs:
* For multi-frame datasets:

`<my_var> = (First frame of interest, Last frame of interest, X1, Y1, X2, Y2)`

* For single-frame images:

`<my_var> = (X1, Y1, X2, Y2)`

* X1, Y1, X2, Y2 are the coordinates of the ROI Rectangle.
