from __future__ import annotations

import os

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    _WATCHDOG_AVAILABLE = True
except Exception:
    _WATCHDOG_AVAILABLE = False


class _TemplateChangeHandler(FileSystemEventHandler if _WATCHDOG_AVAILABLE else object):
    def __init__(self, socketio, watch_exts=(".html", ".css", ".js")):
        self.socketio = socketio
        self.watch_exts = watch_exts

    def on_modified(self, event):  # type: ignore[override]
        try:
            if getattr(event, 'is_directory', False):
                return
            src = getattr(event, 'src_path', '')
            if any(src.endswith(ext) for ext in self.watch_exts):
                self.socketio.emit('reload')
        except Exception:
            pass


def start_dev_watcher(socketio, base_dir: str) -> object | None:
    if not _WATCHDOG_AVAILABLE:
        print("[dev] Watchdog not installed; browser auto-reload disabled. Install 'watchdog' to enable.")
        return None
    try:
        templates_dir = os.path.join(base_dir, 'templates')
        if not os.path.isdir(templates_dir):
            return None
        handler = _TemplateChangeHandler(socketio)
        observer = Observer()
        observer.schedule(handler, templates_dir, recursive=True)
        observer.daemon = True
        observer.start()
        print(f"[dev] Watching for changes in: {templates_dir}")
        return observer
    except Exception as ex:
        print(f"[dev] Failed to start file watcher: {ex}")
        return None
