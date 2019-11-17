#imports
import tkinter as tk
import tkinter.colorchooser
from tkinter import *
import sys


#methods
#update brush size from slider
def updateSize(val):
    global selectedWidth
    selectedWidth = w1.get()

#method to start painting
def startPaint(e):
    global lastX, lastY
    canvas.bind('<B1-Motion>', paint)
    lastX = e.x
    lastY = e.y


#method to perform painting
def paint(e):
    global lastX, lastY, selectedWidth, color
    updateSize(None)
    x = e.x
    y = e.y
    canvas.create_line((lastX, lastY, x, y), width = selectedWidth, fill = color)
    lastX = x
    lastY = y


#method to select color
def newColor():
    global color
    color = colorchooser.askcolor()
    colorCanvas.config(bg = color[1])

#flashing for messages button
flash_delay = 750
bg_flash_colors = ("white", "red")
fg_flash_colors = ("black", "white")
def flashColor(object, color_index):
    object.config(background = bg_flash_colors[color_index])
    object.config(foreground = fg_flash_colors[color_index])
    root.after(flash_delay, flashColor, object, 1 - color_index)
root = tk.Tk()
root.withdraw()

#leave chatroom
def leaveChat():
    #leave the chatroom by letting server know you are exiting
    quit()

#create our gui
gui = tk.Tk()
gui.title('PictoChat The Rebirth')
gui.minsize(1200, 610)
#default color
color = "pink"

#populate our gui
#canvas object
canvas = Canvas(gui, bg = "gray", width = 960, height = 590)
canvas.place(x = 10, y = 10)
#buttons
#send button
button1 = tk.Button(gui, text = "Send Message", width =28, height = 8, fg = "green", activeforeground = "green")
button1.place(x = 980, y = 425)
#leave button
button2 = tk.Button(gui, text = "Leave Chat Room", width = 28, height = 2, fg = "red", activeforeground = "red", command = leaveChat)
button2.place(x = 980, y = 560)
#incoming messages button
button3 = tk.Button(gui, text = "Incoming Messages", width = 28, height = 4, activebackground = "red", activeforeground = "white")
button3.place(x = 980, y =13)
#select color button
button4 = tk.Button(gui, text = "Select A New Color", width = 28, height = 3, command= newColor)
button4.place(x = 980, y = 325)
#selected color display label
label1 = Label(gui, text = "Current Color")
label1.place(x = 1040, y= 240)
#label for brush size
label2 = Label(gui, text = "Brush Size")
label2.place(x = 1050, y = 100)
#selected color display viewable color
colorCanvas = Canvas(gui, bg = color, width = 203, height = 50)
colorCanvas.place(x = 980, y = 260)
#slider for size
w1 = Scale(gui, from_ = 1, to_ = 50, length = 200, orient = HORIZONTAL, command = updateSize)
w1.set(5)
w1.place(x = 980, y= 115)

#if we have messages run this line
flashColor(button3, 0)

#data for drawing
lastX, lastY = None,None
canvas.bind('<1>', startPaint)
#size
selectedWidth = w1.get()



#run our gui
gui.mainloop()
