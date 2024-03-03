#!/usr/bin/env python3

"""
Status: PoC
"""
import socket
import threading
import codecs
from stun import get_ip_info

class Peer:
    """Peer
    """

    def __init__(self, host, port):

        self.host = host
        self.port = port
        self.address = (self.host, self.port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connections = []

    def connect(self, peer_host, peer_port):

        try:
            connection = socket.create_connection((peer_host, peer_port))
            self.connections.append(connection)
            print("Connected to {host}:{port}".format(host=peer_host, port=peer_port))
        except socket.error as e:
            print("Failed to connect to {host}:{port}. Error: {error}".format(host=peer_host, port=peer_port, error=e))

    def stun_connect(self, peer_host, peer_port, stun_host, stun_port=3478):

        try: 
            nat_type, external_ip, external_port = get_ip_info(stun_host=stun_host, stun_port=stun_port)

    def listen(self):

        self.socket.bind((self.host, self.port))
        self.socket.listen(10)

        print("Listening for connections on {}:{}".format(self.host, self.address)

        while True:
            connection, address = self.socket.accept()
            self.connections.append(connection)
            print("Accepted connection from {}".format(address))
            threading.Thread(target=self.handle_client, args=(connection, address)).start()
                

    def send_data(self, message):

        for c in self.connections:
            try:
                data = codecs.encode(message)
                c.sendall(data)
            except socket.error as e:
                print("Failed to send data. Error: {error}".format(e))
            c.close()

    def handle_client(self, connection, address):

        while True:
            try:
                data = connection.recv(1024)
                if not data:
                    break
                print("Received data {} from {}".format(codecs.decode(data), address))
            except socket.error as e:
                break
        print("Connection from {address} closed.".format(address=address))
        self.connections.remove(connection)
        connection.close()

    def start(self):
        listen_thread = threading.Thread(target=self.listen)
        listen_thread.start()
