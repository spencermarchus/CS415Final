import os
import socket
import sys
import threading
import datetime
import time
import _pickle as pickle
from gui import *
from gui2 import *
import tkinter as tk
from tkinter import *
import datetime
from ttkthemes import ThemedStyle
from tkinter import ttk
# host to listen for connections on
host = ''


class Peer(threading.Thread):

    def __init__(self, config):

        super(Peer, self).__init__()

        self.port = config["LOCAL_PORT_NO"]
        self.local_ipv4 = socket.gethostbyname(socket.gethostname())
        self.server_ip = config["SERVER_IP"]
        self.server_port = config["SERVER_PORT"]

        self.server_comms_lock = threading.Lock()

        self.images_received = []

        self.mode = config['mode']

        self.nickname = config['name']

        keep_alive = threading.Thread(name='keep_alive', target=self.ping_server_periodically, args=())
        keep_alive.setDaemon(True)
        keep_alive.start()

        self.peer_list_lock = threading.Lock()

    def run(self):
        # Create a TCP socket to listen for connections
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Re-use the socket
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # bind the socket to a public host, and a port
        self.serverSocket.bind((host, self.port))

        self.serverSocket.listen(10)

        while True:
            try:
                # handle incoming connections

                # Establish the connection
                (clientSocket, client_address) = self.serverSocket.accept()

                d = threading.Thread(name='client',
                                     target=self.peer_thread, args=(clientSocket, client_address))
                d.setDaemon(True)  # can run in background, will not prevent program from closing
                d.start()
            except Exception as e:
                print(e)

    def peer_thread(self, client_sock, client_addr):
        # handle receiving an image
        print('Handling message. . .')

        data = b''

        while True:
            part = client_sock.recv(4096)
            
            data += part
<<<<<<< HEAD

            if len(part) < 128:
=======
            if len(part) < 4096:
