# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 13:24:02 2020

@author: Anand Pallipurath
"""
import os
import numpy as np
import tkinter
import tkinter.font as font
import imageio
import PIL.Image, PIL.ImageTk

class VideoBrowser:
    def __init__(self, myvideo=None):
        window = tkinter.Tk()
        self.window = window
        self.window.title("Video ROI and Frames Selector")
        self.delay = 15 # After it is called once, the update method will be automatically called every delay milliseconds

        self.largefont = font.Font(family="Verdana", size=10, weight=font.BOLD)
        self.mediumfont = font.Font(family="Verdana", size=10, weight=font.BOLD, slant=font.ITALIC)
        self.specialfont = font.Font(family="Helvetica", size=10, weight=font.BOLD, slant=font.ITALIC)
        
        self.index = 0
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
        self.resolution = 800
        
        self.myvideo = myvideo
        self.image_set = imageio.get_reader(myvideo, mode = '?') #image_set is the list of images
        self.number_frames = len(list(enumerate(self.image_set)))
        
        # Display the image based on the index
        self.frame = self.image_set.get_data(self.index) #get_data opens each frame as an image array
        self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.frame))
        self.original_height = self.photo.height()
        self.original_width = self.photo.width()

        # Create a canvas that can fit the above video source size
        if self.photo.width() < self.resolution or self.photo.height() < self.resolution:
            self.mycanvas = tkinter.Canvas(window, width = self.photo.width(), height = self.photo.height(), highlightthickness=0)
        else:
            self.resize = True
            self.photo = PIL.ImageTk.PhotoImage(image = (PIL.Image.fromarray(self.frame)).resize((int(np.round(self.photo.width()*self.resolution/self.original_height)), self.resolution)))
            self.mycanvas = tkinter.Canvas(window, width = self.photo.width(), height = self.photo.height(), highlightthickness=0)
        self.mycanvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW, tags="mypic")
        self.mycanvas.grid(row = 1, column = 0, columnspan = 3)
        
        # Create a box to show the XY cordinates of the mouse
        self.mycanvas.config(scrollregion=self.mycanvas.bbox('mypic'))
        self.mycanvas.bind('<Motion>', self.motion)

        # Create a button to start drawing the ROI
        if self.ROIrect == False:
            self.myROI_button = tkinter.Button(window, text="Click here to draw ROI", width=30, command= self.drawROI, state = "active")
            self.myROI_button['font'] = self.specialfont
        else:
            self.myROI_button = tkinter.Button(window, text="Reselect ROI", width=30, command= self.drawROI, state = "active")
            self.myROI_button['font'] = self.specialfont
        self.myROI_button.grid(row = 3, column = 1, columnspan = 1)
        
        # Create a label to indicate the frame number
        self.myframe = tkinter.Label(window, text = "Frame number: " + str(self.index+1) + " of " + str(self.number_frames))
        self.myframe.grid(row = 0, column = 0, columnspan = 1)
        
        # Button that lets the user move forward by one frame
        if self.index == self.number_frames-1:
            self.forward_button = tkinter.Button(window, text=">>", width=30, state = "disabled")
        else:
            self.forward_button = tkinter.Button(window, text=">>", width=30, command= self.forward, state = "active")
        self.forward_button['font'] = self.largefont
        self.forward_button.grid(row=4, column=2, columnspan=1)

        # Button that lets the user move backward by one frame
        if self.index == 0:
            self.backward_button = tkinter.Button(window, text="<<", width=30, state = "disabled")
        else:
            self.backward_button = tkinter.Button(window, text="<<", width=30, command= self.backward, state = "active")
        self.backward_button['font'] = self.largefont
        self.backward_button.grid(row=4, column=0, columnspan=1)
        
        # Button that lets the user select the first frame of interest
        if self.number_frames > 1:
            self.firstframe_button = tkinter.Button(window, text="Select First Frame", width=30, command= self.firstframe, state = "active")
        else:
            self.firstframe_button = tkinter.Button(window, text="Single Image", width=30, state = "disabled")
        self.firstframe_button['font'] = self.mediumfont
        self.firstframe_button.grid(row=3, column=0, columnspan=1)
        
        # Button that lets the user select the last frame of interest
        if self.number_frames > 1:
            self.lastframe_button = tkinter.Button(window, text="Select Last Frame", width=30, command= self.lastframe, state = "active")
        else:
            self.lastframe_button = tkinter.Button(window, text="Single Image", width=30, state = "disabled")
        self.lastframe_button['font'] = self.mediumfont
        self.lastframe_button.grid(row=3, column=2, columnspan=1)
        
        # Button that lets the user safely close the image dataset
        self.exit_button = tkinter.Button(window, text="Continue", width=30, command= self.continue_program)
        self.exit_button['font'] = self.specialfont
        self.exit_button.grid(row=4, column=1, columnspan=1)

        self.window.mainloop()    

    def forward(self):
        self.index += 1
        if self.index <= self.number_frames-1:
            self.mycanvas.grid_forget()
            self.myframe.grid_forget()
            self.forward_button.grid_forget()
            self.backward_button.grid_forget()
            
            self.myframe = tkinter.Label(self.window, text = "Frame number: " + str(self.index+1) + " of " + str(self.number_frames))
            self.myframe.grid(row = 0, column = 0, columnspan = 1)
            
            self.frame = self.image_set.get_data(self.index) #get_data opens each frame as an image array
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.frame))
            if self.photo.width() < self.resolution or self.photo.height() < self.resolution:
                self.mycanvas = tkinter.Canvas(self.window, width = self.photo.width(), height = self.photo.height(), highlightthickness=0)
            else:
                self.resize = True
                self.photo = PIL.ImageTk.PhotoImage(image = (PIL.Image.fromarray(self.frame)).resize((int(np.round(self.photo.width()*self.resolution/self.original_height)), self.resolution)))
                self.mycanvas = tkinter.Canvas(self.window, width = self.photo.width(), height = self.photo.height(), highlightthickness=0)
            self.mycanvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW, tags="mypic")
            self.mycanvas.grid(row = 1, column = 0, columnspan = 3)
            
            if self.index == self.number_frames-1:
                self.forward_button = tkinter.Button(self.window, text=">>", width=30, state = "disabled")
            else:
                self.forward_button = tkinter.Button(self.window, text=">>", width=30, command= self.forward, state = "active")
            self.forward_button['font'] = self.largefont
            self.forward_button.grid(row=4, column=2, columnspan=1)
            
            if self.index == 0:
                self.backward_button = tkinter.Button(self.window, text="<<", width=30, state = "disabled")
            else:
                self.backward_button = tkinter.Button(self.window, text="<<", width=30, command= self.backward, state = "active")
            self.backward_button['font'] = self.largefont
            self.backward_button.grid(row=4, column=0, columnspan=1)
            # Create a box to show the XY cordinates of the mouse
            self.mycanvas.config(scrollregion=self.mycanvas.bbox('mypic'))
            self.mycanvas.bind('<Motion>', self.motion)
            self.myROI_button.grid_forget()
            if self.ROIrect == False:
                self.myROI_button = tkinter.Button(self.window, text="Click here to draw ROI", width=30, command= self.drawROI, state = "active")
                self.myROI_button['font'] = self.specialfont
            else:
                self.myROI_button = tkinter.Button(self.window, text="Reselect ROI", width=30, command= self.drawROI, state = "active")
                self.myROI_button['font'] = self.specialfont
            self.myROI_button.grid(row = 3, column = 1, columnspan = 1)
            self.window.after(self.delay)
           
    def backward(self):
        self.index -= 1
        if self.index >= 0:
            self.mycanvas.grid_forget()
            self.myframe.grid_forget()
            self.forward_button.grid_forget()
            self.backward_button.grid_forget()
            
            self.myframe = tkinter.Label(self.window, text = "Frame number: " + str(self.index+1) + " of " + str(self.number_frames))
            self.myframe.grid(row = 0, column = 0, columnspan = 1)
            
            self.frame = self.image_set.get_data(self.index) #get_data opens each frame as an image array
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.frame))
            if self.photo.width() < self.resolution or self.photo.height() < self.resolution:
                self.mycanvas = tkinter.Canvas(self.window, width = self.photo.width(), height = self.photo.height(), highlightthickness=0)
            else:
                self.resize = True
                self.photo = PIL.ImageTk.PhotoImage(image = (PIL.Image.fromarray(self.frame)).resize((int(np.round(self.photo.width()*self.resolution/self.original_height)), self.resolution)))
                self.mycanvas = tkinter.Canvas(self.window, width = self.photo.width(), height = self.photo.height(), highlightthickness=0)
            self.mycanvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW, tags="mypic")
            self.mycanvas.grid(row = 1, column = 0, columnspan = 3)
            
            if self.index == 0:
                self.backward_button = tkinter.Button(self.window, text="<<", width=30, state = "disabled")
            else:
                self.backward_button = tkinter.Button(self.window, text="<<", width=30, command= self.backward, state = "active")
            self.backward_button['font'] = self.largefont
            self.backward_button.grid(row=4, column=0, columnspan=1)
            
            if self.index == self.number_frames-1:
                self.forward_button = tkinter.Button(self.window, text=">>", width=30, state = "disabled")
            else:
                self.forward_button = tkinter.Button(self.window, text=">>", width=30, command= self.forward, state = "active")
            self.forward_button['font'] = self.largefont
            self.forward_button.grid(row=4, column=2, columnspan=1)
            # Create a box to show the XY cordinates of the mouse
            self.mycanvas.config(scrollregion=self.mycanvas.bbox('mypic'))
            self.mycanvas.bind('<Motion>', self.motion)
            self.myROI_button.grid_forget()
            if self.ROIrect == False:
                self.myROI_button = tkinter.Button(self.window, text="Click here to draw ROI", width=30, command= self.drawROI, state = "active")
                self.myROI_button['font'] = self.specialfont
            else:
                self.myROI_button = tkinter.Button(self.window, text="Reselect ROI", width=30, command= self.drawROI, state = "active")
                self.myROI_button['font'] = self.specialfont
            self.myROI_button.grid(row = 3, column = 1, columnspan = 1)
            self.window.after(self.delay)
    
    def firstframe(self):
        self.firstframe_button.grid_forget()
        self.lastframe_button.grid_forget()
        self.first_frame = self.index
        
        if self.last_frame == None:
            self.firstframe_button = tkinter.Button(self.window, text="First Frame: " + str(self.first_frame+1), width=30, command= self.firstframe, state = "active")
            self.lastframe_button = tkinter.Button(self.window, text="Select Last Frame", width=30, command= self.lastframe, state = "active")
        elif self.first_frame >= self.last_frame and self.last_frame != None:
            self.firstframe_button = tkinter.Button(self.window, text="Frame Index Out of Range ("+str(self.first_frame+1)+")", width=30, command= self.firstframe, state = "disabled")
            self.lastframe_button = tkinter.Button(self.window, text="Last Frame: " + str(self.last_frame+1), width=30, command= self.lastframe, state = "active")
        else:
            self.firstframe_button = tkinter.Button(self.window, text="First Frame: " + str(self.first_frame+1), width=30, command= self.firstframe, state = "active")
            self.lastframe_button = tkinter.Button(self.window, text="Last Frame: " + str(self.last_frame+1), width=30, command= self.lastframe, state = "active")
        self.firstframe_button['font'] = self.mediumfont
        self.lastframe_button['font'] = self.mediumfont
        self.firstframe_button.grid(row=3, column=0, columnspan=1)
        self.lastframe_button.grid(row=3, column=2, columnspan=1)
        # Create a box to show the XY cordinates of the mouse
        self.mycanvas.config(scrollregion=self.mycanvas.bbox('mypic'))
        self.mycanvas.bind('<Motion>', self.motion)
        self.myROI_button.grid_forget()
        if self.ROIrect == False:
            self.myROI_button = tkinter.Button(self.window, text="Click here to draw ROI", width=30, command= self.drawROI, state = "active")
            self.myROI_button['font'] = self.specialfont
        else:
            self.myROI_button = tkinter.Button(self.window, text="Reselect ROI", width=30, command= self.drawROI, state = "active")
            self.myROI_button['font'] = self.specialfont
        self.myROI_button.grid(row = 3, column = 1, columnspan = 1)
        self.window.after(self.delay)
    
    def lastframe(self):
        self.firstframe_button.grid_forget()
        self.lastframe_button.grid_forget()
        self.last_frame = self.index
        
        if self.first_frame == None:
            self.lastframe_button = tkinter.Button(self.window, text="Last Frame: " + str(self.last_frame+1), width=30, command= self.lastframe, state = "active")
            self.firstframe_button = tkinter.Button(self.window, text="Select First Frame", width=30, command= self.firstframe, state = "active")
        elif self.last_frame <= self.first_frame and self.first_frame != None:
            self.lastframe_button = tkinter.Button(self.window, text="Frame Index Out of Range ("+str(self.last_frame+1)+")", width=30, command= self.lastframe, state = "disabled")
            self.firstframe_button = tkinter.Button(self.window, text="First Frame: " + str(self.first_frame+1), width=30, command= self.firstframe, state = "active")
        else:
            self.lastframe_button = tkinter.Button(self.window, text="Last Frame: " + str(self.last_frame+1), width=30, command= self.lastframe, state = "active")
            self.firstframe_button = tkinter.Button(self.window, text="First Frame: " + str(self.first_frame+1), width=30, command= self.firstframe, state = "active")
        self.firstframe_button['font'] = self.mediumfont
        self.lastframe_button['font'] = self.mediumfont
        self.lastframe_button.grid(row=3, column=2, columnspan=1)
        self.firstframe_button.grid(row=3, column=0, columnspan=1)
        # Create a box to show the XY cordinates of the mouse
        self.mycanvas.config(scrollregion=self.mycanvas.bbox('mypic'))
        self.mycanvas.bind('<Motion>', self.motion)
        self.myROI_button.grid_forget()
        if self.ROIrect == False:
            self.myROI_button = tkinter.Button(self.window, text="Click here to draw ROI", width=30, command= self.drawROI, state = "active")
            self.myROI_button['font'] = self.specialfont
        else:
            self.myROI_button = tkinter.Button(self.window, text="Reselect ROI", width=30, command= self.drawROI, state = "active")
            self.myROI_button['font'] = self.specialfont
        self.myROI_button.grid(row = 3, column = 1, columnspan = 1)
        self.window.after(self.delay)
    
    def drawROI(self):
        if self.ROIrect == True:
            self.mycanvas.delete('all')
            self.rect = None
            self.frame = self.image_set.get_data(self.index) #get_data opens each frame as an image array
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.frame))
            if self.photo.width() < self.resolution or self.photo.height() < self.resolution:
                self.mycanvas = tkinter.Canvas(self.window, width = self.photo.width(), height = self.photo.height(), highlightthickness=0)
            else:
                self.resize = True
                self.photo = PIL.ImageTk.PhotoImage(image = (PIL.Image.fromarray(self.frame)).resize((int(np.round(self.photo.width()*self.resolution/self.original_height)), self.resolution)))
                self.mycanvas = tkinter.Canvas(self.window, width = self.photo.width(), height = self.photo.height(), highlightthickness=0)
            self.mycanvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW, tags="mypic")
            self.mycanvas.grid(row = 1, column = 0, columnspan = 3)
        self.myROI_button.grid_forget()
        self.myROI_button = tkinter.Button(self.window, text="Selecting...", width=30, state = "disabled")
        self.myROI_button['font'] = self.specialfont
        self.myROI_button.grid(row = 3, column = 1, columnspan = 1)
        self.ROIrect = True        
        self.mycanvas.config(scrollregion=self.mycanvas.bbox('mypic'))
        self.mycanvas.bind('<Motion>', self.motion)
        self.mycanvas.bind("<ButtonPress-1>", self.on_button_press)
        self.mycanvas.bind("<B1-Motion>", self.on_move_press)
        self.mycanvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.window.after(self.delay)
        
    def motion(self, event):
        self.x, self.y = event.x, event.y
        if self.resize == False:
            self.myxy = tkinter.Label(self.window, text = "XY coordinates: " + str(self.x) + ", " + str(self.y))
        else:
            self.myxy = tkinter.Label(self.window, text = "XY coordinates: " + str(np.round(self.x*self.original_height/self.resolution)) + ", " + str(np.round(self.y*self.original_height/self.resolution)))
        self.myxy.grid(row = 0, column = 2, columnspan = 1)
    
    def on_button_press(self, event1):
        if not self.rect: # create rectangle if not yet exist
            # save mouse drag start position
            self.start_x = event1.x
            self.start_y = event1.y
            self.rect = self.mycanvas.create_rectangle(self.x, self.y, 1, 1, outline='red')
    
    def on_move_press(self, event2):
        if self.myROI_button['state'] == "disabled":
            self.curX = event2.x
            self.curY = event2.y
            # expand rectangle as you drag the mouse
            self.mycanvas.coords(self.rect, self.start_x, self.start_y, self.curX, self.curY)
    
    def on_button_release(self, event3):
        self.myROI_button.grid_forget()
        self.myROI_button = tkinter.Button(self.window, text="Reselect ROI", width=30, command= self.drawROI, state = "active")
        self.myROI_button['font'] = self.specialfont
        self.myROI_button.grid(row = 3, column = 1, columnspan = 1)
    
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
        self.window.destroy()
        self.results()
    
    def results(self):
        if self.number_frames > 1:
            return (self.first_frame, self.last_frame, self.start_x, self.start_y, self.curX, self.curY)
        else:
            return (self.start_x, self.start_y, self.curX, self.curY)
       
if __name__ == "__main__":
    print("Done")
