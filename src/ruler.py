#!/usr/bin/env python3

"""This file defines methods that parse rules that's been communicated between client and server
Basic Structure:
    - Command: defines the command to determine the behaviour
    - Payload: varys according to the command
    {
    'command': COMMAND, 
    'payload': PAYLOAD,
    }
COMMAND & PAYLOAD:
    - b'register': Register (ip, port) mapping record
        - payload: {'peer': HOST_PUBLIC_KEY}
    - b'request' : Request peer's NAT (ip, port)
        - payload: {'peer': PEER_PUBLIC_KEY}
    - b'reply'   : Reply to the host about all of the list
        - payload: {'peer': PEER_PUBLIC_KEY, 'ip': PEER_NAT_IP, 'port': PEER_NAT_PORT}
    - b'error'   : Tell the client that something is wrong.
        - payload: {'info': ERROR_INFO}
    - b'success'  : Register success
        - payload: {'info': SUCCESS_INFO}
"""

import json
import logger

class PacketException(Exception):
    pass
class RegisterException(Exception):
    pass
class RequestException(Exception):
    pass

# Rules, I think they should be encapsulated in one class and used as static methods.
class rules:

    # would it be a good idea to seperate packet building process from generating a reply?
    @staticmethod
    def build_reply(peer, addr):
        reply = json.dumps({
            'command': 'reply',
            'payload': {
                'peer': peer,
                'ip':   addr[0],
                'port': addr[1],
                },
            })
        return reply

    @staticmethod
    def build_request(peer):
        reqeust = json.dumps({
            'command': 'request',
            'payload': {
                'peer': peer,
                },
            })
        return request

    @staticmethod
    def build_register(peer):
        register_request = json.dumps({
            'command': 'register',
            'payload': {
                'peer': peer,
                },
            })
        return register_request

    @staticmethod
    def build_error_reply(info):
        error_reply = json.dumps({
            'command': 'error',
            'payload': {
                'info': info,
                },
            })
        return error_reply

    @staticmethod
    def build_success_reply(info):
        success_reply = json.dumps({
            'command': 'success',
            'payload': {
                'info': info,
                },
            })
        return success_reply
        
    @staticmethod
    def update_peer(registry, peer, addr):
        if peer in registry.keys():
            # ip and port aren't matching thus need to be updated
            if registry[peer][0] != addr[0] \
                    or registry[peer][1] != addr[1]:
               registry[peer][0] = addr[0]
               registry[peer][1] = addr[1]
        else:
            registry[peer] = {
                    addr,
                    }

    @staticmethod
    def spit_error(info):
        return rules.build_error_reply(info)

    @staticmethod
    def spit_success(info):
        return build_success_reply(info)

    # lookup registry and generate reply accordingly
    @staticmethod
    def request_handler(registry, payload, addr):
        response = None
        try:
            if 'peer' not in payload.keys():
                raise RequestException
            else:
                if rules.check_registry(registry, payload['peer']):
                    response = rules.build_reply(registry[payload['peer']], addr)
                else:
                    response = rules.spit_error('Peer not registerd!')
        except RequestException:
           response = rules.spit_error('An error occurred during parsing the request!')
        return response

    @staticmethod
    def register_handler(registry, payload, addr):
        response = None
        try:
            if 'peer' not in payload.keys():
                raise RegisterException
            else:
                rules.update_peer(registry, payload['peer'], addr)
                # should i send back a response stating registration is successful?
                # TODO: build a basic mechanism much like HTTP...
                response = rules.spit_success("Peer registered!")
        except RegisterException:
            response = rules.spit_error("An error occurred during registering the peer!")
        return response

    @staticmethod
    def check_registry(registry, peer):
        if peer in registry.keys(): return True
        else: return False
    
    # Parse incoming paacket and generate a response accordingly
    @staticmethod
    def packet_parser(registry, packet, addr):
        response = None
        packet = json.loads(packet)
        try:
            if 'command' not in packet.keys() or 'payload' in packet.keys():
                raise PacketException
            else:
                payload = packet['payload']
                match packet['command']:
                    case 'register': 
                        response = rules.register_handler(registry, payload, addr)
                    case 'request' : 
                        response = rules.request_handler(registry, payload, addr)
                    case '_': 
                        response = rules.spit_error("Command not recognized!")
        except PacketException:
            response = rules.spit_error("An error occured while parsing your command!")
            print("An error occurred while parsing the packet!")
        except Exception as e:
            response = rules.spit_error("An error occured while parsing your command!")
            print(e)

        return response
