import socket
import threading

HOST = '127.0.0.1'
PORT = 65432

running = True


def handle_server_data(sock):
    global running
    while running:
        data = sock.recv(1024).decode()
        if data == 'Heartbeat\n':
            continue
        if data == 'q':
            running = False
        if data:
            print(f"{'_' * 20}SERVER SENT{'_' * 20}\n{data}")


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    data = s.recv(1024 * 8)
    print(f"{data}")

    handle_server_data_thread = threading.Thread(
        target=handle_server_data,
        args=[s],
        daemon=True
    )
    handle_server_data_thread.start()

    while running:
        data_to_send = str(input())
        s.sendall(data_to_send.encode())
    print("Closing client")
