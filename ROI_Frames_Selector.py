# -*- coding: utf-8 -*-
"""
Created in April 2020 for UCL EIL

@author: Anand Pallipurath
"""
import os, re
import configparser
import numpy as np
import skimage.util as util
import tkinter
import tkinter.font as font
import tkinter.filedialog as filedialog
import imageio
import PIL.Image, PIL.ImageTk

#  Load the configuration file
ConfigParser = configparser.ConfigParser()
ConfigParser.read('ROI_Frames_Selector.cfg')
#  Load FFMPEG file extensions from settings
FFMPEGFileExtensions = ConfigParser.get("SETTINGS", "FFMPEGFileExtensions")
# Load list of single image filetypes from settings
ImageFileExtensions = ConfigParser.get("SETTINGS", "ImageFileExtensions")

class VideoBrowser:
    def __init__(self, window, multimedia=None, ROIshape=0):
        # Create a window and build the Application objects
        self.haserror = False
        self.window = window
        self.multimedia = multimedia
        if int(ROIshape) != 0 and int(ROIshape) != 1:
            self.window.destroy()
            self.haserror = True
            raise ValueError("\n\nROIshape must be 0 for rectangle and 1 for circle. \n")
        else:
            self.ROIshape = int(ROIshape)
        self.window.title(self.multimedia)
        self.resolution = 600 # Giving a decent resolution to resize large images to fit a screen
        self.delay = 16 # set the delay in milliseconds to refresh the Tkinter window.
        # Create an empty canvas. This creates a separate Tkinter.Tk() object. 'highlightthickness' = 0 is important when dealing with extracting XY coordinates of images through mouse events.
        # Without highlightthickness, canvas is larger than the image --> leading to mouse picking out of bounds XY coordinates.
        self.mycanvas = tkinter.Canvas(self.window, width = self.resolution, height = self.resolution, highlightthickness=0)         
        self.largefont = font.Font(family="Verdana", size=10, weight=font.BOLD)
        self.mediumfont = font.Font(family="Verdana", size=10, weight=font.BOLD, slant=font.ITALIC)
        self.specialfont = font.Font(family="Helvetica", size=10, weight=font.BOLD, slant=font.ITALIC)
        self.index = 0 # Open every dataset at the first frame.
        self.first_frame = None
        self.last_frame = None
        self.x = None
        self.y = None
        self.rect = None
        self.start_x = None
        self.start_y = None
        self.curX = None
        self.curY = None
        self.resize = False
        self.ROIrect = False
        self.filelist = []
        
        # If a single file is selected: use the imageio.getreader() option and check for FFMPEG compatibility.
        if os.path.isfile(multimedia) == True:
            #  Get filename file_extension
            self.file_extension = (os.path.splitext(multimedia)[1])
            self.image_set = imageio.get_reader(multimedia, mode = '?') #image_set is a reader object with the list of images. This loads the entire file onto memory.
    
            #  Check if the imported file is a FFMPEG or some other type
            self.isFFMPEG = self.file_extension in FFMPEGFileExtensions
            #  Calculate the number of frames in the file. count_frames() is used for videos otherwise get_length() is used.
            #  When reading from a video, the number of available frames is hard/expensive to calculate, which is why its
            #  set to inf by default, indicating “stream mode”. To get the number of frames before having read them all, you
            #  can use the reader.count_frames() method.
            #  See: https://imageio.readthedocs.io/en/stable/format_ffmpeg.html#ffmpeg
            self.number_frames = self.image_set.count_frames() if self.isFFMPEG else self.image_set.get_length()
            # Create frame and photo here, only to get the aspect ratio of the photo based on which the canvas will be built.
            self.frame = self.image_set.get_data(self.index) #get_data opens each frame as an image array
            
            # Downscale 16-bit images to 8-bit, as PIL.Image cannot open/handle 16-bit images.
            if self.frame.dtype == "uint16":
                self.frame = util.img_as_ubyte(self.frame)

        elif os.path.isdir(multimedia) == True: # Else if a directory of image sequence is selected: use the imageio.imread() option to open frames.
            for file in os.listdir(multimedia):
                self.file_extension = (os.path.splitext(file)[1])
                #  Check if the imported file is a compatible single image
                self.isSingleImage = self.file_extension in ImageFileExtensions
                if self.isSingleImage == True and self.file_extension != "":
                    self.filelist.append(os.path.join(multimedia, file))
            if self.filelist != []:
                self.filelist = self.sorted_alphanumeric(self.filelist)
                self.number_frames = len(self.filelist)
                self.frame = imageio.imread(self.filelist[self.index]) #open each image from directory
                if self.frame.dtype == "uint16":
                    self.frame = util.img_as_ubyte(self.frame)
            else:
                self.mycanvas.destroy()
                self.window.destroy()
                self.haserror = True
                raise FileNotFoundError("\n\nNo suitable single-frame images found in the folder. \n")
        else:
            self.mycanvas.destroy()
            self.window.destroy()
            self.haserror = True
            raise RuntimeError("\n\nUnknown OS error. File or Directory may be corrupted or non-existent, and couldn't be opened. \n")

        # Store the original aspect ratio to rescale the dataset (i.e. High-Res images will not fit the screen otherwise)
        self.original_height = len(self.frame[0])
        self.original_width = len(self.frame)
        
        self.update_canvas()
        
        # Create a box to show the XY cordinates of the mouse
        self.mycanvas.bind('<Motion>', self.motion)

        # Create a button to start drawing the ROI
        self.update_ROI()
        
        # Create a label to indicate the frame number
        self.update_myframe()
        
        # Button that lets the user move forward by one frame
        self.update_forward()

        # Button that lets the user move backward by one frame
        self.update_backward()
        
        # Button that lets the user select the first and last frames of interest and create a scroll bar to scroll through frames in a dataset.
        if self.number_frames > 1:
            if int(np.ceil(self.photo.width()/self.number_frames)) > 30:
                self.sliderlength = int(np.ceil(self.photo.width()/self.number_frames))
            else:
                self.sliderlength = 30
            self.scrrect = tkinter.Scale(self.window, from_= 1, to = self.number_frames, orient = "horizontal", length = self.photo.width(), sliderlength = self.sliderlength, command = self.scrollrect)
            self.scrrect.grid(row = 2, column = 0, columnspan = 3)
            
            self.firstframe_button = tkinter.Button(self.window, text="Select First Frame", width=30, command= self.firstframe, state = "active")
            self.lastframe_button = tkinter.Button(self.window, text="Select Last Frame", width=30, command= self.lastframe, state = "active")
        else:
            self.firstframe_button = tkinter.Button(self.window, text="Single Image", width=30, state = "disabled")
            self.lastframe_button = tkinter.Button(self.window, text="Single Image", width=30, state = "disabled")
        self.update_ff_lf_buttons()
        
        # Button that lets the user safely close the image dataset
        self.exit_button = tkinter.Button(self.window, text="Continue", width=30, command= self.continue_program)
        self.exit_button['font'] = self.specialfont
        self.exit_button.grid(row=4, column=1, columnspan=1)
        self.window.protocol("WM_DELETE_WINDOW", self.onclosingwindow)
        self.window.mainloop()
    
    def onclosingwindow(self):
        self.window.destroy()
        self.haserror = True
        raise RuntimeError ("\n\nWindow closed during selection. \n")
        
    def sorted_alphanumeric(self, data):
        convert = lambda text: int(text) if text.isdigit() else text.lower()
        alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
        return sorted(data, key=alphanum_key)
    
    def update_canvas(self):
        self.mycanvas.grid_forget()
        if os.path.isfile(self.multimedia) == True:
            self.frame = self.image_set.get_data(self.index) # get_data opens each frame as an image array
        elif os.path.isdir(self.multimedia) == True:
            self.frame = imageio.imread(self.filelist[self.index]) #open each image from directory

        # Downscale 16-bit images to 8-bit, as PIL.Image cannot open/handle 16-bit images.
        if self.frame.dtype == "uint16":
            self.frame = util.img_as_ubyte(self.frame)

        # Convert image array into TKinter compatible image. master=self.mycanvas tells Tkinter to make the photo available to mycanvas and NOT the window (which is a separate Tkinter.Tk() instance)
        self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.frame), master=self.mycanvas) 
        # Resize the photo if needed
        if self.photo.width() < self.resolution or self.photo.height() < self.resolution:
            self.mycanvas = tkinter.Canvas(self.window, width = self.photo.width(), height = self.photo.height(), highlightthickness=0)
        else:
            self.resize = True
            self.photo = PIL.ImageTk.PhotoImage(image = (PIL.Image.fromarray(self.frame)).resize((int(np.round(self.original_height*self.resolution/self.original_width)), int(np.round(self.original_width*self.resolution/self.original_height)))), master=self.mycanvas)
            self.mycanvas = tkinter.Canvas(self.window, width = self.photo.width(), height = self.photo.height(), highlightthickness=0)
        # Post the photo onto the canvas and NOT the window. Create a tag for the photo on the canvas to later handle mouse events occurring ONLY on the photo and not on other objects drawn on mycanvas (e.g. the ROI rectangle or Circle)
        self.mycanvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW, tags="mypic")
        self.mycanvas.config(scrollregion=self.mycanvas.bbox('mypic'))
        self.mycanvas.grid(row = 1, column = 0, columnspan = 3)
  
    def update_ROI(self):
        if self.ROIrect == False:
            self.myROI_button = tkinter.Button(self.window, text="Click here to draw ROI", width=30, command= self.drawROI, state = "active")
            self.myROI_button['font'] = self.specialfont
        else:
            self.myROI_button = tkinter.Button(self.window, text="Reselect ROI", width=30, command= self.drawROI, state = "active")
            self.myROI_button['font'] = self.specialfont
        self.myROI_button.grid(row = 3, column = 1, columnspan = 1)
        
    def update_myframe(self):
        self.myframe = tkinter.Label(self.window, text = "Frame number: " + str(self.index+1) + " of " + str(self.number_frames))
        self.myframe.grid(row = 0, column = 0, columnspan = 1)
    
    def update_forward(self):
        if self.index == self.number_frames-1:
            self.forward_button = tkinter.Button(self.window, text=">>", width=30, state = "disabled")
        else:
            self.forward_button = tkinter.Button(self.window, text=">>", width=30, command= self.forward, state = "active")
        self.forward_button['font'] = self.largefont
        self.forward_button.grid(row=4, column=2, columnspan=1)
    
    def update_backward(self):
        if self.index == 0:
            self.backward_button = tkinter.Button(self.window, text="<<", width=30, state = "disabled")
        else:
            self.backward_button = tkinter.Button(self.window, text="<<", width=30, command= self.backward, state = "active")
        self.backward_button['font'] = self.largefont
        self.backward_button.grid(row=4, column=0, columnspan=1)
    
    def update_ff_lf_buttons(self):
        self.firstframe_button['font'] = self.mediumfont
        self.firstframe_button.grid(row=3, column=0, columnspan=1)
        self.lastframe_button['font'] = self.mediumfont
        self.lastframe_button.grid(row=3, column=2, columnspan=1)

    def forward(self):
        self.index += 1
        if self.index <= self.number_frames-1:
            self.myROI_button.grid_forget()
            
            self.update_myframe()
            self.update_canvas()
            self.update_forward()
            self.update_backward()
            self.update_ROI()
            self.scrrect.set(self.index+1)
            self.scrrect.grid(row = 2, column = 0, columnspan = 3)
            # Create a box to show the XY cordinates of the mouse
            self.mycanvas.bind('<Motion>', self.motion)
           
    def backward(self):
        self.index -= 1
        if self.index >= 0:
            self.myROI_button.grid_forget()
            
            self.update_myframe()            
            self.update_canvas()
            self.update_forward()
            self.update_backward()
            self.update_ROI()
            self.scrrect.set(self.index+1)
            self.scrrect.grid(row = 2, column = 0, columnspan = 3)
            # Create a box to show the XY cordinates of the mouse
            self.mycanvas.bind('<Motion>', self.motion)
            
    def scrollrect(self, val):
        self.index = int(val)-1
        self.scrrect.grid(row = 2, column = 0, columnspan = 3)
        self.update_myframe()
        self.update_canvas()
        self.update_forward()
        self.update_backward()
        self.mycanvas.bind('<Motion>', self.motion)
   
    def firstframe(self):
        self.first_frame = self.index
        self.firstframe_button.grid_forget()
        self.lastframe_button.grid_forget()
        self.myROI_button.grid_forget()
        
        if self.last_frame == None:
            self.firstframe_button = tkinter.Button(self.window, text="First Frame: " + str(self.first_frame+1), width=30, command= self.firstframe, state = "active")
            self.lastframe_button = tkinter.Button(self.window, text="Select Last Frame", width=30, command= self.lastframe, state = "active")
        elif self.first_frame >= self.last_frame and self.last_frame != None:
            self.firstframe_button = tkinter.Button(self.window, text="Frame Index Out of Range ("+str(self.first_frame+1)+")", width=30, command= self.firstframe, state = "disabled")
            self.lastframe_button = tkinter.Button(self.window, text="Last Frame: " + str(self.last_frame+1), width=30, command= self.lastframe, state = "active")
        else:
            self.firstframe_button = tkinter.Button(self.window, text="First Frame: " + str(self.first_frame+1), width=30, command= self.firstframe, state = "active")
            self.lastframe_button = tkinter.Button(self.window, text="Last Frame: " + str(self.last_frame+1), width=30, command= self.lastframe, state = "active")
        self.update_ff_lf_buttons()
        self.update_ROI()
        
        # Create a box to show the XY cordinates of the mouse
        self.mycanvas.bind('<Motion>', self.motion)
    
    def lastframe(self):
        self.last_frame = self.index
        self.firstframe_button.grid_forget()
        self.lastframe_button.grid_forget()
        self.myROI_button.grid_forget()
        
        if self.first_frame == None:
            self.lastframe_button = tkinter.Button(self.window, text="Last Frame: " + str(self.last_frame+1), width=30, command= self.lastframe, state = "active")
            self.firstframe_button = tkinter.Button(self.window, text="Select First Frame", width=30, command= self.firstframe, state = "active")
        elif self.last_frame <= self.first_frame and self.first_frame != None:
            self.lastframe_button = tkinter.Button(self.window, text="Frame Index Out of Range ("+str(self.last_frame+1)+")", width=30, command= self.lastframe, state = "disabled")
            self.firstframe_button = tkinter.Button(self.window, text="First Frame: " + str(self.first_frame+1), width=30, command= self.firstframe, state = "active")
        else:
            self.lastframe_button = tkinter.Button(self.window, text="Last Frame: " + str(self.last_frame+1), width=30, command= self.lastframe, state = "active")
            self.firstframe_button = tkinter.Button(self.window, text="First Frame: " + str(self.first_frame+1), width=30, command= self.firstframe, state = "active")
        self.update_ff_lf_buttons()
        self.update_ROI()
        
        # Create a box to show the XY cordinates of the mouse
        self.mycanvas.bind('<Motion>', self.motion)
    
    def drawROI(self):
        #If to re-draw the rectangle or circle, delete all previous objects on mycanvas and start afresh.
        if self.ROIrect == True:
            self.mycanvas.delete('all')
            self.rect = None
            self.update_canvas()
            
        self.myROI_button.grid_forget()
        self.myROI_button = tkinter.Button(self.window, text="Selecting...", width=30, state = "disabled")
        self.myROI_button['font'] = self.specialfont
        self.myROI_button.grid(row = 3, column = 1, columnspan = 1)
        self.ROIrect = True        

        self.mycanvas.bind('<Motion>', self.motion)
        self.mycanvas.bind("<ButtonPress-1>", self.on_button_press)
        self.mycanvas.bind("<B1-Motion>", self.on_move_press)
        self.mycanvas.bind("<ButtonRelease-1>", self.on_button_release)
    
    # Shows the cursor coordinates on the photo on mycanvas.    
    def motion(self, event):
        self.x, self.y = event.x, event.y
        if self.resize == False:
            self.myxy = tkinter.Label(self.window, text = "XY coordinates: " + str(self.x) + ", " + str(self.y))
        else:
            self.myxy = tkinter.Label(self.window, text = "XY coordinates: " + str(np.round(self.x*self.original_height/self.resolution)) + ", " + str(np.round(self.y*self.original_height/self.resolution)))
        self.myxy.grid(row = 0, column = 2, columnspan = 1)
    
    # Create a rectangle or a circle on left-mouse click ONLY if there are no other rectangles or circles already present.
    def on_button_press(self, event1):
        if not self.rect: # create rectangle/ circle if not yet exist
            # save mouse drag start position
            self.start_x = event1.x
            self.start_y = event1.y
            if self.ROIshape == 0:
                self.rect = self.mycanvas.create_rectangle(self.x, self.y, self.x+1, self.y+1, outline='red')
            else:
                self.rect = self.mycanvas.create_oval(self.x, self.y, self.x+1, self.y+1, outline='red')

    # Update the rectangle/circle size as the mouse performs 'move press' ONLY if the use has clicked 'draw ROI' or 'reselect ROI'
    def on_move_press(self, event2):
        if self.myROI_button['state'] == "disabled":
            self.curX = event2.x
            self.curY = event2.y
            # expand rectangle/circle as you drag the mouse
            self.mycanvas.coords(self.rect, self.start_x, self.start_y, self.curX, self.curY)

    def on_button_release(self, event3):
        self.myROI_button.grid_forget()
        self.update_ROI()        
    
    def results(self):
        if self.number_frames > 1:
            return (self.first_frame, self.last_frame, self.start_x, self.start_y, self.curX, self.curY, self.haserror)
        else:
            return (self.start_x, self.start_y, self.curX, self.curY, self.haserror)
    
    def continue_program(self):
        if self.number_frames > 1:
            if self.first_frame == None:
                print("First frame of interest not selected!") 
            else:
                print("First Frame Index: ", self.first_frame)
            if self.last_frame == None:
                print("Last frame of interest not selected!")
            else:
                print("Last Frame Index: ", self.last_frame)
        if self.start_x != None and self.start_y != None and self.curX != None and self.curY != None:
            if self.start_x < 0:
                self.start_x = 0
            elif self.start_x > self.photo.width():
                self.start_x = self.photo.width()
            if self.start_y < 0:
                self.start_y = 0
            elif self.start_y > self.photo.height():
                self.start_y = self.photo.height()
            if self.curX < 0:
                self.curX = 0
            elif self.curX > self.photo.width():
                self.curX = self.photo.width()
            if self.curY < 0:
                self.curY = 0
            elif self.curY > self.photo.height():
                self.curY = self.photo.height()
            
            if self.resize == True:
                self.start_x = int(np.round(self.start_x*self.original_height/self.resolution))
                self.start_y = int(np.round(self.start_y*self.original_height/self.resolution))
                self.curX = int(np.round(self.curX*self.original_height/self.resolution))
                self.curY = int(np.round(self.curY*self.original_height/self.resolution))
                print("Image rescaled to fit screen. Rounding error of pixel coordinates possible!")
            if self.ROIshape == 0:
                print("ROI Rectangle ( X1, Y1, X2, Y2 ): (", self.start_x, ",", self.start_y, ",", self.curX, ",", self.curY, ")")
            else:
                print("ROI Circle Bounding Box ( X1, Y1, X2, Y2 ): (", self.start_x, ",", self.start_y, ",", self.curX, ",", self.curY, ")")
        else:
            print("ROI not selected. 'None' type will be returned!")
        print()
        if os.path.isfile(self.multimedia) == True:
            self.image_set.close()
        self.mycanvas.destroy()
        self.firstframe_button.destroy()
        self.lastframe_button.destroy()
        self.myROI_button.destroy()
        self.window.destroy()

