import os
import time
from flask import Flask, request, send_from_directory, jsonify, render_template_string

app = Flask(__name__)
os.makedirs("dumps", exist_ok=True)
os.makedirs("uploads", exist_ok=True)

# Route POST pour recevoir logs
@app.route('/log', methods=['POST'])
def receive_log():
    data = request.get_json(force=True)
    log = data.get("log", "")
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    fname = time.strftime("dumps/log_%Y%m%d.txt")
    with open(fname, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {log}\n")
    return "OK", 200

# Route POST pour recevoir un dump mémoire
@app.route('/dump', methods=['POST'])
def receive_dump():
    data = request.get_json(force=True)
    content = data.get("dump", "")
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    fname = time.strftime("dumps/dump_%Y%m%d_%H%M%S.txt")
    with open(fname, "w", encoding="utf-8") as f:
        f.write(f"-- Dump reçu à {ts} --\n{content}\n")
    return "OK", 200

# Route POST pour uploader tout fichier binaire
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get("file")
    if file:
        fname = os.path.join("uploads", file.filename)
        file.save(fname)
        return f"File uploaded: {file.filename}", 200
    return "No file!", 400

# Route GET pour lister les dumps existants
@app.route('/dumps', methods=['GET'])
def list_dumps():
    files = sorted(os.listdir("dumps"))
    html = "<h2>Dumps disponibles :</h2><ul>"
    for f in files:
        html += f'<li><a href="/dumps/{f}">{f}</a></li>'
    html += "</ul><a href='/'>Retour à l\'exploit</a>"
    return html

# Route GET pour servir un dump spécifique
@app.route('/dumps/<path:fname>')
def serve_dump(fname):
    return send_from_directory("dumps", fname)

# Route GET simple pour tester l’API
@app.route('/api/ping')
def ping():
    return jsonify({"msg": "pong", "time": time.strftime("%H:%M:%S")})

# Home: sert la page exploit.html
@app.route('/')
def index():
    if os.path.exists("exploit.html"):
        return send_from_directory('.', 'exploit.html')
    return "<b>exploit.html manquant dans ce dossier !</b>", 404

# Servir les autres fichiers statiques (JS, etc)
@app.route('/<path:filename>')
def static_files(filename):
    if os.path.exists(filename):
        return send_from_directory('.', filename)
    return "Fichier non trouvé", 404

# Petite interface de debug pour voir les 20 derniers logs en live
@app.route('/logs')
def view_logs():
    files = sorted([f for f in os.listdir("dumps") if f.startswith("log_")])
    if not files:
        return "<b>Aucun log trouvé !</b>"
    last_log = files[-1]
    lines = []
    with open(os.path.join("dumps", last_log), encoding="utf-8") as f:
        lines = f.readlines()[-20:]
    html = "<h2>20 dernières lignes du log :</h2><pre>" + "".join(lines) + "</pre>"
    html += "<a href='/'>Retour à l\'exploit</a>"
    return html

if __name__ == '__main__':
    print("Démarrage du serveur Flask, accès :")
    print("  - PC :    http://localhost:5000/")
    print("  - Réseau : http://<IP-PC>:5000/ (ex: http://192.168.1.177:5000/)")
    app.run(host='0.0.0.0', port=5000)