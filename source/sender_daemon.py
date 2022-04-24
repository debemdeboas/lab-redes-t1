import threading
import socket_utils as sock_util


class ReceiverDaemon(threading.Thread):
    def __init__(self) -> None:
        threading.Thread.__init__(self, daemon=True)
        self.socket = sock_util.create_and_bind_socket(sock_util.IFACE)

    def run(self) -> None:
        print('starting')
        while True:
            data = self.socket.recv(sock_util.ETH_FRAME_SIZE)
            src, dst, packet_type = sock_util.unpack_eth_header(data[:14])

            if packet_type != sock_util.ETH_CUSTOM_PROTOCOL:
                continue

            src_mac_str = sock_util.to_mac_str(src)
            print(src_mac_str, bytearray([int(m, 16) for m in src_mac_str.split(':')]))

            # payload = bytearray(data[14:])
            # print(src, dst, packet_type, payload)
    
daemon = ReceiverDaemon()
daemon.start()
daemon.join()
