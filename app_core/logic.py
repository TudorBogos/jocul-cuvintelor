from __future__ import annotations

import random
import threading
from typing import Dict, Any, List

from .state import game_state
from .utils import load_words, update_word_as_used, broadcast_game_state


class GameController:
    """Encapsulates the game flow and timers.

    This keeps Flask event handlers thin and improves readability.
    """

    def __init__(self, socketio):
        self.socketio = socketio

    # --- Timers ---
    def _main_timer_tick(self):
        if game_state["faza_curenta"] == "tura_activa" and game_state["timp_ramas_main"] > 0:
            game_state["timp_ramas_main"] -= 1
            self.socketio.emit('update_timer', {'type': 'main', 'time': game_state["timp_ramas_main"]})
            game_state["main_timer"] = threading.Timer(1.0, self._main_timer_tick)
            game_state["main_timer"].start()
        elif game_state["faza_curenta"] == "tura_activa":
            game_state["faza_curenta"] = "tura_incheiata"
            self.socketio.emit('show_message', "Timpul a expirat!")
            broadcast_game_state(self.socketio, game_state)

    def _answer_timer_tick(self):
        if game_state["faza_curenta"] == "asteptare_validare" and game_state["timp_ramas_answer"] > 0:
            game_state["timp_ramas_answer"] -= 1
            self.socketio.emit('update_timer', {'type': 'answer', 'time': game_state["timp_ramas_answer"]})
            game_state["answer_timer"] = threading.Timer(1.0, self._answer_timer_tick)
            game_state["answer_timer"].start()
        elif game_state["faza_curenta"] == "asteptare_validare":
            self.handle_answer_validation(is_correct=False, from_timeout=True)

    # --- Game flow ---
    def start_next_word(self):
        if game_state["main_timer"]:
            game_state["main_timer"].cancel()

        game_state["cuvant_curent_index"] += 1
        if game_state["cuvant_curent_index"] >= len(game_state["cuvinte_de_joc"]):
            game_state["faza_curenta"] = "tura_incheiata"
            self.socketio.emit('show_message', "Lista de cuvinte terminata!")
            broadcast_game_state(self.socketio, game_state)
            return

        word_data = game_state["cuvinte_de_joc"][game_state["cuvant_curent_index"]]
        cuvant = word_data["cuvant"].upper()

        game_state["cuvant_curent_display"] = {
            "definitie": word_data["definitie"],
            "litere_ghicite": ['_' for _ in cuvant],
            "valoare_ramasa": len(cuvant) * 100,
            "cuvant_original": cuvant,
        }
        update_word_as_used(cuvant)
        game_state["faza_curenta"] = "tura_activa"

        self._main_timer_tick()
        broadcast_game_state(self.socketio, game_state)

    def handle_answer_validation(self, is_correct: bool, from_timeout: bool = False):
        if game_state["answer_timer"]:
            game_state["answer_timer"].cancel()

        current_player_name = game_state["ordine_jucatori"][game_state["jucator_curent_index"]]
        valoare = game_state["cuvant_curent_display"]["valoare_ramasa"]
        cuvant = game_state["cuvant_curent_display"]["cuvant_original"]

        if is_correct:
            game_state["scoruri"][current_player_name] += valoare
            self.socketio.emit('show_feedback', {"corect": True, "cuvant": cuvant})
        else:
            game_state["scoruri"][current_player_name] -= valoare
            mesaj = "Timpul de raspuns a expirat!" if from_timeout else "Raspuns gresit!"
            self.socketio.emit('show_feedback', {"corect": False, "cuvant": cuvant, "mesaj": mesaj})

        game_state["faza_curenta"] = "cuvant_rezolvat"
        broadcast_game_state(self.socketio, game_state)

    def end_game(self):
        game_state["faza_curenta"] = "joc_incheiat"
        scoruri = game_state["scoruri"]
        if not scoruri:
            winner_message = "Jocul s-a incheiat fara castigatori."
        else:
            castigator = max(scoruri, key=scoruri.get)
            suma_castigata = scoruri[castigator]
            winner_message = f"FELICITARI! Castigatorul este {castigator} cu {suma_castigata} lei!"

        self.socketio.emit('show_message', winner_message)
        self.socketio.emit('game_over', {"scoruri": game_state["scoruri"]})
        broadcast_game_state(self.socketio, game_state)

    # --- Event helpers (used by Flask-SocketIO handlers) ---
    def on_start_game(self, players: List[str]):
        game_state["jucatori"] = players
        game_state["ordine_jucatori"] = random.sample(players, len(players))
        game_state["scoruri"] = {player: 0 for player in players}
        game_state["jucator_curent_index"] = -1
        game_state["faza_curenta"] = "asteptare_jucator_nou"
        broadcast_game_state(self.socketio, game_state)
        self.socketio.emit('show_message', "Joc configurat! Apasati 'Continua' pe ecranul prezentatorului pentru a incepe.")

    def on_next_step(self):
        faza = game_state["faza_curenta"]

        if faza == "asteptare_jucator_nou":
            game_state["jucator_curent_index"] += 1
            if game_state["jucator_curent_index"] >= len(game_state["ordine_jucatori"]):
                self.end_game()
                return

            current_player_name = game_state["ordine_jucatori"][game_state["jucator_curent_index"]]
            self.socketio.emit('show_message', f"Urmeaza {current_player_name}!")
            game_state["faza_curenta"] = "confirmare_start_tura"
            broadcast_game_state(self.socketio, game_state)

        elif faza == "confirmare_start_tura":
            game_state["cuvinte_de_joc"] = load_words()
            game_state["cuvant_curent_index"] = -1
            game_state["timp_ramas_main"] = 240
            self.start_next_word()

        elif faza == "cuvant_rezolvat":
            self.start_next_word()

        elif faza == "tura_incheiata":
            current_player_name = game_state["ordine_jucatori"][game_state["jucator_curent_index"]]
            self.socketio.emit('show_message', f"Tura lui {current_player_name} s-a incheiat. Scor: {game_state['scoruri'][current_player_name]} lei.")
            game_state["faza_curenta"] = "asteptare_jucator_nou"
            broadcast_game_state(self.socketio, game_state)

    def on_request_letter(self):
        if game_state["faza_curenta"] != "tura_activa":
            return

        cuvant = game_state["cuvant_curent_display"]["cuvant_original"]
        litere_ghicite = game_state["cuvant_curent_display"]["litere_ghicite"]

        pozitii_ramase = [i for i, char in enumerate(litere_ghicite) if char == '_']
        if not pozitii_ramase:
            return

        pozitie_random = random.choice(pozitii_ramase)
        litere_ghicite[pozitie_random] = cuvant[pozitie_random]

        game_state["cuvant_curent_display"]["valoare_ramasa"] = max(0, game_state["cuvant_curent_display"]["valoare_ramasa"] - 100)
        broadcast_game_state(self.socketio, game_state)

    def on_press_red_button(self):
        if game_state["faza_curenta"] != "tura_activa":
            return

        if game_state["main_timer"]:
            game_state["main_timer"].cancel()

        game_state["faza_curenta"] = "asteptare_validare"
        game_state["timp_ramas_answer"] = 30
        self._answer_timer_tick()
        broadcast_game_state(self.socketio, game_state)
