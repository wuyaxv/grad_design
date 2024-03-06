#!/usr/bin/env python3
import sys
import socket
import struct
import fcntl
import os
from util import *
from logger import *


clients = {}

def tcp_server(host='0.0.0.0', port=5005):
    l = setup_logger("tcp_server_log")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(1)
    s.settimeout(30)

    while True:
        try:
            conn, addr = s.accept()
        except socket.timeout:
            continue

        logger.info('connection address: %s', addr)
        log_message(l, 'connection address: {}:{}'.format(*addr))
        data = recv_msg(conn)
        priv_addr = msg_to_addr(data)
        send_msg(conn, addr_to_msg(addr))
        data = recv_msg(conn)
        data_addr = msg_to_addr(data)
        if data_addr == addr:
            log_message(l, 'client reply matches', 'info')
            clients[addr] = Client(conn, addr, priv_addr)
        else:
            log_message(l, 'client reply did not match', 'info')
            conn.close()

        log_message(l, 'server - received data: {}'.format(data.decode()))

        if len(clients) == 2:
            (addr1, c1), (addr2, c2) = clients.items()
            log_message(l, 'server - send client info to: {}'.format(c1.pub))
            send_msg(c1.conn, c2.peer_msg())
            log_message(l, 'server - send client info to: {}'.format(c2.pub))
            send_msg(c2.conn, c1.peer_msg())
            clients.pop(addr1)
            clients.pop(addr2)

    conn.close()


if __name__ == '__main__':
    main()
