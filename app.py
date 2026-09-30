import os
from functools import wraps
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from supabase import create_client, Client

current_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(current_dir, ".env"))

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "billy2026")

supabase_client: Client = None

def get_supabase() -> Client:
    global supabase_client
    if supabase_client is None:
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return supabase_client

def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer ") or auth.split(" ")[1] != ADMIN_PASSWORD:
            return jsonify({"error": "Non autorise"}), 401
        return f(*args, **kwargs)
    return decorated

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "online", "message": "API Flask operationnelle"}), 200

@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    if data.get("password") == ADMIN_PASSWORD:
        return jsonify({"success": True, "token": ADMIN_PASSWORD}), 200
    return jsonify({"error": "Mot de passe incorrect"}), 401

@app.route("/api/projects", methods=["GET"])
def get_projects():
    try:
        res = get_supabase().table("projects").select("*").order("order_index").execute()
        return jsonify(res.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/projects", methods=["POST"])
@require_admin
def create_project():
    try:
        data = request.get_json() or {}
        for field in ["name_fr", "name_en", "description_fr", "description_en"]:
            if not data.get(field):
                return jsonify({"error": f"'{field}' est obligatoire"}), 400
        payload = {k: data[k] for k in ["name_fr","name_en","description_fr","description_en"]}
        payload["stack"] = data.get("stack", [])
        payload["link"] = data.get("link", "#")
        payload["order_index"] = int(data.get("order_index", 0))
        res = get_supabase().table("projects").insert(payload).execute()
        return jsonify(res.data[0] if res.data else payload), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/projects/<int:pid>", methods=["PUT"])
@require_admin
def update_project(pid):
    try:
        data = request.get_json() or {}
        data.pop("id", None)
        data.pop("created_at", None)
        res = get_supabase().table("projects").update(data).eq("id", pid).execute()
        return jsonify(res.data[0] if res.data else {}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/projects/<int:pid>", methods=["DELETE"])
@require_admin
def delete_project(pid):
    try:
        get_supabase().table("projects").delete().eq("id", pid).execute()
        return jsonify({"message": f"Projet {pid} supprime"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/skills", methods=["GET"])
def get_skills():
    try:
        res = get_supabase().table("skills").select("*").order("order_index").execute()
        return jsonify(res.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/skills", methods=["POST"])
@require_admin
def create_skill():
    try:
        data = request.get_json() or {}
        if not data.get("name") or data.get("level") is None:
            return jsonify({"error": "'name' et 'level' sont obligatoires"}), 400
        payload = {
            "name": data["name"],
            "level": int(data["level"]),
            "tooltip_fr": data.get("tooltip_fr", ""),
            "tooltip_en": data.get("tooltip_en", ""),
            "order_index": int(data.get("order_index", 0)),
        }
        res = get_supabase().table("skills").insert(payload).execute()
        return jsonify(res.data[0] if res.data else payload), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/skills/<int:sid>", methods=["PUT"])
@require_admin
def update_skill(sid):
    try:
        data = request.get_json() or {}
        data.pop("id", None)
        data.pop("created_at", None)
        res = get_supabase().table("skills").update(data).eq("id", sid).execute()
        return jsonify(res.data[0] if res.data else {}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/skills/<int:sid>", methods=["DELETE"])
@require_admin
def delete_skill(sid):
    try:
        get_supabase().table("skills").delete().eq("id", sid).execute()
        return jsonify({"message": f"Competence {sid} supprimee"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    print(f"Serveur Flask sur http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
