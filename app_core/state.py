"""Shared game state for Jocul Cuvintelor.

Avoids circular imports by being a simple module with plain data.
"""

from __future__ import annotations

game_state = {
    "faza_curenta": "inactiv",  # inactiv, asteptare_jucator_nou, confirmare_start_tura, tura_activa, asteptare_validare, cuvant_rezolvat, tura_incheiata, joc_incheiat
    "jucatori": [],
    "scoruri": {},
    "ordine_jucatori": [],
    "jucator_curent_index": -1,
    "cuvinte_de_joc": [],
    "cuvant_curent_index": -1,
    "main_timer": None,
    "answer_timer": None,
    "timp_ramas_main": 240,
    "timp_ramas_answer": 30,
    "cuvant_curent_display": {
        "definitie": "",
        "litere_ghicite": [],
        "valoare_ramasa": 0,
        "cuvant_original": "",
    },
}


def reset_state():
    """Reset the state back to initial values for a new game session."""
    game_state.update({
        "faza_curenta": "inactiv",
        "jucatori": [],
        "scoruri": {},
        "ordine_jucatori": [],
        "jucator_curent_index": -1,
        "cuvinte_de_joc": [],
        "cuvant_curent_index": -1,
        "main_timer": None,
        "answer_timer": None,
        "timp_ramas_main": 240,
        "timp_ramas_answer": 30,
        "cuvant_curent_display": {
            "definitie": "",
            "litere_ghicite": [],
            "valoare_ramasa": 0,
            "cuvant_original": "",
        },
    })
