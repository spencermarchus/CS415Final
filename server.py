"""
CS415 Final - PictoChat: The Rebirth
Server
Represents a central server on the network - used as a directory and/or mailbox

Spencer Marchus
McKenna O'Brien
Cameron Ethier
Jack Olson
"""

import socket
import threading
import datetime
import time
import _pickle as pickle
import signal
import sys

host = ''
port = 9001

localhost = '127.0.0.1'


# Represents a user connected to the network
class User:

    def __init__(self, ip, local_ip, port_no, name, mode):
        self.nickname = name
        self.ip = ip
        self.port = port_no
        self.local_ip = local_ip  # represents a remote peer's IP on its local network
        self.timestamp = datetime.datetime.now()  # current date and time
        self.mode = mode


# Server thread - listens for connections from others on localhost (if possible) and
class Server(threading.Thread):

    def __init__(self, config={}):
        try:
            super(Server, self).__init__()

            # on shutdown, release the sockets
            signal.signal(signal.SIGINT, self.signal_handler)

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

            # try to listen on localhost, just in case
            self.local_socket_success = False
            try:
                self.localSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.localSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.localSocket.bind((localhost, port))
                self.localSocket.listen(50)
                self.local_socket_success = True
            except Exception as e:
                print("Exception initializing localhost socket. . .")
                pass


        except Exception as e:
            print(e)
            print("ERROR ON STARTUP, exiting. . .")
            self.signal_handler()

    # on exit, release sockets and exit
    def signal_handler(self, sig, frame):
        try:
            print('You pressed Ctrl+C!')
            print("CLOSING SOCKETS. . .")
            self.serverSocket.close()
            self.localSocket.close()
        except Exception as e:
            pass
        finally:
            sys.exit(0)

    def run(self):

        # start a thread which periodically checks the list of peers to ensure they are active
        threading.Thread(target=self.prune_dict_thread).start()

        # start a thread which listens for requests on localhost, just in case
        if self.local_socket_success:
            threading.Thread(target=self.listen_on_localhost).start()

        print('Server started on port ' + str(port))

        while True:

            try:
                # Establish the connection
                (clientSocket, client_address) = self.serverSocket.accept()

                d = threading.Thread(name='client',
                                     target=self.server_thread, args=(clientSocket,))
                d.setDaemon(True)
                d.start()

            except Exception as e:
                print(e)

    def listen_on_localhost(self):

        while True:

            try:
                # Establish the connection
                (clientSocket, client_address) = self.localSocket.accept()

                d = threading.Thread(name='client',
                                     target=self.server_thread, args=(clientSocket,))

                d.setDaemon(True)
                d.start()

            except Exception as e:
                print(e)

    # this would get called whenever a client pings the server to tell it that it's alive
    def update_peer(self, client_info):

        # if user is unknown, add them to the list
        # if user is known, update their info

        try:
            ip_addr = client_info['IP']
            port_no = client_info['PORT_NO']
            nickname = client_info['nickname']
            local_ip = client_info['local_ip']
            mode = client_info['mode']

            # create a mailbox for this user

            if mode == 'LAN':
                # operating in LAN mode - refer to local IP
                index = local_ip + ':' + str(port_no)

            else:
                # operating over internet - can use public IP
                index = ip_addr + ':' + str(port_no)

            # create a mailbox for INTERNET peer if needed
            if mode == 'INTERNET':
                if self.mailboxes.get(index) is None:
                    self.mailboxes[index] = []  # create mailbox for user

            # acquire lock to make sure we don't corrupt dict - this runs in little time, no expected perf impact
            self.client_dict_lock.acquire()

            # client dict will be indexed by "IP:port_no" - replace with a new Peer object with current timestamp
            self.clients[index] = User(ip_addr, local_ip, port_no, nickname, mode)

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

    def server_thread(self, clientSocket):
        print('\nHandling client connection. . .')

        # get the request from browser
        data = b''

        while True:
            part = clientSocket.recv(128)
            data += part

            if len(part) < 128:
                data += part
                break

        info = pickle.loads(data)

        # str_data = data.decode()

        # the connected client's IP addr
        h, p = clientSocket.getpeername()

        if info['type'] not in ['IMAGE', 'INTERNET_MSG']:
            print('\nMessage from client: ')
            print(info)

        else:
            print("Message from client: IMAGE FILE")

        req_type = info['type']

        if req_type == 'TEST_CONNECT':
            return_data = {'THIS CONTENT DOES NOT MATTER': -1}
            clientSocket.sendall(pickle.dumps(return_data))

        if req_type == 'KEEP_ALIVE':
            # update the time which we have last seen this client
            client_info = {'IP': h, 'PORT_NO': info['port'], 'nickname': info['nickname'], 'local_ip': info['local_ip'],
                           'mode': info['mode']}
            self.update_peer(client_info)

        if req_type == 'REQUEST_PEER_DICT':
            # respond with directory of all active clients
            self.send_list_of_all_peers_to_peer(clientSocket)

        if req_type == 'QUIT':

            for key in self.clients:
                print(key)

            # remove client from peers dict
            index = h + ':' + str(info['port'])

            print(self.clients)

            # try to delete the user's mailbox - should succeed if on INTERNET mode
            try:
                del self.mailboxes[index]
                print('Removed ' + index + '\'s mailbox due to QUIT command. . .')
            finally:
                pass

            try:
                # this should succeed for INTERNET or LAN mode. . .
                del self.clients[index]
                print('Removed ' + index + ' due to QUIT command. . .')

            except Exception as e:
                # user must be hosting server in separate window - try deleting peer at index of their local IP
                local_ip_index = info['local_ip'] + ':' + str(info['port'])
                del self.clients[local_ip_index]
                print('Removed ' + local_ip_index + ' due to QUIT command. . .')

            finally:
                pass

        if req_type == "MSG_CHECK":
            # check if the peer has any messages waiting
            # assume that the peer is not on the same LAN as the server
            local_ip = info['local_ip']
            ip = h
            port = info['port']

            if ip == local_ip:
                # operating in internet mode on LAN for some reason - refer to peer using its local IP
                index = local_ip + ':' + str(port)

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
                return  # take no further action

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
                if key != index:  # don't send to yourself
                    print(key, index)
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


if __name__ == '__main__':
    # start server
    s = Server()
    s.setDaemon(True)  # allows use of CTRL+C to exit program
    s.start()

    # sleep main thread indefinitely so program doesn't exit
    while True:
        time.sleep(10)
