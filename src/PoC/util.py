import struct
import sys
from collections import namedtuple
from logger import *

def addr_from_args(args, host='127.0.0.1', port=9999):
    if len(args) >= 3:
        host, port = args[1], int(args[2])
    elif len(args) == 2:
        host, port = host, int(args[1])
    else:
        host, port = host, port
    return host, port

# 将node的地址信息从data中提取
def msg_to_addr(data):
    ip, port = data.decode('utf-8').strip().split(':')
    return (ip, int(port))

# 将node的地址信息打包发送给对等节点
def addr_to_msg(addr):
    return '{}:{}'.format(addr[0], str(addr[1])).encode('utf-8')

def send_msg(sock, msg):
    # Prefix each message with a 4-byte length (network byte order)
    msg = struct.pack('>I', len(msg)) + msg
    sock.sendall(msg)

def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def recv_msg(sock):
    # Read message length and unpack it into an integer
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    return recvall(sock, msglen)

def type_send(sock, addr):
    l = setup_logger("type_send_log")
    while True:
        message = sys.stdin.readline().strip()  # 从标准输入读取一行
        sock.sendto(message.encode(), addr)
        log_message(l, "message {} send".format(message), "debug")

def type_recv(sock):
    l = setup_logger("type_recv_message")
    while True:
        data, addr = sock.recvfrom(1024)
        log_message(l, "Received: {} from {}:{}".format(data.decode(), *addr), "debug")

class Client(namedtuple('Client', 'conn, pub, priv')):

    def peer_msg(self):
        return addr_to_msg(self.pub) + b'|' + addr_to_msg(self.priv)

