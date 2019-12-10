#!/usr/bin/env python

# this is a starter server implementation - this code is untested and will be buggy / incomplete for now

import socket
import threading
import datetime
import time
import _pickle as pickle

host = ''
port = 9998


# only one thread can modify the dict at one time


class User:

    def __init__(self, ip, local_ip, port_no, name):
        self.nickname = name
        self.ip = ip
        self.port = port_no
        self.local_ip = local_ip  # represents a remote peer's IP on its local network
        self.timestamp = datetime.datetime.now()  # current date and time


class Server(threading.Thread):

    def __init__(self, config={}):

        super(Server, self).__init__()

        self.CLIENT_TIMEOUT_MINS = 2

        # Create a TCP socket
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.client_dict_lock = threading.Lock()

        # Re-use the socket
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # when operating in centralized-server mode, maintain mailboxes
        self.mailboxes = {}

        # bind the socket to a public host, and a port
        self.serverSocket.bind((host, port))

        self.serverSocket.listen(50)  # become a server socket
        self.clients = {}

    def run(self):

        # start a thread which periodically checks the list of peers to ensure they are active
        threading.Thread(target=self.prune_dict_thread).start()

        print('Server started!')

        while True:
            # Establish the connection
            (clientSocket, client_address) = self.serverSocket.accept()

            d = threading.Thread(name='client',
                                 target=self.server_thread, args=(clientSocket, client_address))
            d.setDaemon(True)
            d.start()

    # this would get called whenever a client pings the server to tell it that it's alive
    def update_peer(self, client_info):

        # if user is unknown, add them to the list all the same

        # again, if user is unknown, respond with OK message telling user they have connected

        try:
            ip_addr = client_info['IP']
            port_no = client_info['PORT_NO']
            nickname = client_info['nickname']
            local_ip = client_info['local_ip']

            # create a mailbox for this user

            if ip_addr == local_ip:
                # operating in LAN mode but using mailboxes?
                index = local_ip + ':' + str(port_no)

            else:
                # operating over internet
                index = ip_addr + ':' + str(port_no)

            if self.mailboxes.get(index) is None:
                self.mailboxes[index] = []  # create mailbox for user

            index = ip_addr + ':' + str(port_no)

            # acquire lock to make sure we don't corrupt dict - this runs in little time, no expected perf impact
            self.client_dict_lock.acquire()

            # client dict will be indexed by "IP:port_no" - replace with a new Peer object with current timestamp
            self.clients[index] = User(ip_addr, local_ip, port_no, nickname)

            print('\nPeer updated successfully!')
            print(self.clients)

        finally:
            # release lock
            self.client_dict_lock.release()

    # when a peer requests a list of all curently connected peers, call this method
    def send_list_of_all_peers_to_peer(self, peer_socket):

        self.client_dict_lock.acquire()

        return_list = []

        try:
            for key in self.clients:
                user = self.clients[key]
                ip = user.ip
                port = user.port
                name = user.nickname
                local_ip = user.local_ip
                return_list.append({'ip': ip, 'local_ip': local_ip, 'port': port, 'name': name})

            # send dict to peer's socket
            response = pickle.dumps(return_list)
            peer_socket.sendall(response)

        finally:

            self.client_dict_lock.release()

    def server_thread(self, clientSocket, client_addr):
        print('\nHandling client connection. . .')

        # get the request from browser
        data = b''

        while True:
            part = clientSocket.recv(4096)
            data += part

            if len(part) < 4096:
                data += part
                break

        info = pickle.loads(data)

        # str_data = data.decode()

        # the connected client's IP addr
        h, p = clientSocket.getpeername()

        print('\nMessage from client: ')
        print(info)

        req_type = info['type']

        if req_type == 'KEEP_ALIVE':
            # update the time which we have last seen this client
            client_info = {'IP': h, 'PORT_NO': info['port'], 'nickname': info['nickname'], 'local_ip': info['local_ip']}
            self.update_peer(client_info)

        if req_type == 'REQUEST_PEER_DICT':
            # respond with directory of all active clients
            self.send_list_of_all_peers_to_peer(clientSocket)

        if req_type == 'QUIT':

            # remove client from peers dict
            index = h+':'+str(info['port'])
            del self.clients[index]

            print('Removed '+index+' due to QUIT command. . .')

        if req_type == "MSG_CHECK":
            # check if the peer has any messages waiting
            # assume that the peer is not on the same LAN as the server
            local_ip = info['local_ip']
            ip = h
            port = info['port']

            if ip == local_ip:
                # operating in internet mode on LAN for some reason - refer to peer using its local IP
                index = local_ip+':'+str(port)

            else:
                # truly operating over the internet - refer to peer using IP not local IP
                index = ip + ':' + str(port)

            if self.mailboxes.get(index) is not None:
                return_data = {'data': []}
                for tup in self.mailboxes[index]:
                    print("\nRETURNING IMAGE\n")
                    return_data['data'].append((tup[0], tup[1]))

                self.mailboxes[index] = []  # messages will be sent to user, so remove them from central server

                data = pickle.dumps(return_data)
                clientSocket.sendall(data)

            else:
                return # take no further action



        if req_type == "INTERNET_MSG":
            # message is to be sent to clients over network
            ip = h
            local_ip = info['local_ip']
            port = info['port']
            sender = info['sender']
            png = info['data']

            if ip == local_ip:
                # operating in internet mode on LAN for some reason but continue
                index = local_ip + ':' + str(port)

            else:
                # truly operating over the internet - use IP not Local IP
                index = ip + ':' + str(port)

            for key in self.mailboxes:
                if key != index: # don't send to yourself
                    self.mailboxes[key].append((sender, png))


        clientSocket.close()



    # this is meant to be a thread that runs indefinitely
    # in general, loop approximately every few seconds and remove peer if a given peer is not active
    def prune_dict_thread(self):

        while True:
            try:
                start = time.time()

                # list of dict keys to remove
                indices_to_remove = []

                self.client_dict_lock.acquire()

                for key in self.clients:

                    # if client has not pinged in last X time, remove from client list
                    timedelta = datetime.datetime.now() - self.clients[key].timestamp

                    if timedelta > datetime.timedelta(
                            minutes=self.CLIENT_TIMEOUT_MINS):  # remove this peer from active list
                        print('REMOVING peer ' + str(key) + ' from directory due to inactivity')
                        indices_to_remove.append(key)

                # delete clients that need to get deleted
                for key in indices_to_remove:
                    del self.clients[key]

                self.client_dict_lock.release()

                seconds_to_sleep = 5 - (time.time() - start)

                # sleep thread for about 5 seconds, less however long it took to do above operations

                time.sleep(seconds_to_sleep)

            except Exception as e:
                print(e)
                continue  # try again


# start server
s = Server()
s.setDaemon(True)  # allows use of CTRL+C to exit program
s.start()

# sleep main thread indefinitely so program doesn't exit
while True:
    time.sleep(10000)
