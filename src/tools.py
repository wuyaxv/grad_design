#!/usr/bin/env python3

"""small tools but hugely helpful
"""

import re

def is_valid_ip_and_port(ip_port_str):
    # 使用正则表达式匹配IP:Port格式
    ip_port_pattern = r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|\[?[0-9a-fA-F:]+\]?):(\d{1,5})$'
    if re.match(ip_port_pattern, ip_port_str):
        return True
    else:
        return False
