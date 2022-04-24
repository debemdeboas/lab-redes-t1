from typing import Callable, Dict
from src.socket_daemon import RawSocketDaemon
from src.sender_daemon import SenderDaemon
import src.socket_utils as sock_util
from lib.t1_protocol import *


class ReceiverDaemon(RawSocketDaemon):
    def __init__(self, ack_alive_func: Callable = ..., interface: str = ...) -> None:
        super().__init__(interface)

        self.routing_table: Dict[str, str] = {
            sock_util.MAC_BROADCAST: sock_util.MAC_BROADCAST
        }

        self.ack_alive = ack_alive_func

    def run(self) -> None:
        print('starting')
        while True:
            packet = self.socket.recv(sock_util.ETH_FRAME_SIZE)
            src, dst, packet_type = sock_util.unpack_eth_header(packet[:14])

            if packet_type != sock_util.ETH_CUSTOM_PROTOCOL \
                or dst not in [sock_util.MAC_BROADCAST, self.mac_str]:
                continue

            data = T1Protocol.FromString(packet[14:])
            print(f'From {src} to {dst} (proto {hex(packet_type)}): {str(T1ProtocolMessageType(data.type))[22:]} | {data.data}')

            match data.type:
                case T1ProtocolMessageType.START:
                    self.ack_alive(dst)
                case T1ProtocolMessageType.HEARTBEAT:
                    ...
                case T1ProtocolMessageType.TALK:
                    ...
                case _:
                    print(f'Unknown protocol type! Type: {packet_type}')
