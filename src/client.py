#!/usr/bin/env python3

import socket
import wg
import udp_filter
from udp_packer import build_udp_packet, messenger
from ruler import rules
import logger
from time import sleep

def client(wg_ip, server_addr, peers=[]):

    # infrastructure
    client_logger = logger.logger('client')
    wg_conf = wg.wg(client_logger)
    interface = 'wg-p2p0'

    # basic attributions
    listening_port = None
    public = b''

    # WireGuard interface setup and configuration
    if not wg_conf.check_interface(interface):
        wg_conf.create_interface(wg_ip)
    wg_conf.configure_wireguard(peers=peers)
    if not (listening_port:=wg_conf.get_wg_port()):
        client_logger.log_message("获取WireGuard监听端口失败", "error")
        exit(-1)
    if not (public:=wg_conf.get_wg_public()):
        client_logger.log_message("获取WireGuard Public-Key失败", "error")
        exit(-1)

    # setup listening server
    server = None
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
    except Exception as e:
        client_logger.log_message("An error occurred during the process of creating the raw socket", 'error')
        exit(-1)
    
    # register the public key peer.
    while True:
        messenger(
                server, 
                listening_port, 
                server_addr, 
                message = rules.build_register(public).encode(),
                )
        r, _ = udp_filter.filter(       # if it works, then reply is a json bytes object
                server,
                udp_filter.is_control_packet,
                )
        reply = json.loads(r[2])
        if reply['command'] == 'success':
            client_logger.log_message("Register Successful!", "info")
            break
        sleep(5)
        client_logger.log_message("Sending Register Request Again...", "info")

        
client('10.0.0.1', ('127.0.0.1', 12345), ["BkZ4UIcBY9C4uqbxZu+S+2cPvWuIn/oZbBsRKUcV4QU=", ])

