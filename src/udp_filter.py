#!/usr/bin/env python3

import socket
import struct
import logger
import json

def ip_header_parser(header_bytes):
    header_format = '!BBHHHBBH4s4s'
    header_extracted = struct.unpack(header_format, header_bytes[:20])

    version             = header_extracted[0] >> 4
    IHL                 = header_extracted[0] & 0x0f        # IP Header Length, 用于表示首部有多少*32位(4字)*
    DSCP                = header_extracted[1] & 0xfc        # RFC 2474, formally known as TOS
    ECN                 = header_extracted[2] & 0x03
    total_length        = header_extracted[2]
    identification      = header_extracted[3]
    flags               = header_extracted[4] >> 13
    fragment_offset     = header_extracted[4] & 0xe000
    ttl                 = header_extracted[5]
    protocol            = header_extracted[6]
    checksum            = header_extracted[7]
    source_address      = socket.inet_ntoa(header_extracted[8])
    destination_address = socket.inet_ntoa(header_extracted[9])

    output = ["IP Version: {}".format(version),
              "IP Header Length: {}".format(IHL),
              "Differentiated Services: {}".format(DSCP),
              "Explicit Congestion Notification: {}".format(ECN),
              "Total Length: {}".format(total_length),
              "Identification: {}".format(identification),
              "Flags: {}".format(flags),
              "Fragment Offset: {}".format(fragment_offset),
              "Time to Live: {}".format(ttl),
              "Protocol: {}".format(protocol),
              "Header Checksum: {}".format(checksum),
              "Source Address: {}".format(source_address),
              "Destination Address: {}".format(destination_address)
              ]

    for _ in output:
        logger.l.log_message(_, "debug")

    return version, IHL, DSCP, ECN, total_length, identification, flags, fragment_offset, ttl, protocol,\
            checksum, source_address, destination_address

def udp_parser(header_bytes):

    header_format = '!HHHH'
    _ip = ip_header_parser(header_bytes)
    udp_header = header_bytes[_ip[1]*4:_ip[1]*4+8]
    header_extracted = struct.unpack(header_format, udp_header)
    
    source_port      = header_extracted[0]
    destination_port = header_extracted[1]
    length           = header_extracted[2]
    checksum         = header_extracted[3]

    payload_format = '!{}s'.format(length-8)
    udp_payload = header_bytes[_ip[1]*4+8:_ip[1]*4+8+length]
    payload_extracted = struct.unpack(payload_format, udp_payload)
    payload = payload_extracted[0]

    output = ["Source Port: {}".format(source_port),
              "Destination Port: {}".format(destination_port),
              "UDP Packet Length: {}".format(length),
              "UDP Checksum: {}".format(checksum),
              "UDP Payload: {}".format(payload)
              ]

    for _ in output:
        logger.l.log_message(_, "debug")

    return source_port, destination_port, payload

def filter(raw_sock, port):

    while True:
        data, addr = raw_sock.recvfrom(1024)
        if is_control_packet(data, port):
            return udp_parser(data), addr
            
            
def is_control_packet(data, port):
    result = False
    source_port, destination_port, payload = udp_parser(data)
    try:
        payload_json = json.loads(payload)
        if 'command' in payload_json.keys() and 'payload' in payload_json.keys() and port == destination_port:
            logger.l.log_message("message is accepted", "debug")
            result = True
    except json.decoder.JSONDecodeError as e:
        logger.l.log_message(e, "error")
        result = False
    except Exception as e:
        logger.l.log_message(e, "error")
        result = False

    return result

if __name__ == "__main__":
    filter()
