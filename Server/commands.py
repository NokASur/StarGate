from enum import Enum


class CommandTypes(Enum):
    HELP_COMMAND = "HELP_COMMAND"
    QUIT_COMMAND = "QUIT_COMMAND"
    MATCHMAKING_COMMAND = "MATCHMAKING_COMMAND"
    REGISTER_COMMAND = "REGISTER_COMMAND"
    LOGIN_COMMAND = "LOGIN_COMMAND"
    ADDITIONAL_COMMAND = "ADDITIONAL_COMMAND"


class Command:
    def __init__(self, cmd_type: CommandTypes, commands: set[str]):
        self.cmd_type = cmd_type
        self.commands = commands


class CommandRoster:
    def __init__(self, command_types_list: list[Command]):
        self.command_roster = command_types_list
        self.command_dict = {
            command: command_type.cmd_type
            for command_type in command_types_list
            for command in command_type.commands
        }

    def command_exists(self, command: str) -> bool:
        return command in self.command_dict

    def command_type(self, command: str) -> CommandTypes:
        return self.command_dict[command]
