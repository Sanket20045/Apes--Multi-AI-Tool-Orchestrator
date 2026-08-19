"""
Pleximus AI Agent — Web UI Backend Server
==========================================
Zero-dependency HTTP server built using Python's standard library http.server.
Serves static web assets (HTML/CSS/JS) and provides REST endpoints for Gemini orchestration.

Usage:
    python server.py
    # Open http://localhost:8000 in your browser
"""

import json
import mimetypes
import os
import sys

# Ensure UTF-8 output on Windows consoles if supported
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, List

from orchestrator import PleximusOrchestrator

PORT = 8000
WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")

# Shared orchestrator instance
orchestrator = PleximusOrchestrator()


class PleximusRequestHandler(BaseHTTPRequestHandler):
    """Custom HTTP Request Handler serving static web files and API endpoints."""

    def _set_headers(self, status_code: int = 200, content_type: str = "application/json") -> None:
        self.send_response(status_code)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()

    def do_OPTIONS(self) -> None:
        """Handle CORS pre-flight requests."""
        self._set_headers(204)

    def do_GET(self) -> None:
        """Handle GET requests for static assets and API status."""
        path = self.path.split("?")[0]

        # 1. API: Health and Status
        if path == "/api/status":
            status_data = {
                "status": "online",
                "gemini_connected": orchestrator.is_gemini_available(),
                "model": orchestrator.model_name,
                "tools": [
                    {
                        "name": "calculator",
                        "title": "Calculator",
                        "icon": "🧮",
                        "desc": "Safe AST math evaluator (arithmetic, functions, constants)"
                    },
                    {
                        "name": "weather_lookup",
                        "title": "Weather Lookup",
                        "icon": "🌦️",
                        "desc": "Live Open-Meteo current weather data"
                    },
                    {
                        "name": "text_utility",
                        "title": "Text Utility",
                        "icon": "📝",
                        "desc": "Word/char count, string reverse, case transformation"
                    },
                    {
                        "name": "currency_converter",
                        "title": "Currency Converter",
                        "icon": "💱",
                        "desc": "Live Frankfurter currency exchange rates"
                    }
                ]
            }
            self._set_headers(200, "application/json")
            self.wfile.write(json.dumps(status_data).encode("utf-8"))
            return

        # 2. Static File Serving
        if path == "/" or path == "":
            rel_path = "index.html"
        else:
            rel_path = path.lstrip("/")

        file_path = os.path.abspath(os.path.join(WEB_DIR, rel_path))

        # Security check: Prevent path traversal
        if not file_path.startswith(WEB_DIR) or not os.path.exists(file_path) or os.path.isdir(file_path):
            self._set_headers(404, "text/plain")
            self.wfile.write(b"404 Not Found")
            return

        content_type, _ = mimetypes.guess_type(file_path)
        if not content_type:
            content_type = "application/octet-stream"

        try:
            with open(file_path, "rb") as f:
                content = f.read()
            self._set_headers(200, content_type)
            self.wfile.write(content)
        except Exception as e:
            self._set_headers(500, "text/plain")
            self.wfile.write(f"500 Internal Server Error: {e}".encode("utf-8"))

    def do_POST(self) -> None:
        """Handle POST requests for chat orchestration."""
        path = self.path.split("?")[0]

        if path == "/api/chat":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode("utf-8")
                data = json.loads(body)
                message = data.get("message", "").strip()

                if not message:
                    self._set_headers(400, "application/json")
                    self.wfile.write(json.dumps({"success": False, "error": "Message cannot be empty."}).encode("utf-8"))
                    return

                # Collect tools used during orchestration
                tools_used: List[Dict[str, Any]] = []

                def on_tool(name: str, args: dict) -> None:
                    tools_used.append({"name": name, "arguments": args})

                # Process query through orchestrator
                response_text = orchestrator.process_query(message, on_tool_selected=on_tool)

                response_payload = {
                    "success": True,
                    "message": message,
                    "response": response_text,
                    "tools_used": tools_used,
                    "gemini_active": orchestrator.is_gemini_available()
                }

                self._set_headers(200, "application/json")
                self.wfile.write(json.dumps(response_payload).encode("utf-8"))

            except json.JSONDecodeError:
                self._set_headers(400, "application/json")
                self.wfile.write(json.dumps({"success": False, "error": "Invalid JSON body."}).encode("utf-8"))
            except Exception as e:
                self._set_headers(500, "application/json")
                self.wfile.write(json.dumps({"success": False, "error": f"Server error: {str(e)}"}).encode("utf-8"))
            return

        self._set_headers(404, "application/json")
        self.wfile.write(json.dumps({"success": False, "error": "Endpoint not found."}).encode("utf-8"))

    def log_message(self, format: str, *args: Any) -> None:
        """Keep console log clean and readable."""
        sys.stdout.write(f"[Server] {args[0]} - {args[1]} -> {args[2]}\n")


def run_server(port: int = PORT) -> None:
    """Start the multi-threaded HTTP server."""
    server_address = ("", port)
    httpd = ThreadingHTTPServer(server_address, PleximusRequestHandler)
    print("=" * 50)
    print(f"Apes AI Agent Web UI is LIVE!")
    print(f"URL: http://localhost:{port}")
    print(f"Gemini Live: {'YES' if orchestrator.is_gemini_available() else 'NO (Local fallback active)'}")
    print("=" * 50)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.server_close()


if __name__ == "__main__":
    run_server()