>>>>>>> 270b69496b48eee2ec1967adde81e771b4d88fda
                break


        data_loaded = pickle.loads(data)

        if data_loaded['type'] == 'IMAGE':
            img = data_loaded['data']
            sender = data_loaded['sender']

            print("Image recieved from " + sender)
            # save the image received to a list
            self.handle_image(img, sender)

        else:
            print("UNKNOWN MESSAGE TYPE RECEIVED: " + data_loaded)


    # send an image to all known peers
    def broadcast_image(self, img_pointer, sender_name):

        png = img_pointer.read(32768)

        img_pointer.close()

        try:
            if os.path.exists("outgoing.png"):
                os.remove("outgoing.png")
            if os.path.exists("outgoing.eps"):
                os.remove("outgoing.eps")
        except:
            pass

        if self.mode == 'INTERNET':
            # we are already in a separate thread, so simply send the image to the server for distribution
            self.handle_image(png, "Me")
            self.send_image(self.server_ip, self.server_port, png, sender_name, self.local_ipv4, 'INTERNET_MSG')
            print("SENDING IMAGE TO " + self.server_ip + ':' + str(self.server_port))

        if self.mode == 'LAN':

            # get list of all active peers from server
            client_dict = self.get_active_peers()

            self.handle_image(png, "Me")

            # iterate over peers and send the image in separate threads

            for p in client_dict:

                ip = p['local_ip']
                port = p['port']

                if ip + str(port) != self.local_ipv4 + str(self.port):
                    d = threading.Thread(name='client',
                                         target=self.send_image, args=(ip, port, png, sender_name))

                    d.setDaemon(True)  # can run in background
                    d.start()

                    print("SENDING IMAGE TO " + ip + ':' + str(port))

    # image sending method that makes the socket connection and sends the image
    def send_image(self, IP, port, png, sender_name, local_ip='', msg_type='IMAGE'):
        try:
            # create socket connection
            img_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            img_s.connect((IP, port))

            # print which peer is connected

            # send the message along with the type, image, and the sender
            msg = {'type': msg_type, 'data': png, 'sender': sender_name, 'port': self.port}

            if self.mode == "INTERNET":
                msg['local_ip'] = local_ip

            # pickle the dict and send it
            img_s.send(pickle.dumps(msg))
            img_s.close()

        except Exception as e:
            print(e)
            print('Could not make connection to peer!')

    # simply append the image, its sender, and a timestamp to our list in a tuple
    # watcher threads in GUI handle the rest
    def handle_image(self, png, sender):
        # get the current datetime
        now = datetime.datetime.now()
        # append with the image, sender, and the time in 12 hour format
        self.images_received.append((png, sender, str(now.strftime("%I:%M %p"))))

    # method to delete images from the peer's list.
    # gui2 was unable to edit the peer list so the method has to be here
    def delete_image(self, ind):
        # delete image at specific index
        del (self.images_received[ind])

    def broadcast_string(self, message):
        # get updated client dict
        self.get_active_peers()

        client_dict = self.get_active_peers()

        for p in client_dict:
            if p.get("port") != self.port:
                IP = p.get("local_ip")
                port = p.get("port")
                sender = p.get("name")

                print("SENDING TO " + IP + str(port))
                # spawn threads to send strings to all peers
                d = threading.Thread(name='client',
                                     target=self.send_chat, args=(IP, port, message, sender))
                d.setDaemon(True)  # can run in background
                d.start()

    def send_chat(self, IP, port, message, sender):
        msg_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        msg_s.connect((IP, port))
        print('Connected to Peer: ' + sender)
        print('Sent message: ' + message)
        msg = {'type': 'MESSAGE', 'data': message, 'sender': sender}
        # pickle the dict and send it
        msg_s.sendall(pickle.dumps(msg))
        msg_s.close()

    # ping the server every few seconds to maintain alive status
    def ping_server_periodically(self):
        print('Pinging server. . .')
        while True:
            try:
                self.server_comms_lock.acquire()
                start = time.time()
                # open socket to server
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                s.connect((self.server_ip, self.server_port))

                msg = {'type': 'KEEP_ALIVE', 'port': self.port, 'nickname': self.nickname, 'local_ip': self.local_ipv4}

                # pickle the dict and send it to server
                s.sendall(pickle.dumps(msg))
                s.close()

                # wait and do it again
                end = time.time()
                self.server_comms_lock.release()

                if self.mode == "INTERNET":
                    self.check_for_messages_over_network()

                time.sleep(2.5)

            except Exception as e:
                print(e)

    # pings a central server and checks whether or not there are any messages for this peer
    def check_for_messages_over_network(self):

        # while True:
        # try:
        self.server_comms_lock.acquire()
        start = time.time()

        # connect to server and check if we have any messages waiting
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        s.connect((self.server_ip, self.server_port))

        msg = {'type': 'MSG_CHECK', 'port': self.port, 'local_ip': self.local_ipv4}

        data = pickle.dumps(msg)

        s.sendall(data)

        data = b''

        while True:
            part = s.recv(128)
            data += part

            if len(part) < 128:
                break

        return_data = pickle.loads(data)['data']

        for tup in return_data:
            sender = tup[0]
            png = tup[1]

            self.handle_image(png, sender)

        # except Exception as e:
        #     print(e, " REE")
        #     pass
        #
        # finally:
        end = time.time()
        self.server_comms_lock.release()
        time.sleep(3)

    def leave_server(self):
        # tell server we're leaving
        msg = {'type': 'QUIT', 'port': self.port}

        # connect and say we're leaving
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.server_ip, self.server_port))
        s.sendall(pickle.dumps(msg))
        s.close()

    def get_active_peers(self):
        # get list of all active peers from server
        self.server_comms_lock.acquire()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.server_ip, self.server_port))
        print('Connected to server, requesting list of peers')

        request_dict = {'type': 'REQUEST_PEER_DICT'}

        data = pickle.dumps(request_dict)

        # send all data thru socket
        s.sendall(data)

        # wait for response

        data = b''

        while True:
            part = s.recv(128)
            data += part

            if len(part) < 128:
                data += part
                break

        return_data = pickle.loads(data)

        print("RECEIVED CLIENT DICT FROM SERVER. . .")
        print(return_data)
        self.server_comms_lock.release()
        return return_data

    def check_exit_flag(self):
        if self.EXIT_FLAG:
            self.leave_server()  # THIS MUST BE A SYNCHRONOUS CALL else we may not leave gracefully

        os._exit(1)


