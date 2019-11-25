import socket
import threading
import datetime
import time
import _pickle as pickle
import gui

# imports
import tkinter as tk
import tkinter.colorchooser as colorchooser
from tkinter import *

host = '127.0.0.1'


class Peer(threading.Thread):

    def __init__(self, config):

        super(Peer, self).__init__()

        self.port = config["LOCAL_PORT_NO"]

        self.server_ip = config["SERVER_IP"]
        self.server_port = config["SERVER_PORT"]




        keep_alive = threading.Thread(name='keep_alive', target = self.ping_server_periodically, args=())
        keep_alive.setDaemon(True)
        keep_alive.start()


        time.sleep(2)

        # self.broadcast_string('REE')
        # self.broadcast_image("placeholder")


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
            d.setDaemon(True) # can run in background, will not prevent program from closing
            d.start()


    def peer_thread(self, client_sock, client_addr):
        # do stuff
        # generally, here we will handle receiving something like an image
        print('Handling message. . .')

        data = client_sock.recv(4096)

        data_loaded = pickle.loads(data)

        if data_loaded['type'] == 'IMAGE':
            img = data_loaded['data']
            with open('tst' + str(self.port) + '.png', 'wb') as image:
                image.write(img)
            print("Message Recieved: " + 'tst' + str(self.port) + ".png From " + data_loaded['sender'])

        if data_loaded['type'] == "MESSAGE":
            print("Message Recieved: " + data_loaded['data'] + " From: " + data_loaded['sender'])


    # send an image to all peers
    def broadcast_image(self, img):
        img = "/Users/mckennaobrien/Documents/My Pictures/Test.png"
        try:
            img = open(img, "rb").read()
        except IOError:
            pass

        # get list of all active peers from server
        client_dict = self.get_active_peers()

        # iterate over peers and send the image in separate threads
        for p in client_dict:
            if p.get("port") != self.port:
                IP = p.get("ip")
                port = p.get("port")
                sender = p.get("name")
                d = threading.Thread(name='client',
                                     target=self.send_image, args=(IP, port, img, sender))
                d.setDaemon(True)  # can run in background
                d.start()

    def send_image(self, IP, port, img, sender):
        img_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        img_s.connect((IP, port))

        print('Connected to Peer: ' + sender)

        msg = {'type': 'IMAGE', 'data': img, 'sender': sender}

        # pickle the dict and send it
        img_s.send(pickle.dumps(msg))
        img_s.close()


    def broadcast_string(self, message):
        # get updated client dict
        self.get_active_peers()

        client_dict = self.get_active_peers()

        for p in client_dict:
            if p.get("port") != self.port:
                IP = p.get("ip")
                port = p.get("port")
                sender = p.get("name")
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


    # ping the server every 30 seconds to maintain alive status
    def ping_server_periodically(self):

        while True:
            start = time.time()
            # open socket to server and ensure timeout << 30 seconds
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            s.connect((self.server_ip, self.server_port))

            print('Connected to server')

            msg = {'type': 'KEEP_ALIVE', 'port':self.port, 'nickname':'Spencer'}

            # pickle the dict and send it to server
            s.send(pickle.dumps(msg))
            s.close()

            # send a ping message to tell server we are alive

            # close connection

            # wait about 15 seconds and do it again forever
            end = time.time()
            time.sleep(15-(end-start))

    def get_active_peers(self):
        # get list of all active peers from server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.server_ip, self.server_port))
        print('Connected to server, requesting list of peers')

        request_dict = {'type': 'REQUEST_PEER_DICT'}

        data = pickle.dumps(request_dict)

        s.send(data)

        ret_val = s.recv(4096)

        return_data = pickle.loads(ret_val)

        print("RECEIVED CLIENT DICT FROM SERVER. . .")
        print(return_data)
        return return_data

cfg = {"LOCAL_PORT_NO": 4444, "SERVER_IP": '127.0.0.1', "SERVER_PORT": 9999}

p = Peer(cfg)
p.setDaemon(True) # allows use of CTRL+C to exit program

# Peer object/thread created - now instantiate GUI

gui = gui.Canvas_GUI_Wrapper(p)
gui.setDaemon(True)

# GUI now created - TODO - point GUI callbacks at Peer methods

# Start peer / GUI threads
p.start()
gui.start()

# Prevent our main thread from exiting, since all other methods are daemonic
while True:
    time.sleep(100)

