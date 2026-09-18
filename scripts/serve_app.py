from __future__ import annotations

import argparse
import json
import mimetypes
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = ROOT / "web"
MAX_BODY_BYTES = 1_000_000

sys.path.insert(0, str(ROOT))

from scripts.writing_session import run_session


def read_repo_file(relative_path: str) -> str:
    path = ROOT / relative_path
    return path.read_text(encoding="utf-8")


def json_bytes(data: object, status: int = 200) -> tuple[int, bytes]:
    return status, json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")


def validate_text(value: object, field: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be text.")
    text = value.strip()
    if not text:
        raise ValueError(f"{field} is required.")
    if len(text) > 80_000:
        raise ValueError(f"{field} is too long for the local demo.")
    return text


def generate(payload: dict[str, object]) -> str:
    return run_session(payload)["markdown"]


def run_audit() -> dict[str, object]:
    completed = subprocess.run(
        [
            "powershell",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            "scripts\\portfolio_audit.ps1",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=45,
    )
    output = completed.stdout.strip()
    if completed.stderr.strip():
        output = f"{output}\n\n{completed.stderr.strip()}".strip()
    return {
        "ok": completed.returncode == 0 and "AUDIT RESULT: PASS" in output,
        "exitCode": completed.returncode,
        "output": output,
    }


class AppHandler(BaseHTTPRequestHandler):
    server_version = "LiteraryWritingAgent/1.0"

    def do_GET(self) -> None:
        if self.headers.get("Host") not in {f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"}:
            self.send_json({"error": "Host rejected"}, status=403)
            return
        parsed = urlparse(self.path)
        if parsed.path == "/api/health":
            self.send_json({"ok": True, "app": "Literary Writing Agent"})
            return
        if parsed.path == "/api/examples":
            self.send_json(
                {
                    "storyBrief": read_repo_file("examples/sample_story_brief.md"),
                    "characterSeed": read_repo_file("examples/sample_character_seed.md"),
                    "scene": read_repo_file("examples/sample_scene.md"),
                    "reviewExample": json.loads(read_repo_file("examples/revision-input.json")),
                    "reviewProposal": json.loads(read_repo_file("examples/revision-proposal.json")),
                }
            )
            return
        self.serve_static(parsed.path)

    def do_POST(self) -> None:
        expected = {f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"}
        origin = self.headers.get("Origin")
        if self.headers.get("Host") not in expected or (origin and origin not in {f"http://{h}" for h in expected}):
            self.send_json({"error": "Origin rejected"}, status=403)
            return
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/api/session":
                self.send_json({"ok": True, "session": run_session(self.read_json_body())})
                return
            if parsed.path == "/api/generate":
                payload = self.read_json_body()
                self.send_json({"ok": True, "result": generate(payload)})
                return
            if parsed.path == "/api/audit":
                self.send_json(run_audit())
                return
            self.send_json({"ok": False, "error": "Not found."}, status=404)
        except ValueError as error:
            self.send_json({"ok": False, "error": str(error)}, status=400)
        except subprocess.TimeoutExpired:
            self.send_json({"ok": False, "error": "Audit timed out."}, status=504)
        except Exception as error:  # pragma: no cover - last-resort local server guard.
            self.send_json({"ok": False, "error": "生成失败，请检查输入后重试。"}, status=500)

    def read_json_body(self) -> dict[str, object]:
        length = int(self.headers.get("Content-Length", "0"))
        if not 0 < length <= MAX_BODY_BYTES:
            raise ValueError("Request body is too large.")
        raw = self.rfile.read(length)
        if not raw:
            return {}
        data = json.loads(raw.decode("utf-8"))
        if not isinstance(data, dict):
            raise ValueError("Request body must be a JSON object.")
        return data

    def serve_static(self, request_path: str) -> None:
        if request_path in ("", "/"):
            file_path = WEB_ROOT / "index.html"
        else:
            relative = unquote(request_path.lstrip("/"))
            file_path = (WEB_ROOT / relative).resolve()
            if WEB_ROOT.resolve() not in file_path.parents and file_path != WEB_ROOT.resolve():
                self.send_json({"ok": False, "error": "Invalid path."}, status=403)
                return

        if not file_path.exists() or not file_path.is_file():
            self.send_json({"ok": False, "error": "Not found."}, status=404)
            return

        content_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        if file_path.suffix == ".js":
            content_type = "text/javascript; charset=utf-8"
        elif file_path.suffix in {".html", ".css"}:
            content_type = f"text/{file_path.suffix.lstrip('.')}; charset=utf-8"

        content = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
        self.end_headers()
        self.wfile.write(content)

    def send_json(self, data: object, status: int = 200) -> None:
        code, content = json_bytes(data, status=status)
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, format: str, *args: object) -> None:
        print(f"{self.address_string()} - {format % args}")


def find_port(start: int) -> int:
    for port in range(start, start + 20):
        try:
            server = ThreadingHTTPServer(("127.0.0.1", port), AppHandler)
        except OSError:
            continue
        server.server_close()
        return port
    raise RuntimeError("No available local port found.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Serve the local Literary Writing Agent app.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--check", action="store_true", help="Validate imports and static files, then exit.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.check:
        required = [WEB_ROOT / "index.html", WEB_ROOT / "styles.css", WEB_ROOT / "app.js"]
        missing = [str(path) for path in required if not path.exists()]
        if missing:
            raise SystemExit(f"Missing web files: {', '.join(missing)}")
        print("Local app check passed.")
        return

    if args.host not in ("127.0.0.1", "localhost"):
        raise SystemExit("This personal writing server binds to loopback only.")
    port = args.port if args.host != "127.0.0.1" else find_port(args.port)
    server = ThreadingHTTPServer((args.host, port), AppHandler)
    print(f"Literary Writing Agent app running at http://{args.host}:{port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()

