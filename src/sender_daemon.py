from lib.t1_protocol import *
from queue import Queue
from src.socket_daemon import RawSocketDaemon
from src.socket_utils import *
from threading import Timer


class SenderDaemon(RawSocketDaemon):
    def __init__(self, interface: str = ...) -> None:
        super().__init__(interface)
        self.q: Queue[Tuple[Header, T1Protocol]] = Queue()
        self.name = self.mac_str.upper()
        self.alive_timer = Timer(5, self.send_alive)
        self.alive_timer.daemon = True
        self.alive_timer.start()

    def run(self) -> None:
        while True:
            message = self.q.get()
            header, proto_data = message

            # print(f'Sending message {proto_data}')

            proto_data = proto_data.SerializeToString()
            self.socket.send(header + proto_data)

    def encode_message(self, type: T1ProtocolMessageType, dst: str, data: str = '') -> T1Protocol:
        return T1Protocol(type=type, name=self.name, data=data, dest=dst)

    def put(self, type: T1ProtocolMessageType, dst: List[str] | str, data: str = '') -> None:
        if isinstance(dst, str):
            dst_str = dst
            dst = dst.split(':')
        else:
            dst_str = ':'.join(dst)
        dest = [int(d, 16) for d in dst]
        msg = self.encode_message(type, '', data)
        header = Header(pack_eth_header(
            self.mac_address, dest, ETH_CUSTOM_PROTOCOL)
        )
        self.q.put((header, msg))

    def send_alive(self) -> None:
        # print('Sending alive')
        self.put(T1ProtocolMessageType.HEARTBEAT, MAC_BROADCAST)
        self.alive_timer = Timer(5, self.send_alive)
        self.alive_timer.daemon = True
        self.alive_timer.start()

    def ack_alive(self, to: str) -> None:
        # print(f'ack_alive {to}')
        self.put(T1ProtocolMessageType.HEARTBEAT, to.split(':'))
