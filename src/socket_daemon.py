import src.socket_utils as sock_util
import threading


class RawSocketDaemon(threading.Thread):
    def __init__(self, interface: str = sock_util.pref_interface) -> None:
        threading.Thread.__init__(self, daemon=True)

        self.interface = interface
        self.socket = sock_util.create_and_bind_socket(self.interface)
        self.mac_address, self.mac_str = sock_util.get_mac_data(self.interface)

    def run(self) -> None:
        raise NotImplementedError()
