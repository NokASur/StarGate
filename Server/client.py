import socket

from functools import total_ordering
from enum import Enum
from commands import CommandTypes, CommandRoster


@total_ordering
class State:
    def __init__(self, id, available_command_types: list[CommandTypes], description: str = "Not provided"):
        self.id = id
        self.available_command_types = available_command_types
        self.description = description

    def __eq__(self, other):
        return self.id == other.id

    def __lt__(self, other):
        return self.id < other.id


class ClientStates(Enum):
    GUEST = State(
        0,
        [
            CommandTypes.HELP_COMMAND,
            CommandTypes.STATE_COMMAND,
            CommandTypes.LOGIN_COMMAND,
            CommandTypes.REGISTER_COMMAND,
            CommandTypes.QUIT_COMMAND,
        ],
        "Guest (logged out user).\n"
    )

    LOGGING_IN_NAME = State(10, [], "In the process of entering name for logging in.\n")
    LOGGING_IN_PASSWORD = State(11, [], "In the process of entering password for logging in.\n")

    REGISTRATION_NAME = State(20, [], "In the process of entering name for registration.\n")
    REGISTRATION_PASSWORD = State(21, [], "In the process of entering password for registration.\n")
    REGISTRATION_PASSWORD_CONFIRMATION = State(22, [], "In the process of password confirmation.\n")

    LOGGED_IN = State(
        100,
        [
            CommandTypes.HELP_COMMAND,
            CommandTypes.STATE_COMMAND,
            CommandTypes.LOGOUT_COMMAND,
            CommandTypes.MATCHMAKING_COMMAND,
            CommandTypes.QUIT_COMMAND,
            CommandTypes.CREATE_LOBBY_COMMAND,
            CommandTypes.GET_LOBBIES_COMMAND,
            CommandTypes.SELECT_LOBBY_COMMAND,
        ],
        "Logged in user.\n"
    )

    GAME_LOBBY = State(201,
                       [
                           CommandTypes.HELP_COMMAND,
                           CommandTypes.STATE_COMMAND,
                           CommandTypes.CHAT_COMMAND,
                           CommandTypes.LEAVE_COMMAND,
                       ],
                       "In lobby.\n")  # add
    IN_GAME = State(202, [], "In game.\n")  # add


class Client:
    def __init__(self, conn, addr):
        self.conn: socket = conn
        self.addr = addr
        self.state: ClientStates = ClientStates.GUEST
        self.tmp_data_strg: dict[str, str | None] = {
            "name": None,
            "password": None,
        }
        self.heartbeat = True

    def is_logged_in(self):
        return self.state.value >= ClientStates.LOGGED_IN.value

    def is_a_guest(self):
        return self.state == ClientStates.GUEST

    def get_name(self):
        if self.is_logged_in():
            if self.tmp_data_strg["name"] is not None:
                return self.tmp_data_strg["name"]
            raise ValueError(f"Registered user's name is {None}")
        return None

    def command_available(self, command_type: CommandTypes) -> bool:
        return command_type in self.state.value.available_command_types

    def get_all_available_commands_help(self, roster: CommandRoster) -> str:
        reply = ""
        for command in roster.command_roster:
            if command.cmd_type in self.state.value.available_command_types:
                reply += command.help + "\n"
        return reply
