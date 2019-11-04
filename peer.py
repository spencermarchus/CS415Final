import socket
import threading
import datetime
import time

host = '127.0.0.1'


class Peer:

    def __init__(self, config):

        self.port = config["PORT_NO"]

        # Create a TCP socket
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Re-use the socket
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # bind the socket to a public host, and a port
        self.serverSocket.bind((host, self.port))

        # connect to central server

        while True:
            # Establish the connection
            (clientSocket, client_address) = self.serverSocket.accept()

            d = threading.Thread(name='client',
                                 target=self.peer_thread, args=(clientSocket, client_address))
            d.setDaemon(True)
            d.start()


    def peer_thread(self, client_sock, client_addr):
        # do stuff
        # generally, here we will handle receiving something like an image
        pass

    # send an image to all peers
    def broadcast_image(self, img):

        # get list of all active peers from server

        # iterate over peers and send the image

        pass
