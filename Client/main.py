import socket

HOST = '127.0.0.1'
PORT = 65432

running = True

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b"Hello, world")
    data = s.recv(1024)
    print(f"Received {data!r}")

    while running:
        data_to_send = str(input())
        s.sendall(data_to_send.encode())
        data = s.recv(1024)
        print(f"Received {data.decode()}")
        if data.decode() == 'q':
            running = False

    print("Closing client")
