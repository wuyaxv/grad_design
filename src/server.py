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
        self.server.logger.log_message('Received data: {}'.format(data), 'debug')
        addr = self.client_address
        response = rules.packet_parser(self.server.registry, data.rstrip(), addr).encode()
        s.sendto(response, addr)

    def finish(self):
        pass

class MappingRegisterServer(socketserver.ThreadingUDPServer):
    
    def __init__(self, server_addr, RequestHandlerClass, l=None, registry={}, bind_and_activate=True):
        super().__init__(server_addr, RequestHandlerClass, bind_and_activate)
        self.registry = registry

        # setup logger
        if not l:
            self.logger = logger.logger()
        else:
            self.logger = l

def server(l=None, mapping_list=[], listening_port=12345):
    host, port = '0.0.0.0', listening_port

    # setup logger
    if not l:
        l = logger.logger()
    
    with MappingRegisterServer((host, port), Handler, l, mapping_list) as s:
        s.allow_reuse_address = True
        s.serve_forever()
server()
