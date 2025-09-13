import socket
import threading
import time

from datetime import datetime

HOST = '127.0.0.1'
PORT = 65432
connection_timeout = 80

quit_commands = {'exit', 'quit', 'q'}


def connection_timeout_reached(timestamp: datetime) -> bool:
    return (datetime.now() - timestamp).total_seconds() > connection_timeout


def handle_client(conn, addr):
    print(f'Connected by {addr}')
    connection_timestamp = datetime.now()
    try:
        with conn:
            while True:
                data = conn.recv(1024)

                if str(data.decode()).lower() in quit_commands:
                    print(f"Connection closure requested by {addr}.")
                    conn.sendall('q'.encode())
                    break

                if connection_timeout_reached(connection_timestamp):
                    print(f"Connection timeout reached for {addr}.")
                    break

                print(f"Received from {addr}: {data.decode()}\n")
                conn.sendall(data)
                time.sleep(1)
    except Exception as e:
        print(f"Error with client {addr}: {e}")
    finally:
        print(f"Connection with {addr} closed")


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")

        while True:
            conn, addr = s.accept()
            client_thread = threading.Thread(
                target=handle_client,
                args=(conn, addr),
                daemon=True
            )
            client_thread.start()
            print(f"Active connections: {threading.active_count() - 1}")


if __name__ == '__main__':
    main()
