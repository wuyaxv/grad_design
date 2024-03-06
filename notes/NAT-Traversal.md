## 1 NAT 类型

要了解NAT是什么，我们首先要理解为什么需要NAT。目前，我们使用的互联网仍然主要是以IPv4为主，而IPv4总共有$2^{32}$个，同时还要考虑部分保留用于内部网络IP地址的IP网段，导致的现实情况是IPv4不足以给互联网上的每一台机器都分配一个全球IP地址。因此，NAT设备应运而生，NAT设备通过网络地址转换的方式，将内网机器的内网`ip:port`对翻译成具有全球IP地址网关面向Internet的网口的一个`ip:port`对，同时在NAT设备内部会保存一张表以存储内网`ip:port`和外网`ip:port`的映射关系，以实现数据包可以在内外网之间相互传递。然而NAT设备有其自己的规则，有些NAT允许任何发送到特定`ip:port`的流量报传送到目的内网主机，也就是通常说的“Easy NAT”，但是有些NAT设备则指允许在NAT设备中建立明确的映射关系的外网主机和端口对发送数据包到内网主机中，也就是俗称的“Hard NAT”。

以下是具体的一些NAT类型和相关的一些术语。
### 1.1 Full Cone NAT, 全锥形NAT

全锥形NAT的特点是当内网主机向外网发送报文的时候会在NAT设备中形成一个如下的映射：`source ip:source port <---> gateway ip:gateway port <---> ANY ip:ANY port`，在这个关系中，任何外网主机如果向`gateway ip:gateway port`发送报文，都会被NAT设备Forward给内网主机`source ip:source port`。这种类型是最容易进行NAT穿透的，因为只需要对向特定主机发送出一个报文，任意获得网关IP和端口关系的主机都能够向内网主机发送报文，只需要发送给NAT设备的全球网关和端口号即可。
![[full-cone-nat.png]]
### 1.2 Restricted Cone NAT, 受限锥体 NAT
IP首先的NAT接受在NAT设备中建立了映射关系的IP设备的报文发送给在公网接口中已经打开的端口，其相较于Full Cone NAT，对返回到NAT设备的主机的源IP地址具有限制，但是不限制源主机发送回来报文的端口号。因此可以看作建立的映射是：`source ip:source port <---> gateway ip : gateway port <---> destination ip:ANY port`。
![[restricted-cone-nat.png]]

### 1.3 Port-Restricted Cone NAT，端口受限锥体NAT
相较于受限锥体NAT，添加了对发往公网`ip:port`的主机的端口限制，现在，只有内网发送到的确切的目的ip地址和端口号的地址可以发回数据包到NAT设备的对应的ip地址和端口号，否则会被NAT设备丢弃。对应的映射关系是：`source ip:source port <---> gateway ip : gateway port <---> destination ip:destination port`
![[restricted-port-cone-nat.png]]
### 1.4 Symmetric NAT, 对称NAT
相较于端口受限的锥体NAT，针对内网发出的每一条报文，其外部IP地址也可能会改变（PRC NAT的IP地址不会改变），这种情况基本上无法进行P2P。
![[symmetric-nat.png]]

## 2 不同NAT的穿透方案
|  Node-1   |  Node-2   | 能否穿透 | P2P方案 |
| :-------: | :-------: | :--: | ----- |
| Full-Cone | Full-Cone |  ✅   | STUN  |
| Full-Cone |  R-Cone   |  ✅   | STUN  |
| Full-Cone |  RP-Cone  |  ✅   |       |
| Full-Cone |  S-Cone   |  ✅   |       |
|  R-Cone   |  R-Cone   |  ✅   |       |
|  R-Cone   |  RP-Cone  |  ✅   |       |
|  R-Cone   |  S-Cone   |  ✅   |       |
|  RP-Cone  |  RP-Cone  |  ✅   |       |
|  RP-Cone  |  S-Cone   |  ❌   |       |
|  S-Cone   |  S-Cone   |  ❌   |       |
