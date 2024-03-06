#!/usr/bin/env python3

from logger import *
import threading
import socket
import json

l = setup_logger("rendezvous_server_log")

"""rendezvous_server
接受来自对等节点的信息,解析对等节点发送的内容.
1) 对等节点的external ip:port 对
2) 对等节点的internal ip:port 对
3) 对等节点的NAT类型

"""
def rendezvous_server(host="0.0.0.0", port="6167"):

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))     # listening on port 6167

# Handle hook
def handle(command=None, args=[]):
    pass

# Store Wireguard Credentials
def store_wireguard_credentials():
    pass

def parser(data)

# Send Wireguard Credentails

