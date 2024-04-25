#!/usr/bin/env bash
iptables -D FORWARD -i "$1" -j ACCEPT; iptables -D FORWARD -o "$1" -j ACCEPT; iptables -D INPUT -i "$1" -j ACCEPT; iptables -t nat -D POSTROUTING -o enp6s18 -j MASQUERADE
