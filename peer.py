import os
import socket
import sys
import threading
import datetime
import time
import _pickle as pickle
import gui
import gui2
import tkinter as tk
from tkinter import *
import datetime

host = ''


class Peer(threading.Thread):

    def __init__(self, config):

        super(Peer, self).__init__()

        self.port = config["LOCAL_PORT_NO"]
        self.local_ipv4 = socket.gethostbyname(socket.gethostname())
        self.server_ip = config["SERVER_IP"]
        self.server_port = config["SERVER_PORT"]

        self.images_received = []

        self.nickname = config['name']

        keep_alive = threading.Thread(name='keep_alive', target=self.ping_server_periodically, args=())
        keep_alive.setDaemon(True)
        keep_alive.start()

        self.peer_list_lock = threading.Lock()

        # maintain a flag to keep track of whether or not we need to exit all threads (used to exit gracefully)
        self.EXIT_FLAG = False

    def run(self):
        # Create a TCP socket to listen for connections
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Re-use the socket
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # bind the socket to a public host, and a port
        self.serverSocket.bind((host, self.port))

        self.serverSocket.listen(10)

        while True:
            # handle incoming connections

            # Establish the connection
            (clientSocket, client_address) = self.serverSocket.accept()

            d = threading.Thread(name='client',
                                 target=self.peer_thread, args=(clientSocket, client_address))
            d.setDaemon(True)  # can run in background, will not prevent program from closing
            d.start()

    def peer_thread(self, client_sock, client_addr):
        # handle receiving an image
        print('Handling message. . .')

        data = client_sock.recv(512000)

        data_loaded = pickle.loads(data)

        if data_loaded['type'] == 'IMAGE':
            img = data_loaded['data']
            sender = data_loaded['sender']

            print("Image recieved from " + sender)
            # save the image received to a list
            self.handle_image(img, sender)


        # if data_loaded['type'] == "MESSAGE":
        #     print("Message Recieved: " + data_loaded['data'] + " From: " + data_loaded['sender'])

    # send an image to all known peers
    def broadcast_image(self, img_pointer, sender_name):

        # get list of all active peers from server
        client_dict = self.get_active_peers()

        png = img_pointer.read(32768)

        img_pointer.close()

        if os.path.exists("outgoing.png"):
            os.remove("outgoing.png")
        if os.path.exists("outgoing.eps"):
            os.remove("outgoing.eps")

        self.handle_image(png, "Me")

        # iterate over peers and send the image in separate threads
        for p in client_dict:
            if p.get("port") != self.port:
                IP = p.get("local_ip")
                port = p.get("port")
                d = threading.Thread(name='client',
                                     target=self.send_image, args=(IP, port, png, sender_name))

                d.setDaemon(True)  # can run in background
                d.start()

                print("SENDING IMAGE TO " + IP + ':' + str(port))

    # image sending method that makes the socket connection and send the image
    def send_image(self, IP, port, png, sender_name):
        try:
            # create socket connection
            img_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            img_s.connect((IP, port))

            # print which peer is connected
            print('Connected to Peer: ' + sender_name)

            # send the message along with the type, image, and the sender
            msg = {'type': 'IMAGE', 'data': png, 'sender': sender_name}

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
        msg_s.send(pickle.dumps(msg))
        msg_s.close()

    # ping the server every few seconds to maintain alive status
    def ping_server_periodically(self):
        print('Pinging server. . .')
        while True:
            start = time.time()
            # open socket to server
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            s.connect((self.server_ip, self.server_port))

            msg = {'type': 'KEEP_ALIVE', 'port': self.port, 'nickname': self.nickname, 'local_ip': self.local_ipv4}

            # pickle the dict and send it to server
            s.send(pickle.dumps(msg))
            s.close()

            # wait about 15 seconds and do it again
            end = time.time()
            time.sleep(15 - (end - start))

    def leave_server(self):
        # tell server we're leaving
        msg = {'type': 'QUIT', 'port': self.port}

        # connect and say we're leaving
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.server_ip, self.server_port))
        s.send(pickle.dumps(msg))
        s.close()

    def get_active_peers(self):
        # get list of all active peers from server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.server_ip, self.server_port))
        print('Connected to server, requesting list of peers')

        request_dict = {'type': 'REQUEST_PEER_DICT'}

        data = pickle.dumps(request_dict)

        s.send(data)

        # wait for response

        ret_val = s.recv(4096)

        return_data = pickle.loads(ret_val)

        print("RECEIVED CLIENT DICT FROM SERVER. . .")
        print(return_data)
        return return_data

    def check_exit_flag(self):
        if self.EXIT_FLAG:
            self.leave_server()  # THIS MUST BE A SYNCHRONOUS CALL else we may not leave gracefully

        os._exit(1)


try:
    local_port = int(sys.argv[1])
    nickname = str(sys.argv[2])
except Exception:
    print('COULDNT READ COMMAND LINE ARGS')
    local_port = 4444
    nickname = '???'

cfg = {"LOCAL_PORT_NO": local_port, "SERVER_IP": '140.186.135.58', "SERVER_PORT": 9999, "name": nickname}

p = Peer(cfg)
p.setDaemon(True)  # allows use of CTRL+C to exit program

print("Peer started on port " + str(local_port))

# Peer object/thread created - now instantiate GUI

gui = gui.Canvas_GUI_Wrapper(p)
gui.setDaemon(True)

gui2 = gui2.Image_Display_GUI(p)
gui2.setDaemon(True)

# Start peer / GUI threads
p.start()
time.sleep(.5)
gui.start()
time.sleep(.5)
gui2.start()

# Prevent our main thread from exiting, since all other methods are daemonic
while True:
    time.sleep(1)
