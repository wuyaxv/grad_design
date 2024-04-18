#!/usr/bin/env python3

import socketserver
import subprocess
import json
import logger

class Handler(socketserver.BaseRequestHandler):

    def __init__(self):

    def setup(self):
        pass
    
    def handle(self):
        payload, s = self.request
        payload
        pass

    def finish(self):
        pass

class MappingRegisterServer(socketserver.ThreadingUDPServer):
    
    def __init__(self, server_ddr, RequestHandlerClass, l=None, mapping_list=[], bind_and_activate=True):
        super().__init__(server_addr, RequestHandlerClass, bind_and_activate)
        self.mapping_list = mapping_list

        # setup logger
        if not l:
            self.logger = logger.logger()
        else:
            self.logger = l

        

def server(l=None, mapping_list=[]):
    host, port = '0.0.0.0', 12345

    # setup logger
    if not l:
        l = logger.logger()
    
    with MappingRegisterServer((host, port), Handler, l, mapping_list) as s:
        s.allow_reuse_address = True
        s.serve_forever()
