# imports
import io
import os
import time
import tkinter as tk
import tkinter.colorchooser as colorchooser
from tkinter import *
import sys
from PIL import ImageGrab, Image
import threading


class Canvas_GUI_Wrapper(threading.Thread):

    # methods
    # method to clear the canvas
    def clearCanvas(self):
        self.canvas.delete("all")

    # update brush size from slider
    def updateSize(self, val):
        self.selectedWidth = self.w1.get()

    # method to start painting
    def startPaint(self, e):
        self.canvas.bind('<B1-Motion>', self.paint)
        self.lastX = e.x
        self.lastY = e.y

    # method to perform painting
    # sleeps prevent 'twitching' of line when drawing slowly
    def paint(self, e):
        self.updateSize(None)

        brush_width = self.selectedWidth



        x = e.x
        y = e.y
        self.canvas.create_line((self.lastX, self.lastY, x, y), width=self.selectedWidth, fill=self.color[1])

        self.lastX = x
        self.lastY = y

    # method to select color
    def newColor(self):
        self.color = colorchooser.askcolor()
        # self.colorCanvas.config(bg=self.color[1])
        self.button4.config(bg=self.color[1])

    def newBGColor(self):
        self.bgColor = colorchooser.askcolor()
        self.button6.config(bg=self.bgColor[1])
        self.canvas.config(bg=self.bgColor[1])

    def flashColor(self, object, color_index):
        object.config(background=self.bg_flash_colors[color_index])
        # object.config(foreground=self.fg_flash_colors[color_index])
        self.root.after(self.flash_delay, self.flashColor, object, 1 - color_index)

    # leave chatroom
    def leaveChat(self):
        # leave the chatroom by letting server know you are exiting
        self.peer.EXIT_FLAG = True
        try:
            self.peer.leave_server() # synchronous call to ensure that server knows
        finally:
            os._exit(0)


    # this method is honestly disgusting but it needs to be this way
    def __init__(self, peer):
        # call threading.Thread init because otherwise it just crashes (?)
        super(Canvas_GUI_Wrapper, self).__init__()

        self.lastX = 0
        self.lastY = 0
        self.color = None
        self.selectedWidth = None

        # maintain peer reference
        self.peer = peer

    # override the run method of Thread... readability of this is horrible, but we have to create all these instance
    # variables variables in run() to avoid errors inherent to Tkinter and threading
    def run(self):
        # flashing for messages button
        self.flash_delay = 750
        self.bg_flash_colors = ("white", "red")
        self.fg_flash_colors = ("black", "white")

        self.root = tk.Tk()
        self.root.withdraw()

        # create our gui
        self.gui = tk.Tk()
        self.gui.title('PictoChat The Rebirth')
        self.gui.minsize(1200, 610)
        self.gui.maxsize(1200, 610)

        # default color
        self.color = [' ', 'pink']
        self.bgColor = [' ', 'white']

        # populate our gui
        # canvas object
        self.canvas = Canvas(self.gui, bg="white", width=960, height=590)
        self.canvas.place(x=10, y=10)
        # buttons
        # send button
        self.button1 = tk.Button(self.gui, text="Send Message", width=28, height=8, fg="green",
                                 activeforeground="green", command=self.broadcast_canvas)

        self.button1.place(x=980, y=425)
        # leave button
        self.button2 = tk.Button(self.gui, text="Leave Chat Room", width=28, height=2, fg="red", activeforeground="red",
                                 command=self.leaveChat)
        self.button2.place(x=980, y=560)

        # self.button3.place(x=980, y=13)
        # select color button
        self.button4 = tk.Button(self.gui, text="Brush Color", width=28, height=3, command=self.newColor, bg=self.color[1])
        self.button4.place(x=980, y=190)
        # selected color display label
        # self.label1 = Label(self.gui, text="Current Color")
        # self.label1.place(x=1040, y=170)
        # label for brush size
        self.label2 = Label(self.gui, text="Brush Size")
        self.label2.place(x=1050, y=100)

        self.button6 = tk.Button(self.gui, text="Background Color", width=28, height=3, command=self.newBGColor,
                                 bg=self.bgColor[1])
        self.button6.place(x=980, y=255)

        # selected color display viewable color
        # self.colorCanvas = Canvas(self.gui, bg=self.color[1], width=203, height=50)
        # self.colorCanvas.place(x=980, y=190)
        # slider for size
        self.w1 = Scale(self.gui, from_=1, to_=50, length=200, orient=HORIZONTAL, command=self.updateSize)
        self.w1.set(5)
        self.w1.place(x=980, y=115)
        # clear button
        self.button5 = tk.Button(self.gui, text="Clear Drawing", width=28, height=3, command=self.clearCanvas)
        self.button5.place(x=980, y=350)

        # if we have messages run this line
        # self.flashColor(self.button3, 0)

        # data for drawing
        self.lastX, self.lastY = None, None
        self.canvas.bind('<1>', self.startPaint)
        # size
        self.selectedWidth = self.w1.get()
        # run our gui
        self.gui.mainloop()

    # can't have a threaded method as a command for a button, so create a thread to handle this in the background
    def broadcast_canvas(self):
        t = threading.Thread(target=self.broadcast_canvas_thread)
        t.setDaemon(True)
        t.start()

    def save_as_png(self, fileName):
        # save postscipt image
        bgFill = self.canvas.create_rectangle(2, 2, 960, 590, fill = self.bgColor[1])
        self.canvas.tag_lower(bgFill)
        self.canvas.postscript(file=fileName + '.eps')
        # use PIL to convert to PNG
        img = Image.open(fileName + '.eps')
        img.save(fileName + '.png', 'png')

        # save the canvas
    def broadcast_canvas_thread(self):
        self.save_as_png("outgoing")
        img_pointer = open('outgoing.png', mode='rb')

        # tell peer to broadcast image with given file handle or "pointer" to file
        self.peer.broadcast_image(img_pointer, self.peer.nickname)
