"""Preview README.md locally — run with `python3 _preview.py` or `python3 _preview.py --watch`."""
import markdown, webbrowser, sys, time
from pathlib import Path

ROOT = Path(__file__).parent
README = ROOT / "README.md"
OUT = ROOT / "_preview" / "index.html"
OUT.parent.mkdir(exist_ok=True)

CSS = """
body {
  max-width: 900px; margin: 0 auto; padding: 40px 20px;
  background: #ffffff; color: #1f2328;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
}
a { color: #0969da; text-decoration: none; }
img { max-width: 100%; }
pre { background: #f6f8fa; padding: 16px; border-radius: 6px; overflow-x: auto; }
code { background: #eff1f3; padding: 2px 6px; border-radius: 3px; font-size: 85%; }
pre code { background: none; padding: 0; }
hr { border: 0; border-top: 1px solid #d1d9e0; margin: 24px 0; }
table { border-collapse: collapse; }
td, th { padding: 6px 13px; border: 1px solid #d1d9e0; }
"""

RELOAD_JS = """
<script>
  setInterval(async () => {
    try { const r = await fetch('/reload-check'); if (r.ok) location.reload(); } catch(e) {}
  }, 1000);
</script>
"""

def build():
    md = README.read_text()
    # strip the first <div align="center"> wrapper so two rows work
    html = markdown.markdown(md, extensions=["extra", "md_in_html", "tables"])
    watch_mode = "--watch" in sys.argv
    reload_block = RELOAD_JS if watch_mode else ""
    OUT.write_text(
        f"<!DOCTYPE html><html><head><meta charset=utf-8><style>{CSS}</style>{reload_block}</head>"
        f"<body>{html}</body></html>"
    )
    return OUT

def watch():
    last = README.stat().st_mtime
    print(f"  watching {README} — edit & save, browser auto-refreshes")
    while True:
        time.sleep(0.5)
        try:
            mtime = README.stat().st_mtime
            if mtime != last:
                last = mtime
                build()
                print(f"  updated {time.strftime('%H:%M:%S')}")
        except FileNotFoundError:
            pass

if "--watch" in sys.argv:
    import threading, http.server, os
    build()
    # HTTP server that also signals reload
    class Handler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/reload-check":
                self.send_response(204); self.end_headers(); return
            return super().do_GET()
        def log_message(self, f, *a): pass

    os.chdir(OUT.parent)
    s = http.server.HTTPServer(("", 8765), Handler)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    print(f"→ http://localhost:8765/")
    webbrowser.open("http://localhost:8765/")
    watch()
else:
    out = build()
    webbrowser.open(str(out))
    print(f"→ {out}")
