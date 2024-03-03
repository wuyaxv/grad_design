#!/usr/bin/env python
#
# Proof of Concept: UDP Hole Punching
# Two client connect to a server and get redirected to each other.
#
# This is the client.
#

import sys
import socket
from select import select
import struct
from time import sleep

def bytes2addr(bytes):
    """Convert a hash to an address pair."""
    if len(bytes) != 6:
        raise ValueError("invalid bytes")
    host = socket.inet_ntoa(bytes[:4])
    port, = struct.unpack("H", bytes[-2:])
    print('Decoded Host and port: {}:{}'.format(host, port))
    return host, port

def main():
    try:
        master = (sys.argv[1], int(sys.argv[2]))
        pool = sys.argv[3].strip()
    except (IndexError, ValueError):
        print("usage: %s <host> <port> <pool>" % sys.argv[0], file=sys.stderr)
        sys.exit(65)

    sockfd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sockfd.sendto(pool.encode(), master)
    data, addr = sockfd.recvfrom(len(pool)+3)
    if data != b"ok "+pool.encode():
        print("unable to request!", file=sys.stderr)
        sys.exit(1)
    sockfd.sendto(b"ok", master)
    print("request sent, waiting for partner in pool '%s'..." % pool, file=sys.stderr)
    data, addr = sockfd.recvfrom(6)

    target = bytes2addr(data)
    print("connected to %s:%d" % target, file=sys.stderr)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        sock.sendto(b'Hello world', target)
        print('message sent to {}: Hello world'.format(target))
        sleep(5)

    while True:
        rfds,_,_ = select([0, sockfd], [], [])
        if 0 in rfds:
            data = sys.stdin.readline()
            if not data:
                break
            sockfd.sendto(data.encode(), target)
        elif sockfd in rfds:
            data, addr = sockfd.recvfrom(1024)
            sys.stdout.write(data.decode())

    sockfd.close()

if __name__ == "__main__":
    main()

