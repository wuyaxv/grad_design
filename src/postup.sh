#!/usr/bin/env bash

sysctl net.ipv4.ip_forward=1
iptables -I FORWARD -i "$1" -j ACCEPT; iptables -I FORWARD -o "$1" -j ACCEPT; iptables -I INPUT -i "$1" -j ACCEPT; iptables -t nat -A POSTROUTING -o enp6s18 -j MASQUERADE
