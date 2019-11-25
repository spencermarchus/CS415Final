# imports
import tkinter as tk
import tkinter.colorchooser as colorchooser
from tkinter import *
import sys

import threading


class Canvas_GUI_Wrapper(threading.Thread):

    # methods
    # update brush size from slider
    def updateSize(self, val):
        self.selectedWidth = self.w1.get()

    # method to start painting
    def startPaint(self, e):
        self.canvas.bind('<B1-Motion>', self.paint)
        self.lastX = e.x
        self.lastY = e.y

    # method to perform painting
    def paint(self, e):
        self.updateSize(None)
        x = e.x
        y = e.y
        self.canvas.create_line((self.lastX, self.lastY, x, y), width=self.selectedWidth, fill=self.color[1])
        self.lastX = x
        self.lastY = y

    # method to select color
    def newColor(self):
        self.color = colorchooser.askcolor()
        self.colorCanvas.config(bg=self.color[1])

    def flashColor(self, object, color_index):
        object.config(background=self.bg_flash_colors[color_index])
        object.config(foreground=self.fg_flash_colors[color_index])
        self.root.after(self.flash_delay, self.flashColor, object, 1 - color_index)

    # leave chatroom
    def leaveChat(self):
        # leave the chatroom by letting server know you are exiting
        quit()

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

        # default color
        self.color = [' ', 'pink']

        # populate our gui
        # canvas object
        self.canvas = Canvas(self.gui, bg="gray", width=960, height=590)
        self.canvas.place(x=10, y=10)
        # buttons
        # send button
        self.button1 = tk.Button(self.gui, text="Send Message", width=28, height=8, fg="green",
                                 activeforeground="green")
        self.button1.place(x=980, y=425)
        # leave button
        self.button2 = tk.Button(self.gui, text="Leave Chat Room", width=28, height=2, fg="red", activeforeground="red",
                                 command=self.leaveChat)
        self.button2.place(x=980, y=560)
        # incoming messages button
        self.button3 = tk.Button(self.gui, text="Incoming Messages", width=28, height=4, activebackground="red",
                                 activeforeground="white")
        self.button3.place(x=980, y=13)
        # select color button
        self.button4 = tk.Button(self.gui, text="Select A New Color", width=28, height=3, command=self.newColor)
        self.button4.place(x=980, y=325)
        # selected color display label
        self.label1 = Label(self.gui, text="Current Color")
        self.label1.place(x=1040, y=240)
        # label for brush size
        self.label2 = Label(self.gui, text="Brush Size")
        self.label2.place(x=1050, y=100)
        # selected color display viewable color
        self.colorCanvas = Canvas(self.gui, bg=self.color[1], width=203, height=50)
        self.colorCanvas.place(x=980, y=260)
        # slider for size
        self.w1 = Scale(self.gui, from_=1, to_=50, length=200, orient=HORIZONTAL, command=self.updateSize)
        self.w1.set(5)
        self.w1.place(x=980, y=115)

        # if we have messages run this line
        self.flashColor(self.button3, 0)

        # data for drawing
        self.lastX, self.lastY = None, None
        self.canvas.bind('<1>', self.startPaint)
        # size
        self.selectedWidth = self.w1.get()

        # run our gui
        self.gui.mainloop()

