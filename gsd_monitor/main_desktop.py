"""Start uvicorn on loopback + open pywebview window."""

from __future__ import annotations

import socket
import threading
import time

import uvicorn
import webview

from gsd_monitor.api.app import create_app


def _free_port() -> int:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def main() -> None:
    app = create_app()
    port = _free_port()
    cfg = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=port,
        log_level="warning",
        access_log=False,
    )
    server = uvicorn.Server(cfg)
    t = threading.Thread(target=server.run, daemon=True)
    t.start()
    for _ in range(50):
        try:
            socket.create_connection(("127.0.0.1", port), timeout=0.2).close()
            break
        except OSError:
            time.sleep(0.05)
    url = f"http://127.0.0.1:{port}/"
    webview.create_window("GSD Monitor", url, width=1280, height=840)
    webview.start(debug=False)


if __name__ == "__main__":
    main()
