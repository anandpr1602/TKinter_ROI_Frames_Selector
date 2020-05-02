# ROI Rectangle & Frames Selector
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

# Usage:
## Run the ROI_Frames_Selector.py directly:
* On the command line or in a Python console run:

`python ROI_Frames_Selector.py` or `ROI_Frames_Selector.py`

## Call the ROI_Frames_Selector.py from a different Python file:
* In your Python file, include:

`import ROI_Frames_Selector` (**NB:** the `ROI_Frames_Selector.py` and the `ROI_Frames_Selector.cfg` must be in the same working directoy as your Python file.)

* Then call the `VideoBrowser` class directly:

`ROI_Frames_Selector.VideoBrowser(tkinter.Tk(), '<path>', ROI_Shape)`

* To get the selected frames and ROIs returned to `<my_var>`:

`<my_var> = ROI_Frames_Selector.VideoBrowser(tkinter.Tk(), '<path>', ROI_Shape).results()`

* The `<path>` can be that of single file (image or video), or a directory. **NB if directory:** All files in the directory will be considered as a sequence of frames of a single dataset. Remove unwanted files from that directory before opening.

* `ROI_Shape` is an integer that defines the shape of the ROI to be drawn on the frames. Choose between 0 for a rectangle (default) and 1 for a circle.

### Output:
* For multi-frame datasets:

`<my_var> = (First frame of interest, Last frame of interest, X1, Y1, X2, Y2)`

* For single-frame images:

`<my_var> = (X1, Y1, X2, Y2)`

* If `ROI_Shape = 0`: (X1, Y1, X2, Y2) will be the coordinates of the ROI rectangle; else if `ROI_Shape = 1`: they will be the coordinates of the bounding box of the ROI circle. If ROI not chosen, they will be `None`.
