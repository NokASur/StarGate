import socket


class Client:
    def __init__(self, conn, addr):
        self.conn: socket = conn
        self.addr = addr
        self.logged_in: bool = False
        self.name: str or None = None

    def get_name(self):
        if self.logged_in and self.name is not None:
            return self.name
        return "User is unregistered"

    def is_logged_in(self):
        return self.logged_in