try:
    local_port = int(sys.argv[1])
except Exception:
    print('COULDNT READ COMMAND LINE ARG')
    local_port = 4444

# Display a welcome GUI

gui = tk.Tk()

nickname = ''

# Start a GUI which welcomes the user and prompts for a nickname as well as the chat room to join
class StartGUI:

    def __init__(self):

        pass

    def exit_LAN(self):
        global mode
        mode = 'LAN'

        global nickname
        nickname = self.input.get()

        if nickname is not None and nickname != '':
            global gui
            gui.destroy()

        else:
            self.err_label.config(text="ERROR: Please enter a nickname!")

    def exit_INTERNET(self):
        global mode
        mode = 'INTERNET'

        global gui
<<<<<<< HEAD
=======
        
>>>>>>> 270b69496b48eee2ec1967adde81e771b4d88fda

        global nickname
        nickname = self.input.get()

        if nickname is not None and nickname != '':

            gui.destroy()

        else:
            self.err_label.config(text="ERROR: Please enter a nickname!")

    def run(self):
        global gui

        # create our gui
        tabs = ttk.Notebook(gui)
        tabs.pack(expand=1, fill="both")

        gui.title('PictoChat The Rebirth')
        gui.minsize(400, 250)
        gui.maxsize(400, 250)

        # buttons, labels, and fun stuff
        style = ThemedStyle(gui)
        style.set_theme("black")

        button1 = ttk.Button(gui, text="Join LAN Chat Room",  command=self.exit_LAN)
        button1.place(x=60, y=155)


        button2 = ttk.Button(gui, text="Join Internet Chat Room",  command=self.exit_INTERNET)
        button2.place(x=200, y=155)

        label1 = ttk.Label(gui, text="Welcome to PictoChat: The Rebirth!")
        label1.config(font=("Arial", 15))
        label1.place(x=40, y=40)

        label2 = ttk.Label(gui, text="Enter a nickname:")
        label2.config(font=("Arial", 11))
        label2.place(x=40, y=110)

        self.err_label = ttk.Label(gui, text='', foreground='red')
        self.err_label.place(x=40, y=75)

        self.input = ttk.Entry(gui, width=30)
        self.input.place(x=175, y=110)

        # run our gui
        gui.mainloop()

# global variable that GUI modifies
mode = ''

# Welcome the user
g = StartGUI()
g.run()

del gui

# User closed out of welcome GUI - don't start anything else
if mode == '':
    exit()

if nickname == '':
    # user somehow exited without picking a nickname
    nickname = "???"

# else... continue

print("STARTING PEER IN " + mode + " MODE - Nickname: " + nickname)

cfg = {"LOCAL_PORT_NO": local_port, "SERVER_IP": '140.186.135.58', "SERVER_PORT": 9998, "name": nickname, "mode": mode}

p = Peer(cfg)
p.setDaemon(True)  # allows use of CTRL+C to exit program

print("Peer started on port " + str(local_port))

# Peer object/thread created - now instantiate GUI

gui1 = Canvas_GUI_Wrapper(p)
gui1.setDaemon(True)

gui2 = Image_Display_GUI(p)
gui2.setDaemon(True)

# Start peer / GUI threads
p.start()
time.sleep(.5)
gui1.start()
time.sleep(.5)
gui2.start()

# Prevent our main thread from exiting
while True:
    time.sleep(1)
