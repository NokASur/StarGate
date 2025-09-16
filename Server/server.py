import socket
import threading
import time

from datetime import datetime
from lib import connection_timeout_reached, acceptable_name, acceptable_password
from commands import CommandTypes, Command, CommandRoster
from client import Client, ClientStates
from Database.database import Database

HOST = '127.0.0.1'
PORT = 65432


class Server:
    def __init__(self, host=HOST, port=PORT):
        self.ALL_COMMANDS: CommandRoster = CommandRoster(
            [
                Command(CommandTypes.HELP_COMMAND, {'help', 'h'}),
                Command(CommandTypes.QUIT_COMMAND, {'exit', 'quit', 'q'}),
                Command(CommandTypes.MATCHMAKING_COMMAND, {'matchmaking', 'mm'}),
                Command(CommandTypes.REGISTER_COMMAND, {'register', 'reg'}),
                Command(CommandTypes.LOGIN_COMMAND, {'login', 'lgn'}),
                Command(CommandTypes.LOGOUT_COMMAND, {'logout', 'lgt'}),
                Command(CommandTypes.ADDITIONAL_COMMAND, {'placeholder'})
            ]
        )

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
        help_text = self.ALL_COMMANDS.get_all_commands_help()
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

                    # if not client.is_logged_in():
                    #     client.conn.sendall(b'Please log in first. Alternatively, send "h" to get some help')

                    data = str(client.conn.recv(1024).decode()).strip()

                    if data:
                        print("HERE1")
                        print(
                            ClientStates.LOGGING_IN_NAME.value <= client.state.value <= ClientStates.REGISTRATION_PASSWORD.value)
                        print(self.ALL_COMMANDS.command_exists(data))
                        # Handling registration
                        if ClientStates.LOGGING_IN_NAME.value <= client.state.value <= ClientStates.REGISTRATION_PASSWORD_CONFIRMATION.value:
                            print("HERE2")
                            match client.state:
                                case ClientStates.LOGGING_IN_NAME:
                                    client.conn.sendall(b'Enter your password')
                                    client.state = ClientStates.LOGGING_IN_PASSWORD
                                    client.temporary_data_storage["name"] = data

                                case ClientStates.LOGGING_IN_PASSWORD:
                                    client.temporary_data_storage["password"] = data
                                    if db.find_user(
                                            client.temporary_data_storage["name"],
                                            client.temporary_data_storage["password"]
                                    ):
                                        db.create_user_session_into_pool(client.temporary_data_storage["name"])
                                        client.conn.sendall(
                                            f"Successfully logged in into"
                                            f" {client.temporary_data_storage["name"]}'s account.")
                                        client.state = ClientStates.LOGGED_IN

                                case ClientStates.REGISTRATION_NAME:
                                    if acceptable_name(data):
                                        client.conn.sendall(b'Enter your password')
                                        client.state = ClientStates.REGISTRATION_PASSWORD
                                        client.temporary_data_storage["name"] = data
                                    else:
                                        client.conn.sendall(b'Unacceptable name, try again')

                                case ClientStates.REGISTRATION_PASSWORD:
                                    if acceptable_password(data):
                                        client.conn.sendall(b'Repeat your password')
                                        client.state = ClientStates.REGISTRATION_PASSWORD_CONFIRMATION
                                        client.temporary_data_storage["password"] = data
                                    else:
                                        client.conn.sendall(b'Unacceptable password, try again')

                                case ClientStates.REGISTRATION_PASSWORD_CONFIRMATION:
                                    print(f"data: {data}, pswrd: {client.temporary_data_storage['password']}")
                                    if data == client.temporary_data_storage['password']:
                                        client.conn.sendall(b'Registration complete.')
                                        db.create_user_session_into_pool(client.temporary_data_storage["name"])
                                        client.state = ClientStates.LOGGED_IN
                                    else:
                                        client.conn.sendall(
                                            b'Passwords do not match. Enter your password from scratch.')
                                        client.state = ClientStates.REGISTRATION_PASSWORD

                        # Handling commands
                        elif self.ALL_COMMANDS.command_exists(data):
                            print("HERE3")
                            match self.ALL_COMMANDS.command_type(data):
                                case CommandTypes.HELP_COMMAND:
                                    print(f"Help requested by {client.addr}.")
                                    self.send_help(client)

                                case CommandTypes.QUIT_COMMAND:
                                    print(f"Connection closure requested by {client.addr}.")
                                    break

                                case CommandTypes.MATCHMAKING_COMMAND:
                                    if client.is_logged_in():
                                        print(f"Matchmaking request from {client.addr}, Name '{client.get_name()}'.")
                                        self.matchmaking_clients.add(client)
                                        print(self.matchmaking_clients)
                                        client.conn.sendall(b"Searching")
                                    else:
                                        client.conn.sendall(
                                            b"Unregistered users cannot use matchmaking. "
                                            b"Please register."
                                        )

                                case CommandTypes.REGISTER_COMMAND:
                                    client.conn.sendall(b'Enter your username')
                                    client.state = ClientStates.REGISTRATION_NAME
                                    # DB

                                case CommandTypes.LOGIN_COMMAND:
                                    client.conn.sendall(b'Enter your username')
                                    client.state = ClientStates.LOGGING_IN_NAME
                                    # DB

                                case CommandTypes.ADDITIONAL_COMMAND:
                                    client.conn.sendall("How did you get here")
                                    pass

                                case _:
                                    client.conn.sendall(b"Invalid command!")
                        else:
                            print("HERE4")
                            client.conn.sendall(b'Invalid command!')
                        print("HERE5")
                    time.sleep(0.2)

        except Exception as e:
            print(f"Error with client {client.addr}: {e}")

        finally:
            self.clients.discard(client)
            self.matchmaking_clients.discard(client)
            db.session_pool.pop(client.temporary_data_storage["name"], None)
            print(f"Connection with {client.addr} closed")

    def matchmaking_loop(self):
        while True:
            print("Matchmaking loop")
            while len(self.matchmaking_clients) >= 2:
                print("Matchmaking game found")
                player1: Client = self.matchmaking_clients.pop()
                player2: Client = self.matchmaking_clients.pop()
                player1.conn.sendall(b'Match found')
                player2.conn.sendall(b'Match found')
            time.sleep(1)

    def start_matchmaking(self):
        self.matchmaking_thread = threading.Thread(
            target=self.matchmaking_loop,
            args=[],
            daemon=True
        )
        self.matchmaking_thread.start()

