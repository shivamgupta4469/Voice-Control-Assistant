from flask import Flask, jsonify, render_template_string
import os

app = Flask(__name__)

PAGE = """<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Voice Assistant Dashboard</title><style>
body{margin:0;background:#0b1020;color:#f4f7ff;font:16px system-ui;display:grid;min-height:100vh;place-items:center}
main{max-width:680px;padding:36px;background:#141e35;border:1px solid #293858;border-radius:18px;margin:20px}
p{color:#b3bfd8}a{color:#b8caff}.pill{display:inline-block;padding:6px 10px;background:#193b2c;color:#a9f0c7;border-radius:30px}
</style></head><body><main><span class="pill">Web service online</span><h1>Voice Control Assistant</h1>
<p>This is the cloud information dashboard for the desktop project. The microphone, local files, screen reader and Ollama model remain on your Windows computer.</p>
<p>Health check: <a href="/health">/health</a></p><p>Source: <a href="https://github.com/shivamgupta4469/Voice-Control-Assistant">GitHub repository</a></p>
</main></body></html>"""

@app.get("/")
def home():
    return render_template_string(PAGE)

@app.get("/health")
def health():
    return jsonify(status="ok", service="voice-assistant-project-dashboard")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
