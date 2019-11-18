import socket
import threading
import datetime
import time
import _pickle as pickle

host = '127.0.0.1'


class Peer:

    def __init__(self, config):

        global client_dict
        self.port = config["LOCAL_PORT_NO"]

        self.server_ip = config["SERVER_IP"]
        self.server_host = config["LOCAL_SERVER_PORT"]

        # Create a TCP socket to listen for connections
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Re-use the socket
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # bind the socket to a public host, and a port
        self.serverSocket.bind((host, self.port))

        self.serverSocket.listen(10)


        keep_alive = threading.Thread(name='keep_alive', target = self.ping_server_periodically, args=())
        keep_alive.setDaemon(True)
        keep_alive.start()


        time.sleep(2)

        self.broadcast_string('REE')
        self.broadcast_image("placeholder")

        while True:
            # handle incoming connections

            # Establish the connection
            (clientSocket, client_address) = self.serverSocket.accept()

            d = threading.Thread(name='client',
                                 target=self.peer_thread, args=(clientSocket, client_address))
            d.setDaemon(True) # can run in background
            d.start()


    def peer_thread(self, client_sock, client_addr):
        # do stuff
        # generally, here we will handle receiving something like an image
        print('Handling message. . .')

        data = client_sock.recv(4096)

        data_loaded = pickle.loads(data)

        print('Message from client: ')
        print(data_loaded)

        if data_loaded['type'] == 'IMAGE':
            img = data_loaded['data']
            with open('tst' + str(self.port) + '.png', 'wb') as image:
                image.write(img)


    # send an image to all peers
    def broadcast_image(self, img):
        img = "/Users/mckennaobrien/Documents/My Pictures/Test.png"
        try:
            img = open(img, "rb").read()
        except IOError:
            pass

        # get list of all active peers from server
        self.get_active_peers()

        # iterate over peers and send the image in separate threads
        for p in client_dict:
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

        msg = {'type': 'IMAGE', 'port': self.port, 'data': img, 'sender': sender}

        # pickle the dict and send it
        img_s.send(pickle.dumps(msg))
        img_s.close()

    def get_active_peers(self):
        # get list of all active peers from server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.server_ip, self.server_host))
        print('Connected to server, requesting list of peers')

        request_dict = {'type': 'REQUEST_PEER_DICT'}

        data = pickle.dumps(request_dict)

        s.send(data)

        ret_val = s.recv(4096)

        return_data = pickle.loads(ret_val)

        print("RECEIVED CLIENT DICT FROM SERVER. . .")
        print(return_data)
        global client_dict
        client_dict = return_data

    def broadcast_string(self, string):



        # spawn threads to send strings to all peers

        pass

    # ping the server every 30 seconds to maintain alive status
    def ping_server_periodically(self):

        while True:
            start = time.time()
            # open socket to server and ensure timeout << 30 seconds
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            s.connect((self.server_ip, self.server_host))

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


cfg = {"LOCAL_PORT_NO": 5555, "SERVER_IP": '127.0.0.1', "LOCAL_SERVER_PORT": 9999}

peer = Peer(cfg)

