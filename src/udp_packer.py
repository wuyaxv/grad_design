#!/usr/bin/env python3 

import socket
import struct

def build_udp_packet(src_port, dst_port, payload):

    udp_packet_format = '!HHHH{}s'.format(len(payload))
    udp_packet = struct.pack(udp_packet_format, src_port, dst_port, 8+len(payload), 0, payload)
    return udp_packet

def messenger(raw_socket, src_port:int, dst_addr:tuple, message:bytes):

    to_send = build_udp_packet(src_port, dst_addr[1], message)
    
    raw_socket.sendto(to_send, dst_addr)
    raw_socket.close()

if __name__ == '__main__':
    raw_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
    messenger(raw_sock, 12345, ('192.168.6.103', 8888), b"helloworld\n")
