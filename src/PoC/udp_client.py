import socket
import sys
from util import *
from logger import *
import threading

logger = logging.getLogger()

def udp_client(host='120.79.143.252', port=6166):

    l = setup_logger("udp_client_logger")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    sock.sendto(b'bonjour', (host, port))

    # 从server受到对等节点的信息
    data, addr = sock.recvfrom(1024)
    log_message(l, 'client received: {} from {}:{}'.format(data.decode(), *addr), 'info')
    addr = msg_to_addr(data)
    sock.sendto(b'from node-2', addr)
    # 连接建立

    data, addr = sock.recvfrom(1024)
    log_message(l, 'client received: {} {}'.format(addr, data), 'info')

    # 启动发送数据的线程
    send_thread = threading.Thread(target=type_send, args=(sock, addr))
    send_thread.start()

    # 启动接收数据的线程
    receive_thread = threading.Thread(target=type_recv, args=(sock, ))
    receive_thread.start()


    # 等待线程结束
    receive_thread.join()
    send_thread.join()


if __name__ == '__main__':
    udp_client()
