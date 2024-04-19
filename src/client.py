#!/usr/bin/env python3

import socket
import json
import wg
import udp_filter
from udp_packer import build_udp_packet, messenger
from ruler import rules
import logger
from time import sleep

def update_peer(payload):
    wg_conf = wg.wg()
    wg_conf.update_peer(payload['peer'])

def register(raw_sock, local_port, server_addr, public):
    registered = False

    while True:
        messenger(
                raw_socket, 
                local_port, 
                server_addr, 
                message = rules.build_register(public).encode(),
                )
        logger.l.log_message("Sending Register info...", "debug")
        r, _ = udp_filter.filter(       # if it works, then reply is a json bytes object
                raw_socket,
                local_port
                )
        reply = json.loads(r[2])
        if reply['command'] == 'success':
            logger.l.log_message("Register Successful!", "info")
            break
        sleep(5)
        logger.l.log_message("Sending Register Request Again...", "debug")

def request_full_cone(raw_socket, local_port, server_addr, peer):
    messenger(
            raw_socket,
            local_port,
            server_port,
            message = rules.build_request(peer)
            )
    logger.l.log_message("Hole Punching... HOST <----> {}".format(peer), "debug")
    r, _ = udp_filter.filter(
            raw_socket,
            local_poret
            )
    reply = json.loads(r[2])
    if reply['command'] == 'reply':
        logger.l.log_message("Reply Received!", "debug")
        update_peer(reply['payload'])

def client(wg_ip, server_addr, peers=[]):

    wg_conf = wg.wg()
    interface = 'wg-p2p0'

    # basic attributions
    listening_port = None
    public = b''

    # WireGuard interface setup and configuration
    if not wg_conf.check_interface(interface):
        wg_conf.create_interface(wg_ip)
    wg_conf.configure_wireguard(peers=peers)
    if not (listening_port:=wg_conf.get_wg_port()):
        logger.l.log_message("获取WireGuard监听端口失败", "error")
        exit(-1)
    if not (public:=wg_conf.get_wg_public()):
        logger.l.log_message("获取WireGuard Public-Key失败", "error")
        exit(-1)

    # setup listening server
    client = None
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
    except Exception as e:
        logger.l.log_message("An error occurred during the process of creating the raw socket", 'error')
        exit(-1)
    
    # Register this peer with pubkey and (ip, port) tuple
    register(client, listening_port, server_addr, public)

    while True:
        # Requesing (ip, port) info in the peers' list
        for _ in peers:
            try_to_establish_connections(client, listening_port, server_addr, _)

if __name__ == '__main__':
    # for testing
    client('10.0.0.1', ('192.168.6.103', 12345))
