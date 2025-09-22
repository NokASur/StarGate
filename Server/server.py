import socket
import threading
import time

from datetime import datetime
from lib import connection_timeout_reached, acceptable_name, acceptable_password
from commands import CommandTypes, Command, CommandRoster, server_command_roster
from client import Client, ClientStates
from Server.Database.database import Database

HOST = '127.0.0.1'
PORT = 65432


class Server:
    def __init__(self, host=HOST, port=PORT):
        self.ALL_COMMANDS: CommandRoster = server_command_roster

        self.HOST = host
        self.PORT = port

        self.clients: set[Client] = set()
        self.matchmaking_clients: set[Client] = set()

        self.matchmaking_thread = None

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.HOST, self.PORT))
            s.listen()
            print(f"Server listening on {self.HOST}:{self.PORT}\n")
            db = Database()
            self.start_matchmaking()
            print(f"Matchmaking online")

            while True:
                conn, addr = s.accept()
                client = Client(conn, addr)
                self.clients.add(client)
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=[client, db],
                    daemon=True
                )
                client_thread.start()
                print(f"Active connections: {len(self.clients)}\n")

    def send_help(self, client: Client):
        help_text = client.get_all_available_commands_help(self.ALL_COMMANDS)
        # help_text = self.ALL_COMMANDS.get_all_commands_help()
        client.conn.sendall(help_text.encode())

    def handle_client(self, client: Client, db: Database) -> None:
        print(f'Connected by {client.addr} to {self.HOST}:{self.PORT}\n')
        connection_timestamp = datetime.now()
        greeting = True
        try:
            with (client.conn):
                while True:
                    if connection_timeout_reached(connection_timestamp):
                        print(f"Connection timeout reached for {client.addr}.\n")
                        client.conn.sendall('q'.encode())
                        self.clients.remove(client)
                        break

                    if greeting:
                        client.conn.sendall(b'Welcome to StarGate Server! Reply with "h" to get command list.')
                        greeting = False

                    data = str(client.conn.recv(1024).decode()).strip()

                    if data:
                        command = data.split(' ')[0]
                        params = data.split(' ')[1:]
                        # Handling registration
                        if ClientStates.LOGGING_IN_NAME.value <= client.state.value <= ClientStates.REGISTRATION_PASSWORD_CONFIRMATION.value:
                            match client.state:
                                case ClientStates.LOGGING_IN_NAME:
                                    client.tmp_data_strg["name"] = data
                                    client.conn.sendall(b'Enter your password')
                                    client.state = ClientStates.LOGGING_IN_PASSWORD

                                case ClientStates.LOGGING_IN_PASSWORD:
                                    client.tmp_data_strg["password"] = data
                                    error = db.find_user_for_login(
                                        client.tmp_data_strg["name"],
                                        client.tmp_data_strg["password"]
                                    )
                                    if error:
                                        client.conn.sendall(f'logging failure: {error}'.encode())
                                        client.state = ClientStates.GUEST
                                        self.clean_temporary_client_data(client=client)
                                        continue
                                    db.create_user_session_into_pool(client.tmp_data_strg["name"])
                                    client.conn.sendall(
                                        f"Successfully logged in into"
                                        f" {client.tmp_data_strg["name"]}'s account.".encode())
                                    client.state = ClientStates.LOGGED_IN

                                case ClientStates.REGISTRATION_NAME:
                                    name = command
                                    if acceptable_name(name):
                                        client.conn.sendall(b'Enter your password')
                                        client.state = ClientStates.REGISTRATION_PASSWORD
                                        client.tmp_data_strg["name"] = name
                                    else:
                                        client.conn.sendall(b'Unacceptable name, try again')

                                case ClientStates.REGISTRATION_PASSWORD:
                                    password = command
                                    if acceptable_password(password):
                                        client.conn.sendall(b'Repeat your password')
                                        client.state = ClientStates.REGISTRATION_PASSWORD_CONFIRMATION
                                        client.tmp_data_strg["password"] = password
                                    else:
                                        client.conn.sendall(b'Unacceptable password, try again')

                                case ClientStates.REGISTRATION_PASSWORD_CONFIRMATION:
                                    password = command
                                    print(f"data: {password}, pswrd: {client.tmp_data_strg['password']}")
                                    if password == client.tmp_data_strg['password']:
                                        error = db.insert_user(
                                            client.tmp_data_strg["name"],
                                            client.tmp_data_strg["password"]
                                        )
                                        if error:
                                            client.conn.sendall(f'registration failure: {error}'.encode())
                                            client.state = ClientStates.GUEST
                                            self.clean_temporary_client_data(client=client)
                                            continue
                                        db.create_user_session_into_pool(client.tmp_data_strg["name"])
                                        client.state = ClientStates.LOGGED_IN
                                        client.conn.sendall(b'Registration complete.')

                                    else:
                                        client.conn.sendall(
                                            b'Passwords do not match. Enter your password from scratch.')
                                        client.state = ClientStates.REGISTRATION_PASSWORD

                        # Handling commands
                        elif self.ALL_COMMANDS.command_exists(command):
                            command_type = self.ALL_COMMANDS.command_type(command)
                            if client.command_available(command_type):
                                match command_type:
                                    case CommandTypes.HELP_COMMAND:
                                        print(f"Help requested by {client.addr}.")
                                        self.send_help(client)

                                    case CommandTypes.STATE_COMMAND:
                                        client.conn.sendall(
                                            f"Your current state description: {client.state.value.description}".encode()
                                        )

                                    case CommandTypes.QUIT_COMMAND:
                                        print(f"Connection closure requested by {client.addr}.")
                                        break

                                    case CommandTypes.MATCHMAKING_COMMAND:
                                        if client.is_logged_in():
                                            print(
                                                f"Matchmaking request from {client.addr}, Name '{client.get_name()}'.")
                                            self.matchmaking_clients.add(client)
                                            print(self.matchmaking_clients)
                                            client.conn.sendall(b"Searching")
                                        else:
                                            client.conn.sendall(
                                                b"Unregistered users cannot use matchmaking. "
                                                b"Please register."
                                            )

                                    case CommandTypes.REGISTER_COMMAND:
                                        if client.is_a_guest():
                                            client.conn.sendall(b'Enter your username')
                                            client.state = ClientStates.REGISTRATION_NAME
                                        else:
                                            client.conn.sendall(
                                                b"Registered users have to exit current account first.\n"
                                                b"Use 'lgt' to logout."
                                            )

                                    case CommandTypes.LOGIN_COMMAND:
                                        if client.is_a_guest():
                                            client.conn.sendall(b'Enter your username')
                                            client.state = ClientStates.LOGGING_IN_NAME
                                        else:
                                            client.conn.sendall(
                                                b"Registered users have to exit current account first.\n"
                                                b"Use 'lgt' to logout"
                                            )
                                    case CommandTypes.LOGOUT_COMMAND:
                                        self.clients.discard(client)
                                        self.matchmaking_clients.discard(client)
                                        db.session_pool.pop(client.tmp_data_strg["name"], None)
                                        print(f"User: {client.tmp_data_strg['name']} logged out")
                                        client.state = ClientStates.GUEST
                                        client.conn.sendall(b"Successfully logged out.")

                                    case CommandTypes.CREATE_LOBBY_COMMAND:
                                        db.create_lobby_from_user(client.tmp_data_strg["name"])
                                        client.state = ClientStates.GAME_LOBBY
                                        client.conn.sendall(b"Created and entered lobby.")

                                    case CommandTypes.GET_LOBBIES_COMMAND:
                                        lobbies = db.get_lobbies()
                                        reply = "Available lobbies:\n"
                                        for lobby in lobbies:
                                            reply += (
                                                f"Id: {lobby.id}, "
                                                f"type:{lobby.type}, "
                                                f"state: {lobby.state}, "
                                                f"open: {lobby.open}\n"
                                            )
                                        client.conn.sendall(reply.encode())

                                    case CommandTypes.SELECT_LOBBY_COMMAND:
                                        for ind in range(0, len(params)):
                                            param = params[ind]
                                            match param:
                                                case "-id":
                                                    ind += 1
                                                    try:
                                                        lobby_id = int(params[ind])
                                                        db.bind_user_to_lobby(
                                                            username=client.tmp_data_strg['name'],
                                                            lobby_id=lobby_id
                                                        )
                                                        client.state = ClientStates.GAME_LOBBY
                                                        client.conn.sendall(
                                                            f"Successfully entered lobby with id:{lobby_id}".encode()
                                                        )
                                                    except ValueError:
                                                        reply = f"Incorrect value for parameter {param}: {params[ind]}"
                                                        client.conn.sendall(reply.encode())
                                                    except Exception as e:
                                                        reply = repr(e)
                                                        client.conn.sendall(reply.encode())
                                                case _:
                                                    client.conn.sendall(b"Incorrect parameters")

                                    case CommandTypes.CHAT_COMMAND:
                                        pass

                                    case _:
                                        client.conn.sendall(
                                            b"Invalid command type.\n"
                                            b"This is a server problem, please report"
                                        )
                            else:
                                client.conn.sendall(b'Command unavailable from here')
                        else:
                            client.conn.sendall(b'Invalid command!')
                    time.sleep(0.2)

        except Exception as e:
            print(f"Error with client {client.addr}: {e}")

        finally:
            self.clients.discard(client)
            self.matchmaking_clients.discard(client)
            db.session_pool.pop(client.tmp_data_strg["name"], None)
            print(f"Connection with {client.addr} closed")

    def matchmaking_loop(self):
        while True:
            # print("Matchmaking loop")
            while len(self.matchmaking_clients) >= 2:
                print("Matchmaking game found")
                player1: Client = self.matchmaking_clients.pop()
                player2: Client = self.matchmaking_clients.pop()
                player1.state = ClientStates.GAME_LOBBY
                player2.state = ClientStates.GAME_LOBBY

                player1.conn.sendall(b'Match found, entering lobby')
                player2.conn.sendall(b'Match found, entering lobby')
            time.sleep(1)

    def start_matchmaking(self):
        self.matchmaking_thread = threading.Thread(
            target=self.matchmaking_loop,
            args=[],
            daemon=True
        )
        self.matchmaking_thread.start()

    @staticmethod
    def clean_temporary_client_data(client: Client):
        client.tmp_data_strg.clear()
