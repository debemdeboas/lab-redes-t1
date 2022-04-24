from typing import Any, Tuple
from src.receiver_daemon import ReceiverDaemon
from src.sender_daemon import SenderDaemon
from src.socket_utils import IFACE, MAC_BROADCAST
from lib.t1_protocol import *

import sys

def print_menu() -> None:
    print("""
0. MENU: Prints this menu.
1. START: Sends a START message to the other nodes.
2. HEARTBEAT: Sends a HEARTBEAT message to the other nodes.
3. TALK <data>: Sends a TALK message to the broadcast address.
4. TALKTO <dest(s)> <data>: Sends a TALK message to the specified address.
   You can also pass a CSV list of addresses.
5. REDIAL <data>: Responds to the last TALK host(s)
6. TABLE: Prints the current address table.
          """)

def execute(interface: str = IFACE) -> None:
    writer = SenderDaemon(interface=interface)
    reader = ReceiverDaemon(ack_alive_func = writer.ack_alive, interface=interface)

    reader.start()
    writer.start()

    print_menu()
    while True:
        match (data := input('> ').split(' ', 1))[0].lower():
            case '0' | 'menu':
                print_menu()
            case '1' | 'start':
                writer.put(T1ProtocolMessageType.START, MAC_BROADCAST)
            case '2' | 'heartbeat':
                writer.send_alive()
            case '3' | 'talk':
                writer.put(T1ProtocolMessageType.TALK, MAC_BROADCAST, ''.join(data[1:]))
            case '6' | 'table':
                reader.print_routing_table()
            case _:
                print('Invalid input')


if __name__ == '__main__':
    print(sys.argv)

    execute()
