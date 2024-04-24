#!/usr/bin/env python3

import socket
import json
import wg
import udp_filter
from udp_packer import build_udp_packet, messenger
from ruler import rules
import logger
from time import sleep
from threading import Thread
import sys

def update_peer(payload):

    wg_conf = wg.wg()
    wg_conf.set_endpoint(payload['peer'], 
                         (payload['ip'], payload['port']),
                         payload['allowed_ips'],
                         )

def register(raw_socket, local_port, server_addr, public, endpoint):

    registered = False
    count = 0

    while True:
        if count >= 30: break
        messenger(
                raw_socket, 
                local_port, 
                server_addr, 
                message = rules.build_register(public, endpoint).encode(),
                )
        logger.l.log_message("Sending Register info...", "debug")
        r, _ = udp_filter.filter(       # if it works, then reply is a json bytes object
                raw_socket,
                local_port
                )
        reply = json.loads(r[2])
        if reply['command'] == 'success':
            logger.l.log_message("Register Successful!", "info")
            registered = True
            break
        sleep(5)
        count+=5
        logger.l.log_message("Sending Register Request Again...", "debug")

    return registered


def request_full_cone(raw_socket, local_port, server_addr, peer):

    messenger(
            raw_socket,
            local_port,
            server_addr,
            message = rules.build_request(peer).encode()
            )
    logger.l.log_message("Hole Punching... HOST <----> {}".format(peer), "debug")
    r, _ = udp_filter.filter(
            raw_socket,
            local_port
            )
    reply = json.loads(r[2])
    if reply['command'] == 'reply':
        logger.l.log_message("Reply Received!", "debug")
        update_peer(reply['payload'])


def client(endpoint, server_addr, wg_port=51820, peers=[], interface='wg-p2p0'):

    wg_conf = wg.wg()
    interface = 'wg-p2p0'

    # basic attributions
    listening_port = None
    public = b''

    # WireGuard interface setup and configuration
    if not wg_conf.check_interface(interface):
        wg_conf.create_interface(endpoint)
    wg_conf.configure_wireguard(peers=peers, port=wg_port, interface=interface)
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
    registered = register(client, listening_port, server_addr, public, endpoint)
    if not registered:
        logger.l.log_message("注册超时，退出...", "error")
        print("注册超时，退出", file=sys.stderr)
        exit(-1)
    

    while True:
        # Requesing (ip, port) info in the peers' list
        for _ in peers:
            request_full_cone(client, listening_port, server_addr, _)
        sleep(5)

if __name__ == '__main__':

    # for testing
    pass
