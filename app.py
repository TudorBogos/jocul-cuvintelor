import os
from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO

from app_core.state import game_state
from app_core.logic import GameController
from app_core.dev_reload import start_dev_watcher

# Initializam aplicatia Flask si SocketIO la nivel de modul
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-final-revised!'
socketio = SocketIO(app)

# Controller-ul care contine logica jocului
controller = GameController(socketio)

# --- Rutele HTTP ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/joc')
def joc():
    return render_template('joc.html')

@app.route('/prezentator')
def prezentator():
    return render_template('prezentator.html')

@app.route('/buton-rosu')
def buton_rosu():
    return render_template('buton_rosu.html')

@app.route('/pictures/<path:filename>')
def pictures(filename):
    base_dir = os.path.dirname(__file__)
    pics_dir = os.path.join(base_dir, 'pictures')
    return send_from_directory(pics_dir, filename)

# --- Evenimente Socket.IO ---
@socketio.on('start_game')
def on_start_game(data):
    controller.on_start_game(data['players'])

@socketio.on('next_step')
def on_next_step():
    controller.on_next_step()

@socketio.on('request_letter')
def on_request_letter():
    controller.on_request_letter()

@socketio.on('press_red_button')
def on_press_red_button():
    controller.on_press_red_button()

@socketio.on('host_validation')
def on_host_validation(data):
    if game_state["faza_curenta"] != "asteptare_validare":
        return
    controller.handle_answer_validation(data['status'] == 'corect')

if __name__ == '__main__':
    base_dir = os.path.dirname(__file__)
    _observer = start_dev_watcher(socketio, base_dir)
    try:
        socketio.run(app, debug=True, host='0.0.0.0')
    finally:
        try:
            if _observer:
                _observer.stop()
                _observer.join(timeout=2.0)
        except Exception:
            pass
