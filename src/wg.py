#!/usr/bin/env python3

import subprocess
import logger
import os
import base64
import configparser
import shutil
from getpass import getpass

class wg:

    def __init__(self):

        self.password = ""    # Privilege password
        self.public   = ""    # Host peer public key
        self.private  = ""    # Host peer private key
        self.logger = logger.l # setting our own logger, but now we stick to the global one
        self.setlog()         # Setup the logger

    def setlog(self):
        
        if self.logger == None:
            self.logger = logger.logger()

    def password_getter(self):

        self.password = getpass("Authentication is required: \U0001F511 ")


    def run_as_root(self, c):

        # If the program is running as root, don't bother.
        if os.getuid() == 0:
            return self.run(c)

        if len(self.password) == 0:
            self.password_getter()

        command = "sudo -S {}".format(c)     # run as privileged user
        f = subprocess.run(command.split(), input=self.password, capture_output=True, check=False, text=True)
        return f.stdout, f.stderr, f.returncode

        """
        try:
            f = subprocess.run(command.split(), input=self.password, capture_output=True, check=True, text=True)
            return f.stdout, f.stderr, f.returncode
        except Exception as e:
            self.logger.log_message(e, "error")
        """


    def run(self, c, i=None):

        f = subprocess.run(c.split(), input=i, capture_output=True, check=False, text=True)
        return f.stdout, f.stderr, f.returncode

        """
        try:
            f = subprocess.run(c.split(), input=i, capture_output=True, check=True, text=True)
            return f.stdout, f.stderr, f.returncode
        except Exception as e:
            self.logger.log_message(e, "error")
        """

    # Check key pairs to see if they exist. Return True if they do, False otherwise
    def check_key_pairs(self, base='.wg-p2p'):

        base = base.rstrip('/')
        if os.path.exists(base):
            try:
                if os.path.exists(base+'/'+'public_key'):
                    with open(base+'/'+'public_key') as f:
                        pub = f.readline().rstrip()
                        if len(base64.b64decode(pub)) != 32:
                            raise ValueError("public_key文件内公钥长度非256bit")
                        else:
                            self.public = pub
                if os.path.exists(base+'/'+'private_key'):
                    with open(base+'/'+'private_key') as f:
                        priv = f.readline().rstrip()
                        if len(base64.b64decode(pub)) != 32:
                            raise ValueError("private_key文件内私钥长度非256bit")
                        else:
                            self.private = priv
            except Exception as e:
                self.logger.log_message(e, 'error')
                try:
                    # If anything doesn't checkout, remove the base directory
                    shutil.rmtree(base)
                except Exception as e:
                    self.logger.log_message(e, "error")
                    exit(-1)
                return False
            return True
        else:
            return False


    def generate_key_pairs(self, write_file=True, write_dir='.wg-p2p'):
        gen_private = self.run("wg genkey")[0].rstrip()
        gen_public = self.run("wg pubkey", gen_private)[0].rstrip()
        write_dir = write_dir.rstrip('/')
        if self.check_key_pairs(write_dir):     # Key pair already exists, and they will be read into the object
            ans = input("\033[93m检测到已经有一对密钥生成，你希望重新生成吗? [Y/n] \033[0m")
            if ans != 'N' and ans != 'n': # Wish to overwrite them
                self.private = gen_private
                self.public = gen_public
                if not write_file:      # Not recommended...
                    print("\033[91m警告！你选择不保存密钥，" \
                            + "这意味着下次运行程序你的密钥需要重新生成!\033[0m")
                else:
                    # recreate a new directory to store public and private keys
                    shutil.rmtree(write_dir)
                    os.mkdir(write_dir, 0o700)
                    with open('{}/public_key'.format(write_dir), 'w') as f:
                        f.write(self.public+'\n')
                    with open('{}/private_key'.format(write_dir), 'w') as f:
                        f.write(self.private+'\n')
            # else: we've already read both public key and private key in check_key_pairs().

        else:   # Key pair doesn't exist yet, we need to create a new pair.
            if os.path.exists(write_dir):
                shutil.rmtree(write_dir)
            os.mkdir(write_dir, 0o700)
            self.private = gen_private
            self.public = gen_public
            if not write_file:      # Again, not recommended and doesn't really make any sense.
                print("\033[91m警告！你选择不保存密钥，" \
                        + "这意味着下次运行程序你的密钥需要重新生成\033[0m")
            else:
               # write new key pair
               with open('{}/public_key'.format(write_dir), 'w') as f:
                   f.write(self.public+'\n')
               with open('{}/private_key'.format(write_dir), 'w') as f:
                   f.write(self.private+'\n')



    def check_interface(self, interface):

        t = self.run_as_root("ip link show {}".format(interface))
        if t[2] == 0:
            return True
        else:
            return False

    def create_interface(self, wg_addr, interface="wg-p2p0", mask=24):
        commands = [
                "ip link add dev {} type wireguard".format(interface),
                "ip address add dev {} {}/{}".format(interface, wg_addr, mask),
                "ip link set up dev {}".format(interface),
                ]
        for _ in commands:
            result = self.run_as_root(_)
            if len(result[0]) != 0: # 记录部署过程中的log
                self.logger.log_message(result[0], 'info')

        
    def configure_wireguard(self, interface='wg-p2p0', key_base_dir='.wg-p2p', port=51820, keep_alive=300, peers=[]):

        config = configparser.ConfigParser(strict=False)
        config.optionxform = str
        base_key_dir = key_base_dir.rstrip('/')
        config_file = "{}.conf".format(interface)

        # wg_conf[0] is for the host, others are for each peer
        wg_conf = []

        self.generate_key_pairs(write_file=True, write_dir=base_key_dir)

        wg_conf.append(
                {
                    "PrivateKey": self.private,
                    "ListenPort": port,
                })

        for _ in peers: # peers[] stores public key of each peer
            wg_conf.append(
                    {
                        "PublicKey": _,
                        "AllowedIPs": '0.0.0.0/0',
                        "PersistentKeepalive": keep_alive,
                    })
        with open(config_file, "w") as f:

            # Config record for this host
            config['Interface'] = wg_conf[0]
            config.write(f)
            config.remove_section('Interface')

            for _ in wg_conf[1:]:
                config['Peer'] = _
                config.write(f)
                config.remove_section('Peer')

        self.run_as_root("wg setconf {} {}".format(interface, config_file))

    def get_wg_peers(self, interface='wg-p2p0'):

        if self.check_interface(interface):
            peers = self.run_as_root("wg show {} peers".format(interface))[0].rstrip().split()
            return peers
        return None

    def get_wg_port(self, interface='wg-p2p0'):

        if self.check_interface(interface):
            listen_port = int(self.run_as_root("wg show {} listen-port".format(interface))[0].rstrip())
            return listen_port
        return None

    def get_wg_public(self, interface='wg-p2p0'):

        if self.check_interface(interface):
            public = self.run_as_root("wg show {} public-key".format(interface))[0].rstrip()
            return public
        return None

    # set endpoint for the peer `peer`
    def set_endpoint(self, peer, endpoint:tuple, interface='wg-p2p0'):

        # endpoint is a tuple -> (dst_addr, dst_port)
        try:
            if self.check_interface(interface):
                answer = self.run_as_root("wg set {} peer {} endpoint {}:{}".format(interface, peer, endpoint[0], endpoint[1]))
                if answer != 0:
                    logger.l.log_message("Failed to build a p2p tunnel between host and peer {}!".format(peer), "error")
                else:
                    logger.l.log_message("Setup the peer {} successful".format(peer), "info")
        
if __name__ == "__main__":
    w = wg()
    w.get_wg_peers()
