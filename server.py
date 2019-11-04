#!/usr/bin/env python

# this is a starter server implementation - this code is untested and will be buggy / incomplete for now

import socket
import threading
import datetime
import time

host = '127.0.0.1'
port = 9999


# only one thread can modify the dict at one time


class User:

    def __init__(self, ip, port_no, name):
        self.nickname = name
        self.ip = ip
        self.port = port_no
        self.timestamp = datetime.datetime  # current date and time


class Server:

    def __init__(self, config={}):

        self.CLIENT_TIMEOUT_MINS = 2

        # Create a TCP socket
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.client_dict_lock = threading.Lock()

        # Re-use the socket
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # bind the socket to a public host, and a port
        self.serverSocket.bind((host, port))

        self.serverSocket.listen(50)  # become a server socket
        self.clients = {}

        # start a thread which periodically checks the list of peers to ensure they are active
        threading.start_new_thread(self.prune_dict_thread, ())

        while True:
            # Establish the connection
            (clientSocket, client_address) = self.serverSocket.accept()

            d = threading.Thread(name='client',
                                 target=self.server_thread, args=(clientSocket, client_address))
            d.setDaemon(True)
            d.start()


    # this would get called whenever a client pings the server to tell it that it's alive
    def update_peer(self, client_info):
        # acquire lock to make sure we don't corrupt dict - this runs in little time, no expected perf impact
        self.client_dict_lock.acquire()

        # if user is unknown, add them to the list all the same

        # again, if user is unknown, respond with OK message telling user they have connected

        try:
            ip_addr = client_info['IP']
            port_no = client_info['PORT_NO']

            index = ip_addr + ':' + str(port_no)

            # client dict will be indexed by "IP:port_no" - replace with a new Peer object with current timestamp
            self.clients[index] = User(ip_addr, port_no)

        finally:
            # release lock
            self.client_dict_lock.release()

    # when a peer requests a list of all curently connected peers, call this method
    def send_list_of_all_peers_to_peer(self, peer_socket):

        self.client_dict_lock.acquire()

        str_clients = 'PEERLIST;'

        try:
            for key in self.clients:
                str_clients += key + ';'

            # send string to peer's socket

        finally:

            self.client_dict_lock.release()


    def server_thread(self, clientSocket, client_addr):
        print('thread started')

        # get the request from browser
        data = clientSocket.recv(4096)

        str_data = str(data)

        # do something with the info

        # if request is to update a client's last seen time, do that

        pass

    # this is meant to be a thread that runs indefinitely
    # in general, loop approximately every 2 minutes and remove peer if a given peer is not active
    def prune_dict_thread(self):

        while True:

            start = time.time()

            # list of dict keys to remove
            indices_to_remove = []

            for key, val in self.clients:

                # if client has not pinged in last X time, remove from client list
                timedelta = val.timestamp - datetime.datetime

                if timedelta > timedelta(minutes=self.CLIENT_TIMEOUT_MINS):  # remove this peer from active list

                    indices_to_remove.append(key)

            # delete clients that need to get deleted
            for key in indices_to_remove:
                del self.clients[key]

            end = time.time()
            seconds_to_sleep = 120 - (end - start)

            # sleep thread for 2 minutes less however long it took to do above operations
            time.sleep(seconds_to_sleep)


# start server
s = Server()
