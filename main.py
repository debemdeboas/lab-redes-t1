from lib.t1_protocol import *
from src.receiver_daemon import ReceiverDaemon
from src.sender_daemon import SenderDaemon
from src.socket_utils import pref_interface, MAC_BROADCAST

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


def execute(interface: str) -> None:
    writer = SenderDaemon(interface=interface)
    reader = ReceiverDaemon(
        ack_alive_func=writer.ack_alive, interface=interface)

    reader.start()
    writer.start()

    print_menu()
    while True:
        try:
            match (data := input('> ').split(' ', 1))[0].lower():
                case '0' | 'menu':
                    print_menu()
                case '1' | 'start':
                    writer.put(T1ProtocolMessageType.START, MAC_BROADCAST)
                case '2' | 'heartbeat':
                    writer.send_alive()
                case '3' | 'talk':
                    writer.put(T1ProtocolMessageType.TALK,
                               MAC_BROADCAST, data[1])
                case '4' | 'talkto':
                    to_whom = [mac.split(' ')[0] for mac in data[1].split(',')]
                    msg = data[1].split(' ', 1)[1:][0]
                    print(msg)
                    for to in to_whom:
                        writer.put(T1ProtocolMessageType.TALK, to, msg)
                case '5' | 'redial':
                    if not reader.last_contact:
                        print('No last contact!')
                        continue
                    writer.put(T1ProtocolMessageType.TALK,
                               reader.last_contact, data[1])
                case '6' | 'table':
                    reader.print_routing_table()
                case _:
                    print(f'Invalid input. {data[0]}')
        except KeyboardInterrupt:
            print('Goodbye!')
            exit(0)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    if sys.argv == 2:
        pref_interface = sys.argv[1]
        print(f'Starting on interface {pref_interface}')

    execute(pref_interface)
