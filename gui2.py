import io
import os
import datetime
import time
import tkinter as tk
import threading
from tkinter import *
from PIL import Image, ImageTk


class Image_Display_GUI(threading.Thread):

    # this class represents the GUI which will display messages
    def __init__(self, peer):
        # call threading.Thread init because otherwise it just crashes (?)
        super(Image_Display_GUI, self).__init__()

        # maintain peer reference
        self.peer = peer

        self.root = None

        self.msg_counter = 0

    # watch indefinitely for incoming messages
    def watch_for_incoming_messages(self):

        previous_state = 0
        previous_selection = -1

        # keep track of whether or not we have received an update and need to re-display the image
        needs_updated_flag = False

        while True:
            try:
                self.peer.peer_list_lock.acquire()

                selection = -1
                try:
                    selection = self.Listbox.curselection()[0]
                except Exception as e:
                    pass

                # if there are images to display, and selection in Listbox has changed, or we need an update. . .
                if len(self.peer.images_received) > 0 and (selection != previous_selection or needs_updated_flag):
                    previous_selection = selection

                    # maintain reference to raw PNG data
                    raw_png = self.peer.images_received[selection][0]

                    # create PIL Image object from raw data and resize for GUI
                    png_img = Image.open(io.BytesIO(raw_png)).resize((960, 590), Image.ANTIALIAS)

                    # create PhotoImage object from Image to display to GUI
                    photoimg = ImageTk.PhotoImage(png_img, master=self.canvas)

                    self.canvas.create_image((2, 2), anchor=NW, image=photoimg)

                    needs_updated_flag = False

                # if there has been an update to the message list, update the listbox
                images_list_len = len(self.peer.images_received)
                if images_list_len != previous_state:

                    previous_state = images_list_len

                    # if user has not made a selection in the list box, update gui to display latest chat
                    needs_updated_flag = images_list_len != 0

                    # refresh the listbox contents
                    self.Listbox.delete(0, 'end')

                    for i, img in enumerate(self.peer.images_received):
                        # img[1] is the nickname of sender, or just "Me" if the user is the sender
                        # img[2] is the date of when the message was received
                        self.Listbox.insert(END, img[2] + ' - Chat sent by ' + img[1])

                    # attempt to preserve the selected item from before update
                    try:
                        self.Listbox.selection_set(first=previous_selection)
                    except Exception as e:
                        self.Listbox.selection_set(first='end')



            except Exception as e:
                print(e)
                pass

            finally:

                self.peer.peer_list_lock.release()

                if not needs_updated_flag:
                    time.sleep(.05)  # sleep a bit if we don't need to do an update in the next loop iteration

    def delete_selected_msg(self):
        selection = -1
        try:
            # get the user's cursor selection
            selection = self.Listbox.curselection()[0]
        except Exception as e:
            pass
        # delete the selection from the listbox
        self.Listbox.delete(selection)
        # delete the selection from the peer's list of images
        self.peer.delete_image(selection)

        if self.Listbox.size() == 0:
            self.canvas.delete('all')


    # override the run method of Thread... readability of this is horrible, but we have to create all the instance
    # variables variables in run() to avoid errors inherent to Tkinter and threading
    def run(self):

        self.root = tk.Tk()
        self.root.withdraw()

        # create our gui
        self.gui = tk.Tk()
        self.gui.title('Messages Received')
        self.gui.minsize(1200, 610)
        self.gui.maxsize(1200, 610)

        # populate our gui
        # canvas object
        self.canvas = Canvas(self.gui, bg="gray", width=960, height=590)
        self.canvas.place(x=10, y=10)

        # label for the listbox
        self.Label1 = Label(self.gui, text="Messages")
        self.Label1.place(x=1050, y=10)
        # listbox to store our given messages
        self.Listbox = Listbox(self.gui, width=31, height=30)
        self.Listbox.place(x=980, y=48)
        # scrollbar for listbox (unlikely its necessary but good for continuity)
        self.Scrollbar1 = Scrollbar(self.gui, orient="vertical")
        self.Scrollbar1.place(x=1175, y=48)
        # button to delete an entry from the listbox
        self.Button1 = Button(self.gui, text="Delete Message", width=28, height=3,
                              command=self.delete_selected_msg)
        self.Button1.place(x=980, y=545)

        # start a thread which constantly watches for incoming messages and updates listbox/gui
        watcher = threading.Thread(target=self.watch_for_incoming_messages)
        watcher.setDaemon(True)
        watcher.start()

        # run our gui
        self.gui.mainloop()
