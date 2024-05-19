import socket
import keyboard
import pyautogui
import threading
import time
from pynput.mouse import Listener
pyautogui.FAILSAFE = False


class ClientRemoteControl:
    def __init__(self, server_address):
        self.server_address = server_address
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(server_address)
        print(f"Connected to {self.server_address}")
        self.active_controlling = False

    def controlling(self):
        self.active_controlling = True
        self.client_socket.send(b'start')
        try:
            while self.active_controlling:
                data = self.client_socket.recv(1024).decode()
                if not data:
                    break
                message = data.split(",")
                if message[0] == "exit":
                    break
                if len(message) == 3:
                    if message[0] == 'mouse' and message[1].isnumeric() and message[2].isnumeric():
                        x = int(message[1])
                        y = int(message[2])
                        pyautogui.moveTo(x, y)
                    elif 'mouse' in message[0]:
                        pass
                    elif 'left' in message[0] or message[1] or message[2]:
                        pyautogui.click()
                    elif 'right' in message[0] or message[1] or message[2]:
                        pyautogui.rightClick()
                else:
                    if 'left' in message[0]:
                        pyautogui.click()
                    elif 'right' in message[0]:
                        pyautogui.rightClick()
                    elif len(message[0]) == 1:
                        keyboard.write(data)  # Simulate keystrokes on server
                    else:
                        pass
        except Exception as e:
            print(f"Error: {e}")

        print(f"Connection to {self.server_address} closed")
        self.client_socket.close()

    def start_controlling(self):
        self.active_controlling = True
        controlling_thread = threading.Thread(target=self.controlling)
        controlling_thread.start()
        controlling_thread.join()

    def stop_controlling(self):
        self.active_controlling = False


class ServerRemoteControl:
    def __init__(self, server_address):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(server_address)
        self.active_sharing = False
        self.server_socket.listen(1)
        self.client_socket, self.client_address = self.server_socket.accept()

    def send_mouse_position(self):
        while self.active_sharing:
            # Get mouse position
            x, y = pyautogui.position()

            # Send mouse position to server
            self.client_socket.send(f"mouse,{x},{y}".encode())

            # Sleep for a short duration to avoid excessive sending
            time.sleep(0.1)

    def send_keyboard_input(self):
        try:
            while self.active_sharing:
                key_event = keyboard.read_event()
                if key_event.event_type == keyboard.KEY_DOWN:
                    key = key_event.name
                    if key == "backspace":
                        self.client_socket.send(b'\x08')  # Send backspace character
                    elif key == "space":
                        self.client_socket.send(b' ')  # Send space character
                    elif key == "enter":
                        self.client_socket.send(b'\n')  # Send newline character
                    elif key == "shift":
                        # You may handle shift key press as needed
                        pass
                    # Add more key mappings as needed
                    else:
                        self.client_socket.send(key.encode())  # Send other characters
        except KeyboardInterrupt:
            print("Closing connection")
            self.client_socket.close()

    def on_click(self, x, y, button, pressed):
        if self.active_sharing:
            if pressed:
                if button == button.left:
                    self.client_socket.send(b'left')
                elif button == button.right:
                    self.client_socket.send(b'right')

    def detect_mouse_click(self):
        with Listener(on_click=self.on_click) as listener:
            listener.join()

    def start_controlling(self):
        if self.client_socket.recv(1024).decode() == 'start':
            self.active_sharing = True
            keyboard_thread = threading.Thread(target=self.send_keyboard_input)
            mouse_thread = threading.Thread(target=self.send_mouse_position)
            mouse_clicks_thread = threading.Thread(target=self.detect_mouse_click)
            keyboard_thread.start()
            mouse_thread.start()
            mouse_clicks_thread.start()
            keyboard_thread.join()
            mouse_thread.join()
            mouse_clicks_thread.join()

    def stop_controlling(self):
        self.active_sharing = False
