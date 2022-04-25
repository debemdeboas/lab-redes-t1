from lib.t1_protocol import *
from src.socket_daemon import RawSocketDaemon
from threading import Timer, Lock
from typing import Callable, Dict, Set
import src.socket_utils as sock_util
import time


class ReceiverDaemon(RawSocketDaemon):
    def __init__(self, ack_alive_func: Callable[..., None] = ..., interface: str = ...) -> None:
        super().__init__(interface)

        self.known_hosts: Set = {sock_util.MAC_BROADCAST}
        self.known_hosts_lock = Lock()

        self.alive_table: Dict[str, float] = {}
        self.alive_table_lock = Lock()

        self.last_contact: str = ''

        self.ack_alive = ack_alive_func
        self.alive_timer = Timer(15, self.check_known_hosts)
        self.alive_timer.daemon = True
        self.alive_timer.start()

    def check_known_hosts(self) -> None:
        try:
            self.alive_table_lock.acquire()
            for host, last_alive_time in self.alive_table.items():
                if time.time() - last_alive_time > 15:
                    print(f'Removing host {host} due to alive timeout')
                    self.alive_table.pop(host)
                    try:
                        self.known_hosts_lock.acquire()
                        self.known_hosts.remove(host)
                    except:
                        pass
                    self.known_hosts_lock.release()
        except:
            pass
        self.alive_table_lock.release()
        self.alive_timer = Timer(15, self.check_known_hosts)
        self.alive_timer.daemon = True
        self.alive_timer.start()

    def update_alive_table(self, host: str) -> None:
        try:
            self.alive_table_lock.acquire()
            self.alive_table[host] = time.time()
        except:
            pass
        self.alive_table_lock.release()

    def add_to_routing_table(self, host: str) -> None:
        if host in self.known_hosts:
            return
        print(f'Adding host {host} to routing table')
        try:
            self.known_hosts_lock.acquire()
            self.known_hosts.add(host)
        except:
            pass
        self.known_hosts_lock.release()
        self.update_alive_table(host)

    def print_routing_table(self) -> None:
        for host in self.known_hosts:
            print(f'Host\t{host}')

    def run(self) -> None:
        while True:
            packet = self.socket.recv(sock_util.ETH_FRAME_SIZE)
            src, dst, packet_type = sock_util.unpack_eth_header(
                sock_util.Header(packet[:14])
            )

            if packet_type != sock_util.ETH_CUSTOM_PROTOCOL:
                continue

            if src == self.mac_str:
                # print(1, src, self.mac_str)
                continue
            elif (data := T1Protocol.FromString(packet[14:])).name == self.mac_str:
                # print(2, data.name, self.mac_str)
                continue
            elif dst != sock_util.MAC_BROADCAST and dst != self.mac_str:
                # print(3, dst, self.mac_str)
                continue
            elif data.name not in self.known_hosts and \
                    data.type != T1ProtocolMessageType.START:
                if dst != sock_util.MAC_BROADCAST and data.type == T1ProtocolMessageType.HEARTBEAT:
                    # print('START response')
                    pass
                else:
                    # print(5, data.name, dst, self.known_hosts, data.type)
                    continue

            match data.type:
                case T1ProtocolMessageType.START:
                    self.add_to_routing_table(data.name)
                    self.ack_alive(data.name)
                case T1ProtocolMessageType.HEARTBEAT:
                    # print(f'Updating alive time for {data.name}')
                    if src != sock_util.MAC_BROADCAST:
                        self.add_to_routing_table(data.name)
                    self.update_alive_table(data.name)
                case T1ProtocolMessageType.TALK:
                    print(
                        f'TALK[From {src} ({data.name}) to {dst}]: {data.data}')
                    self.last_contact = data.name
                case _:
                    print(f'Unknown type. Type: {packet_type}')
