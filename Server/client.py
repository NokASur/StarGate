import socket

from enum import Enum


class ClientStates(Enum):
    GUEST = 0

    LOGGING_IN_NAME = 10
    LOGGING_IN_PASSWORD = 11

    REGISTRATION_NAME = 20
    REGISTRATION_PASSWORD = 21
    REGISTRATION_PASSWORD_CONFIRMATION = 22

    LOGGED_IN = 100


class Client:
    def __init__(self, conn, addr):
        self.conn: socket = conn
        self.addr = addr
        self.state: ClientStates = ClientStates.GUEST
        self.temporary_data_storage: dict[str, str | None] = {
            "name": None,
            "password": None,
        }

    def is_logged_in(self):
        return self.state == ClientStates.LOGGED_IN

    def get_name(self):
        if self.is_logged_in():
            if self.temporary_data_storage["name"] is not None:
                return self.temporary_data_storage["name"]
            raise ValueError(f"Registered user's name is {None}")
        return None
