# ROI & Frames Selector
is a Tkinter-based GUI that loads a variety of multimedia files (or a directory with individual image) and lets the user select a rectangular or a circular region of interest (ROI) and choose the frames of interest for further image inalysis on Python. 

* **NB: This version can open 16-bit images, but this will be downscaled to 8-bit to be PIL-compatible. This is however, slow in the current version.**

# Requirements:
## Tkinter:
### From Python 3.1 - Tkinter is included with all standard Python distribution.
### For Python 3.x use:
`import tkinter.Tk()` and NOT `import Tkinter.Tk()`

## Numpy:
`pip install numpy` or `python -m pip install numpy`

## PIL:
`pip install Pillow` or `python -m pip install Pillow`

## Scikit-Image:
`pip install scikit-image` or `python -m pip install scikit-image`

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
* See https://imageio.readthedocs.io/en/stable/format_itk.html#itk

# Usage:
## Run the ROI_Frames_Selector.py directly:
* On the command line or in a Python console run:

`python ROI_Frames_Selector.py` or `ROI_Frames_Selector.py`

## Call the ROI_Frames_Selector.py from a different Python file:
* In your Python file, include:

`import ROI_Frames_Selector` and `import tkinter` (**NB:** the `ROI_Frames_Selector.py` and the `ROI_Frames_Selector.cfg` must be in the same working directory as your Python file.)

### 1. If the path to the `<multimedia>` file/folder is already known:

* Call the `VideoBrowser` class directly:

`ROI_Frames_Selector.VideoBrowser(tkinter.Tk(), '<multimedia>', ROIshape=0)`

* **OR** To get the selected frames of interest and ROI coordinates returned to `<my_var>`:

`<my_var> = ROI_Frames_Selector.VideoBrowser(tkinter.Tk(), '<multimedia>', ROIshape=0).results()`

### 2. To select a `<multimedia>` file/folder using a file dialog box:

* Call the `FileSelector` class directly:

`ROI_Frames_Selector.FileSelector(tkinter.Tk())`

* **OR** To get the selected frames of interest and ROI coordinates returned to `<my_var>`:

`<my_var> = ROI_Frames_Selector.FileSelector(tkinter.Tk()).results()`

* `<multimedia>` can be a path to a single file (image or video), or a directory. **NB if path to a directory:** All files in the directory will be considered as a sequence of frames of a single dataset. Remove unwanted files from that directory before opening.

* `ROIshape` is an integer that defines the shape of the ROI to be drawn on the frames. Choose between 0 for a rectangle (default) and 1 for a circle.

### Output:
* For multi-frame datasets:

`<my_var> = (<First frame of interest>, <Last frame of interest>, <X1>, <Y1>, <X2>, <Y2>, <haserror>)`

* For single-frame images:

`<my_var> = (<X1>, <Y1>, <X2>, <Y2>, <haserror>)`

* If `ROIshape = 0`: `(<X1>, <Y1>, <X2>, <Y2>)` are the coordinates of the ROI rectangle; else if `ROIshape = 1`: they are the coordinates of the bounding box of the ROI circle. If ROI not chosen, `None` is returned.

* `<First frame of interest>` and `<Last frame of interest>` (int), if chosen, are the indices of the frames of interest to be analysed, else `None` is returned.

* `<haserror>` (True or False) returns whether the execution of ROI_Frames_Selector file resulted in any errors. This is useful for managing and handling errors when called from a different Python file.
