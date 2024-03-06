#!/bin/bash

list_files=( 
        util.py
        udp_server.py
        udp_client.py
        logger.py
        _server.py
        _client.py
        )

PASSWORD='displaycode@joshua'
# sshpass -p $PASSWORD scp ${list_files[@]} wuyaxu@120.79.143.252:/home/wuyaxu/
sshpass -p $PASSWORD scp ${list_files[@]} wuyaxu@49.232.213.235:/home/wuyaxu/
sshpass -p $PASSWORD scp -P 10023 ${list_files[@]} wuyaxu@192.168.6.135:/home/wuyaxu
sshpass -p $PASSWORD scp -P 10022 ${list_files[@]} wuyaxu@192.168.6.135:/home/wuyaxu
sshpass -p $PASSWORD scp -P 10022 ${list_files[@]} wuyaxu@192.168.6.206:/home/wuyaxu


