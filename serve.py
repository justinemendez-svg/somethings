#!/usr/bin/env python3
"""
Simple HTTP server to serve the dashboard (avoids CORS issues).
"""
import http.server
import socketserver
from pathlib import Path

PORT = 8000

Handler = http.server.SimpleHTTPRequestHandler
Handler.extensions_map['.json'] = 'application/json'

print(f"🚀 Starting dashboard server on http://localhost:{PORT}")
print(f"📂 Serving from: {Path.cwd()}")
print(f"🌐 Open: http://localhost:{PORT}/ai_penetration_dashboard.html")
print(f"\nPress Ctrl+C to stop\n")

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✅ Server stopped")
