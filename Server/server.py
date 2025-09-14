import socket
import threading
import time

from datetime import datetime
from lib import connection_timeout_reached
from commands import CommandTypes, Command, CommandRoster
from client import Client
from enum import Enum

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
                Command(CommandTypes.LOGIN_COMMAND, {'login', 'l'}),
                Command(CommandTypes.ADDITIONAL_COMMAND, set())
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
            print(f"Server listening on {self.HOST}:{self.PORT}")

            self.start_matchmaking()
            print(f"Matchmaking online")

            while True:
                conn, addr = s.accept()
                client = Client(conn, addr)
                self.clients.add(client)
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=[client],
                    daemon=True
                )
                client_thread.start()
                print(f"Active connections: {len(self.clients)}")

    def send_help(self):
        pass

    def handle_client(self, client: Client):
        print(f'Connected by {client.addr} to {self.HOST}:{self.PORT}')
        connection_timestamp = datetime.now()
        greeting = True
        try:
            with client.conn:
                while True:
                    if connection_timeout_reached(connection_timestamp):
                        print(f"Connection timeout reached for {client.addr}.")
                        client.conn.sendall('q'.encode())
                        self.clients.remove(client)
                        break

                    if greeting:
                        client.conn.sendall(b'Welcome to StarGate Server! Reply with "h" to get command list.')
                        greeting = False

                    # if not client.is_logged_in():
                    #     client.conn.sendall(b'Please log in first. Alternatively, send "h" to get some help')

                    data = str(client.conn.recv(1024).decode())

                    if data:
                        if self.ALL_COMMANDS.command_exists(data):
                            match self.ALL_COMMANDS.command_type(data):
                                case CommandTypes.HELP_COMMAND:
                                    print(f"Help requested by {client.addr}.")
                                    self.send_help()

                                case CommandTypes.QUIT_COMMAND:
                                    print(f"Connection closure requested by {client.addr}.")
                                    break

                                case CommandTypes.MATCHMAKING_COMMAND:
                                    if client.is_logged_in():
                                        print(f"Matchmaking request from {client.addr}, Name '{client.get_name()}'.")
                                        self.matchmaking_clients.add(client)

                                case CommandTypes.REGISTER_COMMAND:
                                    name = self.ask_name()
                                    password = self.ask_password(registration=True)
                                    # DB

                                case CommandTypes.LOGIN_COMMAND:
                                    name = self.ask_name()
                                    password = self.ask_password(registration=False)
                                    # DB

                                case CommandTypes.ADDITIONAL_COMMAND:
                                    client.conn.sendall("How did you get here")
                                    pass

                                case _:
                                    client.conn.sendall(b"Invalid command!")
                        else:
                            client.conn.sendall(b'Invalid command!')

                    client.conn.sendall(data)
                    time.sleep(0.2)

        except Exception as e:
            print(f"Error with client {client.addr}: {e}")

        finally:
            self.clients.discard(client)
            self.matchmaking_clients.discard(client)
            print(f"Connection with {client.addr} closed")

    def matchmaking_loop(self):
        while True:
            while len(self.matchmaking_clients) >= 2:
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
