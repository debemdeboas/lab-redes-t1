import socket
import struct
from typing import List, Tuple
import netifaces

IFACE = 'eth0'
ETH_P_ALL = 3
ETH_FRAME_SIZE = 1518
ETH_CUSTOM_PROTOCOL = 0x8044

def create_and_bind_socket(iface: str) -> socket.SocketType:
    s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(ETH_P_ALL))
    s.bind((iface, 0))
    return s

def get_mac_data(iface: str) -> Tuple[List[int], List[int]]:
    src_mac_data = netifaces.ifaddresses(iface)[netifaces.AF_LINK][0]
    src_mac_addr = [int(d, 16) for d in src_mac_data['addr'].split(':')]
    broadcast_mac_addr = [int(d, 16) for d in src_mac_data['broadcast'].split(':')]
    return (src_mac_addr, broadcast_mac_addr)

def pack_eth_header(src: List[int], dst: List[int], packet_type: int = ETH_CUSTOM_PROTOCOL) -> bytes:
    return struct.pack('!6B6BH', *src, *dst, packet_type)

# def unpack_eth_header(buf: bytes) -> Tuple(List[int], List[int], int):
def unpack_eth_header(buf: bytes):
    if len(buf) > 14:
        buf = buf[:14]
    data = struct.unpack('!6B6BH', buf)
    src = [hex(b) for b in data[:6]]
    dst = [hex(b) for b in data[6:12]]
    packet_type = data[12:14][0]
    return src, dst, packet_type

def to_mac_str(mac: List[str]) -> str:
    return ':'.join([f'{m[2:].upper():02}' for m in mac])

# def from_mac_str(mac: str) -> bytearray:
#     mac = mac.split(':')


# src_mac_addr, broadcast_mac_addr = get_mac_data(IFACE)
# eth_header = build_eth_header(broadcast_mac_addr, src_mac_addr)

