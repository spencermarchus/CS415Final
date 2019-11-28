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

host = '127.0.0.1'


class Peer(threading.Thread):

    def __init__(self, config):

        super(Peer, self).__init__()

        self.port = config["LOCAL_PORT_NO"]

        self.server_ip = config["SERVER_IP"]
        self.server_port = config["SERVER_PORT"]

        self.images_received = []

        self.nickname = config['name']

        keep_alive = threading.Thread(name='keep_alive', target=self.ping_server_periodically, args=())
        keep_alive.setDaemon(True)
        keep_alive.start()

        self.peer_list_lock = threading.Lock()

        time.sleep(2)


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
        # do stuff
        # generally, here we will handle receiving something like an image
        print('Handling message. . .')

        data = client_sock.recv(512000)

        data_loaded = pickle.loads(data)

        if data_loaded['type'] == 'IMAGE':
            img = data_loaded['data']
            sender = data_loaded['sender']
            # with open('tst' + str(self.port) + '.png', 'wb') as image:
            #     image.write(img)
            print("Image recieved from " + sender)
            self.handle_image(img, sender)

        if data_loaded['type'] == "MESSAGE":
            print("Message Recieved: " + data_loaded['data'] + " From: " + data_loaded['sender'])

    # send an image to all known peers
    def broadcast_image(self, img_pointer, sender_name):

        # get list of all active peers from server
        client_dict = self.get_active_peers()

        png = img_pointer.read(512000)

        img_pointer.close()

        # self.images_received.append((png, sender))

        # iterate over peers and send the image in separate threads
        for p in client_dict:
            if p.get("port") != self.port:
                IP = p.get("ip")
                port = p.get("port")
                sender = p.get("name")
                d = threading.Thread(name='client',
                                     target=self.send_image, args=(IP, port, png, sender_name))
                d.setDaemon(True)  # can run in background
                d.start()

    def send_image(self, IP, port, png, sender_name):
        try:
            img_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            img_s.connect((IP, port))

            print('Connected to Peer: ' + sender_name)

            msg = {'type': 'IMAGE', 'data': png, 'sender': sender_name}

            # pickle the dict and send it
            img_s.send(pickle.dumps(msg))
            img_s.close()

        except Exception as e:
            print(e)
            print('Could not make connection to peer!')

    # simply append the image and its sender to our list in a tuple
    # watcher threads in GUI handle the rest
    def handle_image(self, png, sender):
        self.images_received.append((png, sender))

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

    # ping the server every few seconds to maintain alive status
    def ping_server_periodically(self):
        print('Pinging server. . .')
        while True:
            start = time.time()
            # open socket to server and ensure timeout << 30 seconds
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            s.connect((self.server_ip, self.server_port))

            msg = {'type': 'KEEP_ALIVE', 'port': self.port, 'nickname': self.nickname}

            # pickle the dict and send it to server
            s.send(pickle.dumps(msg))
            s.close()

            # wait about 15 seconds and do it again
            end = time.time()
            time.sleep(15 - (end - start))

    def leave_server(self):
        # TODO - tell server we're leaving
        pass

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


try:
    local_port = int(sys.argv[1])
    nickname = str(sys.argv[2])
except Exception:
    print('COULDNT READ PORT VALUE FROM BATCH FILE')
    local_port = 4444
    nickname = 'TEST'

cfg = {"LOCAL_PORT_NO": local_port, "SERVER_IP": '127.0.0.1', "SERVER_PORT": 9999, "name": nickname}

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
gui.start()
gui2.start()

# Prevent our main thread from exiting, since all other methods are daemonic
while True:
    time.sleep(100000)
