from queue import Queue
from src.socket_daemon import RawSocketDaemon
from lib.t1_protocol import *
from src.socket_utils import *
from typing import NewType
from threading import Lock, Timer

Header = NewType('Header', bytes)

class SenderDaemon(RawSocketDaemon):
    def __init__(self, interface: str = ...) -> None:
        super().__init__(interface)
        self.q: Queue[Tuple[Header, T1Protocol]] = Queue()
        self.name = self.mac_str.upper()
        self.lock = Lock()
        self.alive_timer = Timer(5, self.send_alive)
        self.alive_timer.start()

    def run(self) -> None:
        print('starting')
        while True:
            message = self.q.get()
            
            header, proto_data = message
            proto_data = proto_data.SerializeToString()
            # print(message)
            self.socket.send(header + proto_data)


    def encode_message(self, type: T1ProtocolMessageType, data: str = '') -> T1Protocol:
        return T1Protocol(type, self.name, data)

    def put(self, type: T1ProtocolMessageType, dst: List[str], data: str = '') -> None:
        dest = [int(d, 16) for d in dst]
        msg = self.encode_message(type, data)
        header = Header(pack_eth_header(self.mac_address, dest, ETH_CUSTOM_PROTOCOL))
        self.q.put((header, msg))

    def send_alive(self) -> None:
        self.put(T1ProtocolMessageType.HEARTBEAT, self.broadcast)
        self.alive_timer.run()

    def ack_alive(self, to: str) -> None:
        self.put(T1ProtocolMessageType.HEARTBEAT, to.split(':'))
