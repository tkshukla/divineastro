"""A stand-in for an Ollama daemon, for the Starter emailed-answer tests (DIVASTRO-155).

Serves the two endpoints app/llm.py and app/emailed_answers.py call, on a free
localhost port, with no model behind them:

    GET  /api/tags   {"models": [{"name": <model>}]}
    POST /api/chat   streamed NDJSON chunks of a fixed English reading, then done

`FakeOllama.mode` switches behaviour: "ok", "error" (HTTP 500 on /api/chat),
"down" (every request 503, /api/tags included). Every /api/chat request body is
kept in `.requests` so a test can check the prompt it was sent.

    python -m tests.fake_ollama 11500     # run one by hand (e2e tests start it themselves)
"""

from __future__ import annotations

import json
import socket
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

READING = (
    "**Your career question.** The chart shows a steady rise through effort rather than luck. "
    "Saturn's influence on the tenth house asks for patience, and the running dasha supports "
    "responsibility and recognition that builds slowly.\n\n"
    "The coming period favours consolidating your position before a change. Keep records of "
    "your work, speak with seniors plainly, and avoid quarrels with colleagues.\n\n"
    "As a remedy, keep Saturdays simple and give help to people who work with their hands."
)


class FakeOllama:
    def __init__(self, model: str = "qwen2.5:7b", reply: str = READING, port: int = 0):
        self.model, self.reply, self.mode = model, reply, "ok"
        self.requests: list[dict] = []
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *a):            # quiet
                pass

            def _send(self, code: int, body: bytes, ctype="application/json"):
                self.send_response(code)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self):
                if outer.mode == "down":
                    return self._send(503, b"{}")
                if self.path.startswith("/api/tags"):
                    return self._send(200, json.dumps(
                        {"models": [{"name": outer.model}]}).encode())
                self._send(404, b"{}")

            def do_POST(self):
                length = int(self.headers.get("Content-Length") or 0)
                data = json.loads(self.rfile.read(length) or b"{}")
                if outer.mode == "down":
                    return self._send(503, b"{}")
                if not self.path.startswith("/api/chat"):
                    return self._send(404, b"{}")
                outer.requests.append(data)
                if outer.mode == "error":
                    return self._send(500, b'{"error":"model crashed"}')
                words = outer.reply.split(" ")
                lines = [json.dumps({"message": {"content": w + " "}, "done": False})
                         for w in words]
                lines.append(json.dumps({"done": True, "done_reason": "stop"}))
                self._send(200, ("\n".join(lines) + "\n").encode(), "application/x-ndjson")

        if not port:
            with socket.socket() as s:
                s.bind(("127.0.0.1", 0))
                port = s.getsockname()[1]
        self.port = port
        self.url = f"http://127.0.0.1:{port}"
        self.server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def start(self) -> "FakeOllama":
        self.thread.start()
        return self

    def stop(self) -> None:
        self.server.shutdown()
        self.server.server_close()


if __name__ == "__main__":
    fake = FakeOllama(port=int(sys.argv[1]) if len(sys.argv) > 1 else 0).start()
    print(fake.url, flush=True)
    try:
        fake.thread.join()
    except KeyboardInterrupt:
        fake.stop()
