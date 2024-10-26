from modules.server.client_handler import handle_client
import socket

def start_server(host='localhost', port=8888):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)  # Allow multiple connections
    print(f"Server listening on {host}:{port}...")

    while True:
        conn, addr = server_socket.accept()
        print(f"Connection from {addr}")
        handle_client(conn)

if __name__ == "__main__":
    start_server()