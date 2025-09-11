"""Core modules for Jocul Cuvintelor app.

This package contains:
- state: shared game state container
- utils: JSON load/save helpers and broadcast helpers
- logic: GameController encapsulating game flow and timers
- dev_reload: optional watchdog-based auto-reload emitter
"""

__all__ = [
    "state",
    "utils",
    "logic",
    "dev_reload",
]
