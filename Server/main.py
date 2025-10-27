import time

from server import Server

if __name__ == '__main__':
    print("CONTAINER WAITS", flush=True)
    time.sleep(5)
    print("CONTAINER AWOKEN", flush=True)
    server = Server()
    server.start()
