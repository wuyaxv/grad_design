#!/usr/bin/env python3

# ultimate user interface (unfortunately cli at this time).

import wg
import client
import server
import argparse
import logger
import sys
import base64
from tools import is_valid_ip_and_port

def get_parser():

    parser = argparse.ArgumentParser(prog="wg-p2p",
                                     description="Building P2P Tunnel using WireGuard."
                                     )

    parser.add_argument('-v', '--verbose', action="store_true", help="打开调试信息")
    parser.add_argument('-S', '--server', action="store_true", help="作为服务器运行")
    parser.add_argument('-C', '--client', action="store_true", help="作为客户端运行")
    parser.add_argument('-s', '--destination', type=str, help="客户端指定服务器ip地址")
    parser.add_argument('-p', '--port', type=int, default=12345, help="作为客户端指定服务器端口，作为服务器指定监听端口")
    parser.add_argument('-g', '--generate-keypair', action="store_true", help='生成并打印WireGuard公私钥对，然后退出')
    parser.add_argument('-P', '--print-key-pairs', action="store_true", help="打印存在的WireGuard公私密钥对")
    parser.add_argument('--peer', action='append', help="指定要建立连接的节点公钥")
    parser.add_argument('-d', '--output-dir', type=str, default='.wg-p2p', help="设置WireGuard公私密钥存储文件夹，默认为./.wg-p2p")
    parser.add_argument('--allowed-ips', type=str, help="指定当前节点的WireGuard端点虚拟ip地址，格式为：{IP}:{PORT}")

    return parser.parse_args()

if __name__ == '__main__':

    args = get_parser()

    if args.verbose == True:
        logger.l.do_log = True
    else:
        logger.l.do_log = False
    
    logger.l.log_message(args)
    wg = wg.wg()


    if args.server and args.client:
        print("选项-C与-S冲突", file=sys.stderr)
        exit(-1)

    if args.generate_keypair and not (args.server and args.client):
        wg.generate_key_pairs(write_dir=args.output_dir)
        wg.check_key_pairs(base=args.output_dir, print_key=True)
        exit(0)

    if args.server:
        try:
            if args.port != None:
                server.server(listening_port=args.port)
            else:
                server.server()
        except KeyboardInterrupt:
            print('Exiting server...')
            exit(0)

    if args.print_key_pairs:
        wg.print_key_pairs(args.output_dir)

    if args.client:
        if args.port == None \
           or args.destination == None:
            print("\033[91m未指定服务器地址或端口，退出\033[0m", file=sys.stderr)
            logger.l.log_message('未指定端口或目的地址', 'error')
            exit(-1)

        if args.allowed_ips == None:
            logger.l.log_message("未指定WireGuard的Endpoint地址或端口")
            if not is_valid_ip_and_port(args.allowed_ips):
                logger.l.log_message("指定的Endpoint格式不正确", "error")
                print("\033[91m指定的Endpoint格式不正确，正确格式：--endpoint {IP}:{PORT}\033[0m", file=sys.stderr)
            exit(-1)

        if len(args.peer) != 0:
            for _ in args.peer:
                if len(base64.b64decode(_)) != 32:
                    args.peer.remove(_)
                    print("\033[91mpeer公钥不合规: {}\033[0m".format(_), file=sys.stderr)

        wg_ip, wg_port = args.allowed_ips.split(':')[0], int(args.allowed_ips.split(':')[1])
        print(wg_ip, wg_port)

        client.client(wg_ip, (args.destination, args.port), wg_port=wg_port, peers=args.peer)





        
        
