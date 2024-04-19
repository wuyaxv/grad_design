#!/usr/bin/env python3

import configparser
import base64
import os.path
import os
import sys
import subprocess
import logger
from io import StringIO

def setup_configs(*peer_path, config_file="wg0.conf", master_path=None, default_port=51820, keep_alive=300):

    peers = []
    master = None
    config = configparser.ConfigParser(strict=False)
    config.optionxform = str

    with open(config_file, 'w') as file:
        master_key = parse_keys(master_path, public=False, private=True)
        master = {
                     "PrivateKey": master_key[1],
                     "ListenPort": default_port,
                 }

        if len(peer_path) != 0:
            for _ in peer_path:
                p = parse_keys(_)
                peers.append(
                        {
                            "PublicKey": p[0],
                            "AllowedIPs": '0.0.0.0/0',
                            "PersistentKeepalive": keep_alive,
                        })

        config['Interface'] = master
        config.write(file)
        config.remove_section('Interface')

        for _ in peers:
            config['Peer'] = _
            config.write(file)
            config.remove_section('Peer')
            

def parse_keys(path, public=True, private=False):
    """Read from a directory which contains public and private key"""

    pub = None
    priv = None
    base = path.rstrip('/')
    
    try:
        # set to read public key.
        if public:
            if os.path.exists(base + '/' + 'public_key'):
                with open(base+'/public_key') as f:
                    pub = f.readline().rstrip()

                    if len(base64.b64decode(pub)) != 32:
                        raise ValueError("公钥必须长256bit")
            else:
                raise OSError("公钥文件不存在")

        # set to read private key.
        if private:
            if os.path.exists(base + '/' + 'private_key'):
                with open(base + '/' + 'private_key') as f:
                    priv = f.readline().rstrip()
                    if len(base64.b64decode(priv)) != 32:
                        raise ValueError("私钥必须长256bit")
            else:
                raise OSError("私钥文件不存在")

    except ValueError as e:
        print("读取密钥异常：" + repr(e))
    except OSError as e:
        print("读取密钥异常：" + repr(e))
    except Exception as e:
        print("读取密钥异常：" + repr(e))

    return pub, priv

def create_interface(wg_addr, interface="wg0", mask=24):

    if os.getuid() != 0:
        sys.stderr.write("Must run as root!\n")
        exit(-1)

    commands = [
            "ip link add dev {} type wireguard".format(interface),
            "ip address add dev {} {}/{}".format(interface, wg_addr, mask),
            "ip link set up dev {}".format(interface),
            "wg setconf {} wg0.conf".format(interface),
            ]

    try:
        result=None
        for _ in commands:
            result = subprocess.run(_.split(), capture_output=True, check=True, text=True)

    except subprocess.CalledProcessError as e:
        logger.l.log_message(e, "error")
    except Exception as e:
        logger.l.log_message(e, "error")
        
if __name__ == '__main__':
    
    setup_configs(*sys.argv[2:-1], master_path=sys.argv[1])
    create_interface(sys.argv[-1])

