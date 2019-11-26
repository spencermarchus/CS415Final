import time
import tkinter as tk
import threading
from tkinter import *


class Image_Display_GUI(threading.Thread):

    # this class represents the GUI which will display messages
    def __init__(self, peer):
        # call threading.Thread init because otherwise it just crashes (?)
        super(Image_Display_GUI, self).__init__()

        self.lastX = 0
        self.lastY = 0
        self.color = None
        self.selectedWidth = None

        # maintain peer reference
        self.peer = peer

        # make python stop being angry about declarations of self. variables
        self.flash_delay = None
        self.bg_flash_colors = None
        self.fg_flash_colors = None

        self.root = None

    # watch indefinitely for incoming messages
    def watch_for_incoming_messages(self):

        previous_state = []

        while True:
            try:
                self.peer.peer_list_lock.acquire()

                # if there has been an update to the message list. . . update the GUI!
                if self.peer.images_received != previous_state:

                    # TODO - update the gui!

                    previous_state = self.peer.images_received

                    pass

                time.sleep(.1) # we're busy waiting here for simplicity, so we don't want to hog CPU cycles

            finally:
                self.peer.peer_list_lock.release()


    # override the run method of Thread... readability of this is horrible, but we have to create all these instance
    # variables variables in run() to avoid errors inherent to Tkinter and threading
    def run(self):

        self.root = tk.Tk()
        self.root.withdraw()

        # create our gui
        self.gui = tk.Tk()
        self.gui.title('Messages Received')
        self.gui.minsize(980, 700)
        self.gui.maxsize(980, 700)

        # populate our gui
        # canvas object
        self.canvas = Canvas(self.gui, bg="gray", width=960, height=590)
        self.canvas.place(x=10, y=10)
        # buttons
        # send button
        self.button1 = tk.Button(self.gui, text="<<", width=10, height=2, fg="black", activeforeground="red")
        self.button1.place(x=400, y=630)
        # leave button
        self.button2 = tk.Button(self.gui, text=">>", width=10, height=2, fg="black", activeforeground="red")
        self.button2.place(x=500, y=630)

        # start a thread which constantly watches Peer object for new messages received

        # run our gui
        self.gui.mainloop()

