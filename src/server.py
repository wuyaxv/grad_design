#!/usr/bin/env python3

import socketserver
import subprocess
import json
import logger
from ruler import rules

"""
registry = {
        'PEER_PUBKEY':(ip, port), 
        ...
        }
"""

class Handler(socketserver.BaseRequestHandler):

    def setup(self):
        pass
    
    def handle(self):
        data, s = self.request[0], self.request[1]
        logger.l.log_message('Received data: {}'.format(data), 'info')
        addr = self.client_address
        response = rules.packet_parser(self.server.registry, data.rstrip(), addr).encode()
        s.sendto(response, addr)

    def finish(self):
        pass

class MappingRegisterServer(socketserver.ThreadingUDPServer):
    
    def __init__(self, server_addr, RequestHandlerClass, registry=dict(), bind_and_activate=True):
        super().__init__(server_addr, RequestHandlerClass, bind_and_activate)
        self.registry = registry
        self.logger = None

def server(registry=dict(), listening_port=12345):
    host, port = '0.0.0.0', listening_port
    
    with MappingRegisterServer((host, port), Handler, registry) as s:
        s.allow_reuse_address = True
        s.serve_forever()

if __name__ == '__main__':
    server()
