import socket
import threading
import datetime
import time

host = '127.0.0.1'


class Peer:

    def __init__(self, config):

        self.port = config["LOCAL_PORT_NO"]

        self.server_ip = config["SERVER_IP"]
        self.server_host = config["SERVER_PORT"]

        # Create a TCP socket to listen for connections
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Re-use the socket
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # bind the socket to a public host, and a port
        self.serverSocket.bind((host, self.port))

        self.serverSocket.listen(10)

        # TODO - ping central server periodically
        keep_alive = threading.Thread(name='keep_alive', target = self.ping_server_periodically, args=())
        keep_alive.setDaemon(True)
        keep_alive.start()

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
        pass

    # send an image to all peers
    def broadcast_image(self, img):

        # get list of all active peers from server

        # iterate over peers and send the image in separate threads

        pass

    def broadcast_string(self, string):

        # get list of all active peers from server

        # spawn threads to send strings to all peers

        pass

    # ping the server every 30 seconds to maintain alive status
    def ping_server_periodically(self):
        start = time.time()

        while True:
            start = time.time()
            # open socket to server and ensure timeout << 30 seconds

            # send a ping message to tell server we are alive

            # close connection

            # wait about 30 seconds and do it again forever
            end = time.time()
            time.sleep(30-(end-start))

