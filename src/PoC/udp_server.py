# UDP Hole Punching PoC

import socket
import sys
import time
from util import *
from logger import *

def udp_server(host='0.0.0.0', port=6166):
    l = setup_logger("udp_server_logger")
    addresses = []

    # 监听端口6166
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))

    while True:
        data, addr = sock.recvfrom(1024)
        log_message(l, "connection from: {}:{}".format(*addr), 'info')
        addresses.append(addr)
        if len(addresses) >= 2:
            log_message(l, "server - send client info to: {}:{}".format(*addresses[0]), 'info')

            sock.sendto(addr_to_msg(addresses[1]), addresses[0])
            log_message(l, "server - send client info to: {}:{}".format(*addresses[1]), 'info')
            sock.sendto(addr_to_msg(addresses[0]), addresses[1])
            addresses.pop(1)
            addresses.pop(0)

if __name__ == '__main__':
    udp_server()
