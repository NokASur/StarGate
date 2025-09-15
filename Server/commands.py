from enum import Enum


class CommandTypes(Enum):
    HELP_COMMAND = "HELP_COMMAND"
    QUIT_COMMAND = "QUIT_COMMAND"
    MATCHMAKING_COMMAND = "MATCHMAKING_COMMAND"
    REGISTER_COMMAND = "REGISTER_COMMAND"
    LOGIN_COMMAND = "LOGIN_COMMAND"
    LOGOUT_COMMAND = "LOGOUT_COMMAND"
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
        print(command)
        print("____")
        return command in self.command_dict.keys()

    def command_type(self, command: str) -> CommandTypes:
        return self.command_dict[command]

    def get_all_commands_help(self):
        help_text = ""
        for command in self.command_dict:
            # RE DO: CLARIFY COMMANDS (Remake class)
            help_text += command + "\n"
        return help_text