class FileSelector:
    def __init__(self, root):
        self.root = root
        self.root.title("UCL EIL - ROI and Frames Selector. Built by Anand Pallipurath.")
        self.roishape = tkinter.IntVar()
        
        self.frame3 = tkinter.Radiobutton(self.root, text = "Rectangle", variable = self.roishape, value = 0)
        self.frame3.grid(row = 1, column = 0, columnspan = 1)
        
        self.frame4 = tkinter.Radiobutton(self.root, text = "Circle", variable = self.roishape, value = 1)
        self.frame4.grid(row = 1, column = 2, columnspan = 1)
        
        self.frame3a = tkinter.Label(self.root, text = "Specify the shape of the ROI", state = "active")
        self.frame3a['font'] = font.Font(family="Helvetica", size=10, weight=font.BOLD, slant=font.ITALIC)
        self.frame3a.grid(row = 0, column = 1, columnspan = 1)
        
        self.frame1 = tkinter.Button(self.root, text = "Open Single Multimedia File", command = self.opt1_select, state = "active")
        self.frame1['font'] = font.Font(family="Helvetica", size=10, weight=font.BOLD, slant=font.ITALIC)
        self.frame1.grid(row = 2, column = 0, columnspan = 1)
        
        self.frame1a = tkinter.Label(self.root, text = "(e.g.: TIFF, JPEG, GIF, AVI, MP4, etc.)", state = "active")
        self.frame1a.grid(row = 3, column = 0, columnspan = 1)
        
        self.frame2 = tkinter.Button(self.root, text = "Open a Folder with Image Sequence", command = self.opt2_select, state = "active")
        self.frame2['font'] = font.Font(family="Helvetica", size=10, weight=font.BOLD, slant=font.ITALIC)
        self.frame2.grid(row = 2, column = 2, columnspan = 1)
        
        self.frame2a = tkinter.Label(self.root, text = "(e.g.: A Sequence of TIFF files in a Folder)", state = "active")
        self.frame2a.grid(row = 3, column = 2, columnspan = 1)
        
        self.frame4 = tkinter.Button(self.root, text = "CANCEL", command = self.root.destroy, state = "active")
        self.frame4['font'] = font.Font(family="Helvetica", size=10, weight=font.BOLD, slant=font.ITALIC)
        self.frame4.grid(row = 4, column = 1, columnspan = 1)
        self.root.protocol("WM_DELETE_WINDOW", self.onclosingroot)
        self.root.mainloop()
    
    def onclosingroot(self):
        self.root.destroy()
        raise RuntimeError ("\n\nWindow closed during selection. \n")
    
    def opt1_select(self):
        self.root.withdraw()
        self.filename = filedialog.askopenfilename(title = "Select a File", filetypes = (("All Files", "*.*"),))
        self.root.destroy()
        if self.filename != "":
            self.callvideobrowser()
        else:
            print("No file selected.")
    
    def opt2_select(self):
        self.root.withdraw()
        self.filename = filedialog.askdirectory(title = "Select a Folder", mustexist = True)
        self.root.destroy()
        if self.filename != "":
            self.callvideobrowser()
        else:
            print("No folder selected.")
    
    def callvideobrowser(self):
        if os.path.isfile(self.filename):
            self.myresults = VideoBrowser(tkinter.Tk(), self.filename, self.roishape.get()).results()
        elif os.path.isdir(self.filename):
            self.myresults = VideoBrowser(tkinter.Tk(), self.filename+"/", self.roishape.get()).results()  
    
    def results(self):
        return self.myresults

#Code starts here                       
if __name__ == "__main__":  
    FileSelector(tkinter.Tk())
