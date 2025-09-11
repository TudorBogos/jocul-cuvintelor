# jocul-cuvintelor
O versiune web a jocului TV 'Jocul Cuvintelor', realizata cu Flask si SocketIO. Suporta multiplayer in timp real, unde jucatorii incearca sa ghiceasca cuvinte pe baza definitiilor, iar un prezentator gestioneaza desfasurarea jocului.

## Structura proiectului

- `app.py` – rute Flask si evenimente Socket.IO subtiri; initializeaza aplicatia si controllerul.
- `app_core/`
	- `state.py` – starea globala de joc (in-memorie) si `reset_state()`.
	- `utils.py` – functii utilitare pentru JSON si `broadcast_game_state`.
	- `logic.py` – `GameController` cu logica jocului si timerele.
	- `dev_reload.py` – watchdog pentru auto-reload in browser (optional).
- `templates/` – `index.html`, `joc.html`, `prezentator.html`.
- `cuvinte.json` – lista de cuvinte si marcajul `utilizat`.

## Dezvoltare

Instalare dependinte:

```powershell
python -m pip install -r .\requirements.txt
```

Rulare server:

```powershell
python .\app.py
```

Cu `debug=True`, modificarile Python repornesc serverul, iar modificarile de template trimit un eveniment `reload` catre clienti (daca pachetul `watchdog` este instalat) pentru a reimprospata paginile automat.

## Note

- Starea se pierde la restart; pentru persistenta, folositi o baza de date sau Redis.
- Evitati editarea fisierului `cuvinte.json` in timpul jocului (se fac scrieri concurente).
