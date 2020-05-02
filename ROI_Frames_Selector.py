# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 13:24:02 2020

@author: Anand Pallipurath
"""
import numpy as np
import tkinter
import tkinter.font as font
import tkinter.filedialog as filedialog
import imageio
import PIL.Image, PIL.ImageTk
import os
import json

#  Load the configuration file
import configparser
config = configparser.ConfigParser()
config.read('TKinter_ROI_Frames_Selector.cfg')

#  Load FFMPEG file extensions from settings
FFMPEGFileExtensions = json.loads(config.get("SETTINGS", "FFMPEGFileExtensions"))


class VideoBrowser:
    def __init__(self, window, myvideo=None):
        # Create a window and build the Application objects
        self.window = window
        self.myvideo = myvideo
        self.window.title("UCL EIL - ROI and Frames Selector. Built by Anand Pallipurath.")
        
        self.resolution = 800 # Giving a decent resolution to resize large images to fit a screen
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

        #  Get filename file_extension
        self.file_extension = (os.path.splitext(myvideo)[1])
        
        self.image_set = imageio.get_reader(myvideo, mode = '?') #image_set is a reader object with the list of images. This loads the entire file onto memory.

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
        self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.frame), master=self.mycanvas) #convert image array into TKinter compatible image
        # Store the original aspect ratio to rescale the dataset (i.e. High-Res images will not fit the screen otherwise)
        self.original_height = self.photo.height() 
        self.original_width = self.photo.width()
        
        self.mycanvas.grid_forget()
        self.update_canvas()
        self.scrollcanvas = tkinter.Canvas(self.window, width = self.photo.width(), height = 20, bg = "#D3D3D3", highlightthickness=0)
        
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
            self.scrrect = self.scrollcanvas.create_rectangle(int(np.round(self.index*(self.photo.width() - 75)/(self.number_frames-1))), 2, int(np.round(self.index*(self.photo.width() - 75)/(self.number_frames-1)) + 75), 18, fill='#808080', outline = '#808080', activefill = "#696969" , activeoutline = "#696969", disabledfill = "#D3D3D3", disabledoutline = "#D3D3D3", state="normal", tags="scrrect")
            self.scrollcanvas.grid(row = 2, column = 0, columnspan = 3)
            self.scrollrect()
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
        self.window.mainloop()

    def update_canvas(self):
        self.frame = self.image_set.get_data(self.index) # get_data opens each frame as an image array
        # Convert image array into TKinter compatible image. master=self.mycanvas tells Tkinter to make the photo available to mycanvas and NOT the window (which is a separate Tkinter.Tk() instance)
        self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.frame), master=self.mycanvas) 
        # Resize the photo if needed
        if self.photo.width() < self.resolution or self.photo.height() < self.resolution:
            self.mycanvas = tkinter.Canvas(self.window, width = self.photo.width(), height = self.photo.height(), highlightthickness=0)
        else:
            self.resize = True
            self.photo = PIL.ImageTk.PhotoImage(image = (PIL.Image.fromarray(self.frame)).resize((int(np.round(self.photo.width()*self.resolution/self.original_height)), self.resolution)), master=self.mycanvas)
            self.mycanvas = tkinter.Canvas(self.window, width = self.photo.width(), height = self.photo.height(), highlightthickness=0)
        # Post the photo onto the canvas and NOT the window. Create a tag for the photo on the canvas to later handle mouse events occurring ONLY on the photo and not on other objects drawn on mycanvas (e.g. the ROI rectangle)
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
            self.mycanvas.grid_forget()
            self.myframe.grid_forget()
            self.forward_button.grid_forget()
            self.backward_button.grid_forget()
            self.myROI_button.grid_forget()
            
            self.update_myframe()
            self.update_canvas()
            self.update_forward()
            self.update_backward()
            self.update_ROI()
            self.scrollrect()
            # Create a box to show the XY cordinates of the mouse
            self.mycanvas.bind('<Motion>', self.motion)
           
    def backward(self):
        self.index -= 1
        if self.index >= 0:
            self.mycanvas.grid_forget()
            self.myframe.grid_forget()
            self.forward_button.grid_forget()
            self.backward_button.grid_forget()
            self.myROI_button.grid_forget()
            
            self.update_myframe()            
            self.update_canvas()
            self.update_forward()
            self.update_backward()
            self.update_ROI()
            self.scrollrect()
            # Create a box to show the XY cordinates of the mouse
            self.mycanvas.bind('<Motion>', self.motion)
            
    def scrollrect(self):
        self.scrollcanvas.delete('scrrect')
        self.scrrect = self.scrollcanvas.create_rectangle(int(np.round(self.index*(self.photo.width() - 75)/(self.number_frames-1))), 2, int(np.round(self.index*(self.photo.width() - 75)/(self.number_frames-1)) + 75), 18, fill='#808080', outline = '#808080', activefill = "#696969" , activeoutline = "#696969", disabledfill = "#D3D3D3", disabledoutline = "#D3D3D3", state="normal", tags="scrrect")
        self.scrollcanvas.config(scrollregion=self.scrollcanvas.bbox('scrrect'))
        self.scrollcanvas.grid(row = 2, column = 0, columnspan = 3)
        #self.scrollcanvas.tag_bind("scrrect", "<ButtonPress-1>", self.on_button_press_rect)
        self.scrollcanvas.tag_bind("scrrect", "<B1-Motion>", self.on_move_press_rect)
            
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
        #If to re-draw a rectangle, delete all previous objects on mycanvas and start afresh.
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
    
    # Create a rectangle on left-mouse click ONLY if there are no other rectangles already present.
    def on_button_press(self, event1):
        if not self.rect: # create rectangle if not yet exist
            # save mouse drag start position
            self.start_x = event1.x
            self.start_y = event1.y
            self.rect = self.mycanvas.create_rectangle(self.x, self.y, 1, 1, outline='red')

    # Update the rectangle size as the mouse performs 'move press' ONLY if the use has clicked 'draw ROI' or 'reselect ROI'
    def on_move_press(self, event2):
        if self.myROI_button['state'] == "disabled":
            self.curX = event2.x
            self.curY = event2.y
            # expand rectangle as you drag the mouse
            self.mycanvas.coords(self.rect, self.start_x, self.start_y, self.curX, self.curY)
    
    def on_button_release(self, event3):
        self.myROI_button.grid_forget()
        self.update_ROI()
    
    def on_button_press_rect(self, event3):
        # move scrollbar once if clicked.
        self.scr_x = event3.x
        if self.scr_x < 0:
            self.scr_x = 0
        elif self.scr_x > self.photo.width() - 75:
            self.scr_x = self.photo.width() - 75
        self.scrollcanvas.coords(self.scrrect, int(np.round(self.index*(self.scr_x)/(self.number_frames-1))), 2, int(np.round(self.index*(self.scr_x)/(self.number_frames-1))+75), 18)
        self.index = int(np.round(self.scr_x*(self.number_frames-1)/(self.photo.width() - 75)))
        self.update_forward()
        self.update_backward()
        self.update_myframe()
        self.update_canvas()

    def on_move_press_rect(self, event4):
        # move scroll bar as the mouse is dragged after a click.
        self.curscrX = event4.x
        if self.curscrX < 0:
            self.curscrX = 0
        elif self.curscrX > self.photo.width() - 75:
            self.curscrX = self.photo.width() - 75
        self.scrollcanvas.coords(self.scrrect, int(np.round(self.index*(self.curscrX)/(self.number_frames-1))), 2, int(np.round(self.index*(self.curscrX)/(self.number_frames-1))+75), 18)
        self.index = int(np.round(self.curscrX*(self.number_frames-1)/(self.photo.width() - 75)))
        self.update_forward()
        self.update_backward()
        self.update_myframe()
        self.update_canvas()
    
    def results(self):
        if self.number_frames > 1:
            return (self.first_frame, self.last_frame, self.start_x, self.start_y, self.curX, self.curY)
        else:
            return (self.start_x, self.start_y, self.curX, self.curY)
    
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
                print("Image rescaled to fit screen. Possible rounding error of pixel coordinates!")
            print("ROI Rectangle ( X1, Y1, X2, Y2 ): (", self.start_x, ",", self.start_y, ",", self.curX, ",", self.curY, ")")
        else:
            print("ROI Rectangle not selected. 'None' type will be returned!")
        print()
        self.image_set.close()
        self.mycanvas.destroy()
        self.firstframe_button.destroy()
        self.lastframe_button.destroy()
        self.myROI_button.destroy()
        self.window.destroy()

if __name__ == "__main__":
    root = tkinter.Tk()
    root.withdraw()
    root.filename = filedialog.askopenfilename(title = "Select a File", filetypes = (("All Files", "*.*"),))
    filename = root.filename
    root.destroy()
    if filename != "":
        output = VideoBrowser(tkinter.Tk(), filename).results()
        print(output)
    else:
        print("No file selected.")
