from enum import Enum


class CommandTypes(Enum):
    HELP_COMMAND = "HELP_COMMAND"
    STATE_COMMAND = "STATE_COMMAND"
    QUIT_COMMAND = "QUIT_COMMAND"
    MATCHMAKING_COMMAND = "MATCHMAKING_COMMAND"
    REGISTER_COMMAND = "REGISTER_COMMAND"
    LOGIN_COMMAND = "LOGIN_COMMAND"
    LOGOUT_COMMAND = "LOGOUT_COMMAND"
    CREATE_LOBBY_COMMAND = "CREATE_LOBBY_COMMAND"
    GET_LOBBIES_COMMAND = "GET_LOBBIES_COMMAND"
    SELECT_LOBBY_COMMAND = "SELECT_LOBBY_COMMAND"
    CHAT_COMMAND = "CHAT_COMMAND"
    LEAVE_COMMAND = "LEAVE_COMMAND"


class Command:
    def __init__(self, cmd_type: CommandTypes, command_variants: set[str], help_text: str = "No help provided"):
        self.cmd_type = cmd_type
        self.commands = command_variants
        self.help = f"{cmd_type.value} : {command_variants} : {help_text}"


class CommandRoster:
    def __init__(self, command_types_list: list[Command]):
        self.command_roster = command_types_list
        self.command_dict = {
            command: command_type.cmd_type
            for command_type in command_types_list
            for command in command_type.commands
        }

    def command_exists(self, command: str) -> bool:
        return command in self.command_dict.keys()

    def command_type(self, command: str) -> CommandTypes:
        return self.command_dict[command]


server_command_roster = CommandRoster(
    [
        Command(
            CommandTypes.HELP_COMMAND,
            {'help', 'h'},
            "Prints all available commands from your current state."
        ),
        Command(
            CommandTypes.STATE_COMMAND,
            {'state', 'st'},
            "Prints your current state."
        ),
        Command(
            CommandTypes.QUIT_COMMAND,
            {'exit', 'quit', 'q'},
            "Closes connection to the server."
        ),
        Command(
            CommandTypes.MATCHMAKING_COMMAND,
            {'matchmaking', 'mm'},
            "Puts you in a matchmaking queue."
        ),
        Command(
            CommandTypes.REGISTER_COMMAND,
            {'register', 'reg'},
            "Starts a registration procedure."
        ),
        Command(
            CommandTypes.LOGIN_COMMAND,
            {'login', 'lgn'},
            "Starts a login procedure."
        ),
        Command(
            CommandTypes.LOGOUT_COMMAND,
            {'logout', 'lgt'},
            "Logs you out of your account."
        ),
        Command(
            CommandTypes.CREATE_LOBBY_COMMAND,
            {'create_lobby', 'crlb'},
            "Creates a customizable lobby."
        ),
        Command(
            CommandTypes.GET_LOBBIES_COMMAND,
            {'get_lobbies', 'lobbies', 'lob'},
            "Returns a list of all lobbies available."
        ),
        Command(
            CommandTypes.SELECT_LOBBY_COMMAND,
            {'select_lobby', 'select', 'selob', 's'},
            "Selecting a lobby. IMPORTANT, use -id X, where X is the id of the lobby you want to join\n"
            "Example: s -id 1"
        ),
        Command(
            CommandTypes.CHAT_COMMAND,
            {'chat', 'ch', 'text', 't'},
            "Send in-chat message."
        ),
        Command(
            CommandTypes.LEAVE_COMMAND,
            {'leave', 'l'},
            "Leave a lobby."
        )
    ]
)
