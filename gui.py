#imports
import tkinter as tk
import tkinter.colorchooser
from tkinter import *
import sys

#default color
color = "pink"

#methods
#method to select color
def newColor():
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
#selected color display viewable color
colorCanvas = Canvas(gui, bg = color, width = 203, height = 50)
colorCanvas.place(x = 980, y = 260)

#if we have messages run this line
flashColor(button3, 0)


#run our gui
gui.mainloop()
