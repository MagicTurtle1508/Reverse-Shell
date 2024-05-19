import socket
import threading
import time
from zlib import compress
from zlib import decompress
from mss import mss
import pyautogui
import pygame


class ScreenSharingClient:
    def __init__(self, server_address):
        self.udp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = server_address
        self.chunk_size = 50000
        self.active_sharing = False

    def start_sharing(self):
        self.active_sharing = True
        send_thread = threading.Thread(target=self.capture_and_send)
        send_thread.start()

    def stop_sharing(self):
        self.active_sharing = False

    def send_screen_shot(self, data, cursor_pos, width, height):
        header = f"first data:{len(data)},{width},{height},{cursor_pos[0]},{cursor_pos[1]}"
        self.udp_client_socket.sendto(header.encode(), self.server_address)

        offset = 0
        while offset < len(data):
            time.sleep(0.001)
            chunk = data[offset:offset + self.chunk_size]
            self.udp_client_socket.sendto(chunk, self.server_address)
            # offset += len(chunk)
            offset += self.chunk_size

    def capture_and_send(self):
        with mss() as sct:
            monitor = sct.monitors[1]
            while self.active_sharing:
                img = sct.grab(monitor)
                rgb_data = compress(img.rgb, 6)

                # Get mouse position
                cursor_pos = pyautogui.position()

                # Send screen shot and mouse position
                self.send_screen_shot(rgb_data, cursor_pos, monitor["width"], monitor["height"])


class ScreenSharingServer:
    def __init__(self, udp_server_address):
        self.udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_server_socket.bind(udp_server_address)
        self.receive_buffer = 50000
        self.active_sharing = False
        self.screen_size = (900, 700)
        self.screen_surface = pygame.Surface(self.screen_size)

    def start_sharing(self):
        self.active_sharing = True
        receive_thread = threading.Thread(target=self.receive_screen_shots)
        receive_thread.start()
        display_thread = threading.Thread(target=self.display_screen)
        display_thread.start()

    def stop_sharing(self):
        self.active_sharing = False

    def receive_screen_shots(self):
        while self.active_sharing:
            try:
                data, address = self.udp_server_socket.recvfrom(self.receive_buffer)
                data = data.decode()

                if data.startswith("first data:"):
                    header_length = len("first data:")
                    data_parts = data[header_length:].split(",")
                    length, width, height = map(int, data_parts[:3])
                    cursor_x, cursor_y = map(int, data_parts[3:])
                    screen_data_received = b""
                    while len(screen_data_received) < length:
                        chunk, _ = self.udp_server_socket.recvfrom(self.receive_buffer)
                        screen_data_received += chunk

                    rgb_data = decompress(screen_data_received)
                    self.screen_surface = pygame.image.fromstring(rgb_data, (width, height), 'RGB')

                    # Draw cursor at received position
                    pygame.draw.circle(self.screen_surface, (255, 255, 255), (cursor_x, cursor_y), 5)

            except Exception as e:
                # print("Error receiving screen shots:", e)
                continue

    def display_screen(self):
        pygame.init()
        screen = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption("Screen Sharing Server")
        clock = pygame.time.Clock()

        while self.active_sharing:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop_sharing()
                    pygame.quit()
                    return

            screen.blit(pygame.transform.smoothscale(self.screen_surface, screen.get_size()), (0, 0))
            pygame.display.flip()
