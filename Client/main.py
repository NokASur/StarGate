import socket

HOST = '127.0.0.1'
PORT = 65432

running = True

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    data = s.recv(1024 * 8)
    print(f"Received {data!r}")

    while running:
        data_to_send = str(input())
        s.sendall(data_to_send.encode())
        try:
            data = s.recv(1024 * 8).decode().strip()
        except Exception as e:
            print(f"ERROR: {e}")

        print(f"{'_' * 20}SERVER RESPONDED WITH{'_' * 20}\n{data}")
        if data == 'q':
            running = False

    print("Closing client")
