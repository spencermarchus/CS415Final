import io
import time
import tkinter as tk
import threading
from tkinter import *
from mttkinter import mtTkinter
from PIL import Image


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
        while True:
            try:
                self.peer.peer_list_lock.acquire()

                selection = -1
                try:
                    selection = self.Listbox.curselection()[0]
                except Exception as e:
                    i = 1

                # if selection in Listbox has changed. . .
                if selection != previous_selection:
                    previous_selection = selection
                    self.png = self.peer.images_received[selection][0]
                    f = open('received\\recv.png', 'wb')
                    f.write(self.png)
                    f.close()
                    img = PhotoImage(file='received\\recv.png', master=self.canvas)
                    self.canvas.create_image((960 / 2, 590 / 2), image=img)
                    print('UPDATED CANVAS')

                # if there has been an update to the message list, update the listbox
                images_list_len = len(self.peer.images_received)
                if images_list_len != previous_state:
                    print('UPDATING MESSAGES RECEIVED')
                    previous_state += 1 # in case we somehow receive two images at once, increment only by one and process next image in next loop
                    # this ^ needs to become more robust as we allow for deleting messages
                    sender = self.peer.images_received[-1][1]

                    self.Listbox.insert(END, str(images_list_len) + " - Message from " + sender)
                    self.msg_counter += 1

            except Exception as e:
                print(e)
                pass

            finally:
                self.peer.peer_list_lock.release()
                time.sleep(.02)  # we're busy waiting here for simplicity (no dealing with events), so we don't want to hog CPU cycles

    def delete_selected_msg(self):
        # TODO
        pass

    # override the run method of Thread... readability of this is horrible, but we have to create all these instance
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
        self.Label1 = Label(self.gui, text="Incoming Messages")
        self.Label1.place(x=1025, y=10)
        # listbox to store our given messages
        self.Listbox = Listbox(self.gui, width=31, height=30)
        self.Listbox.place(x=980, y=48)
        # scrollbar for listbox (unlikely its necessary but good for continuity)
        self.Scrollbar1 = Scrollbar(self.gui, orient="vertical")
        self.Scrollbar1.place(x=1175, y=48)
        # button to delete an entry from the listbox
        self.Button1 = Button(self.gui, text="Delete Message", width=28, height=3,
                              command=self.watch_for_incoming_messages)
        self.Button1.place(x=980, y=545)

        # buttons

        # placeholder buttons (these should be removed but i am keeping for safety
        # send button
        # self.button1 = tk.Button(self.gui, text="<<", width=10, height=2, fg="black", activeforeground="red")
        # self.button1.place(x=400, y=630)
        # leave button
        # self.button2 = tk.Button(self.gui, text=">>", width=10, height=2, fg="black", activeforeground="red")
        # self.button2.place(x=500, y=630)

        # start a thread which constantly watches Peer object for new messages received
        watcher = threading.Thread(target=self.watch_for_incoming_messages)
        watcher.setDaemon(True)
        watcher.start()

        # run our gui
        self.gui.mainloop()
