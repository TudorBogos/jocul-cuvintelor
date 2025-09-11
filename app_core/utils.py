from __future__ import annotations

import json
import random
from typing import Any, Dict, List


def load_words(json_path: str = 'cuvinte.json') -> List[Dict[str, Any]]:
    """Load up to 14 unused words from JSON, resetting usage if needed."""
    with open(json_path, 'r+', encoding='utf-8') as f:
        all_words = json.load(f)
        for word in all_words:
            if 'utilizat' not in word:
                word['utilizat'] = 0

        available_words = [w for w in all_words if w.get('utilizat', 0) == 0]
        if len(available_words) < 14:
            for word in all_words:
                word['utilizat'] = 0
            available_words = all_words
            f.seek(0)
            json.dump(all_words, f, indent=4, ensure_ascii=False)
            f.truncate()

    random.shuffle(available_words)
    return available_words[:14]


def update_word_as_used(word_to_mark: str, json_path: str = 'cuvinte.json') -> None:
    """Mark a word as used in the JSON store."""
    with open(json_path, 'r+', encoding='utf-8') as f:
        all_words = json.load(f)
        for word in all_words:
            if word['cuvant'].upper() == word_to_mark.upper():
                word['utilizat'] = 1
                break
        f.seek(0)
        json.dump(all_words, f, indent=4, ensure_ascii=False)
        f.truncate()


def broadcast_game_state(socketio, game_state: Dict[str, Any]) -> None:
    """Emit the current state to both player and presenter views."""
    faza = game_state["faza_curenta"]
    current_player_name = (
        game_state["ordine_jucatori"][game_state["jucator_curent_index"]]
        if game_state["jucator_curent_index"] != -1
        else ""
    )

    # Mutăm acțiunea "cerere literă" de pe ecranul jucătorului pe ecranul prezentatorului.
    stare_butoane = {
        "jucator": {"cer_litera": False, "buton_rosu": faza == "tura_activa"},
        "prezentator": {
            "continua": faza
            in [
                "asteptare_jucator_nou",
                "confirmare_start_tura",
                "cuvant_rezolvat",
                "tura_incheiata",
            ],
            "validare": faza == "asteptare_validare",
            "cer_litera": faza == "tura_activa",
        },
    }

    payload = {
        "jucator_curent": current_player_name,
        "scor": game_state["scoruri"].get(current_player_name, 0),
        "definitie": game_state["cuvant_curent_display"]["definitie"],
        "litere_afisate": game_state["cuvant_curent_display"]["litere_ghicite"],
        "valoare_ramasa": game_state["cuvant_curent_display"]["valoare_ramasa"],
        "timp_ramas_main": game_state["timp_ramas_main"],
        "scoruri_finale": game_state["scoruri"],
        "stare_butoane": stare_butoane,
    }
    socketio.emit('update_jucator', payload)

    host_payload = dict(payload)
    host_payload["cuvant"] = game_state["cuvant_curent_display"]["cuvant_original"]
    socketio.emit('update_prezentator', host_payload)
