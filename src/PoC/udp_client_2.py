import socket
import sys
from util import *
from logger import *
import threading
import subprocess

logger = logging.getLogger()

# Peer1 Config (PoC)
peer1 = {
        "port": 51820,
        "public_key": "oNgFtsTGSX0gBXX7FbS/K8nOIwAGI0i8AXBWagpOoT0=",
        "private_key": "mP+9grSaAAjVveyttutcX8cJHXGiD2z30n11vlbxo0s=",
        "public_key_path": "p1_public_key",
        "private_key_path": "p1_private_key",
        }

peer2 = {
        "port": 51820,
        "public_key": "irlPD7wX4ebUuH+Ay6hwQnjOlkN/I+Uy1K1h7l7gcBY=",
        "private_key": "IOD+9XCsq5L7z84mAhQLyDIpiXcEc3Sf8vdHfWHh91I=",
        "public_key_path": "p2_public_key",
        "private_key_path": "p2_private_key",
        }

def setup_peer1(t_host, t_port, s_port):        # target host and target port
    l = setup_logger("setup_peer1_logger")
    log_message(l, "Setting up wg0...", "debug")

    peer2['port'] = s_port

    # 清除wg0设置
    result=None
    try:
        result = subprocess.run('ip link del dev wg0 type wireguard'.split(), capture_output=True, check=True, text=True)
        # [*] 作为前缀表示标准输出和标准错误输出
        log_message(l, "[*] {}".format(result.stdout), "debug")
        log_message(l, "[*] {}".format(result.stderr), "error")
    except subprocess.CalledProcessError as e:
        log_message(l, e, "error")

    # 重新设置wg0
    try:
        result = subprocess.run('ip link add dev wg0 type wireguard'.split(), capture_output=True, check=True, text=True)
        log_message(l, "[*] {}".format(result.stdout), "debug")
        log_message(l, "[*] {}".format(result.stderr), "error")
        result = subprocess.run('ip address add dev wg0 100.64.0.1/24'.split(), capture_output=True, check=True, text=True)
        log_message(l, "[*] {}".format(result.stdout), "debug")
        log_message(l, "[*] {}".format(result.stderr), "error")
        result = subprocess.run('ip link set dev wg0 up'.split(), capture_output=True, check=True, text=True)
        log_message(l, "[*] {}".format(result.stdout), "debug")
        log_message(l, "[*] {}".format(result.stderr), "error")
        result = subprocess.run('ip route add 100.64.0.0/16 dev wg0'.split(), capture_output=True, check=True, text=True)
        log_message(l, "[*] {}".format(result.stdout), "debug")
        log_message(l, "[*] {}".format(result.stderr), "error")
    except subprocess.CalledProcessError as e:
        log_message(l, e, "error")

    # 设置对端的节点信息
    try:
        result = subprocess.run('wg set wg0 listen-port {} private-key {}'.format(peer1["port"], peer1["private_key_path"]).split(), capture_output=True, check=True, text=True)
        log_message(l, "[*] {}".format(result.stdout), "debug")
        log_message(l, "[*] {}".format(result.stderr), "error")
        result = subprocess.run('wg set wg0 peer {} endpoint {}:{} allowed-ips 0.0.0.0/0'.format(peer2["public_key"], t_host, t_port).split(), capture_output=True, check=True, text=True)
        log_message(l, "[*] {}".format(result.stdout), "debug")
        log_message(l, "[*] {}".format(result.stderr), "error")
    except subprocess.CalledProcessError as e:
        log_message(l, e, "error")


def setup_peer2(t_host, t_port, s_port):        # target host and target port
    l = setup_logger("setup_peer2_logger")
    log_message(l, "Setting up wg0...", "debug")

    peer2['port'] = s_port

    # 清除wg0设置
    try:
        result = subprocess.run('ip link del dev wg0 type wireguard'.split(), capture_output=True, check=True, text=True)
        # [*] 作为前缀表示标准输出和标准错误输出
        log_message(l, "[*] {}".format(result.stdout), "debug")
        log_message(l, "[*] {}".format(result.stderr), "error")
    except subprocess.CalledProcessError as e:
        log_message(l, e, "error")

    # 重新设置wg0
    try:
        result = subprocess.run('ip link add dev wg0 type wireguard'.split(), capture_output=True, check=True, text=True)
        log_message(l, "[*] {}".format(result.stdout), "debug")
        log_message(l, "[*] {}".format(result.stderr), "error")
        result = subprocess.run('ip address add dev wg0 100.64.0.2/24'.split(), capture_output=True, check=True, text=True)
        log_message(l, "[*] {}".format(result.stdout), "debug")
        log_message(l, "[*] {}".format(result.stderr), "error")
        result = subprocess.run('ip link set dev wg0 up'.split(), capture_output=True, check=True, text=True)
        log_message(l, "[*] {}".format(result.stdout), "debug")
        log_message(l, "[*] {}".format(result.stderr), "error")
        result = subprocess.run('ip route add 100.64.0.0/16 dev wg0'.split(), capture_output=True, check=True, text=True)
        log_message(l, "[*] {}".format(result.stdout), "debug")
        log_message(l, "[*] {}".format(result.stderr), "error")
    except subprocess.CalledProcessError as e:
        log_message(l, e, "error")

    # 设置对端的节点信息
    try:
        result = subprocess.run('wg set wg0 listen-port {} private-key {}'.format(peer2["port"], peer2["private_key_path"]).split(), capture_output=True, check=True, text=True)
        log_message(l, "[*] {}".format(result.stdout), "debug")
        log_message(l, "[*] {}".format(result.stderr), "error")
        result = subprocess.run('wg set wg0 peer {} endpoint {}:{} allowed-ips 0.0.0.0/0'.format(peer1["public_key"], t_host, t_port).split(), capture_output=True, check=True, text=True)
        log_message(l, "[*] {}".format(result.stdout), "debug")
        log_message(l, "[*] {}".format(result.stderr), "error")
    except subprocess.CalledProcessError as e:
        log_message(l, e, "error")


def udp_client(host='49.232.213.235', port=6166):

    l = setup_logger("udp_client_logger")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    #sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    #sock.bind(('0.0.0.0', 51820))
    sock.sendto(b'bonjour', (host, port))

    # 从server受到对等节点的信息
    data, addr = sock.recvfrom(1024)
    log_message(l, 'client received: {} from {}:{}'.format(data.decode(), *addr), 'info')
    addr = msg_to_addr(data)
    """
    sock.sendto(b'bonsoir', addr)
    log_message(l, 'message sent to {}:{}'.format(*addr), 'info')
    # 连接建立

    data, addr = sock.recvfrom(1024)
    log_message(l, 'client received: {} {}'.format(addr, data), 'info')
    """

    # 设置wireguard
    """
    wireguard_thread = threading.Thread(target=setup_peer1, args=(*addr, 51820))
    wireguard_thread.start()
    """

    """
    # 启动发送数据的线程
    send_thread = threading.Thread(target=type_send, args=(sock, addr))
    send_thread.start()
    """

    # 启动接收数据的线程
    receive_thread = threading.Thread(target=type_recv, args=(sock, ))
    receive_thread.start()

    # 等待线程结束
    receive_thread.join()
   # send_thread.join()


if __name__ == '__main__':
    udp_client()
