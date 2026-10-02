import os
import jwt
import datetime
from functools import wraps
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from supabase import create_client, Client

current_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(current_dir, ".env"))

app = Flask(__name__)

# ── CORS : restreint au domaine Vercel en prod ─────────────────────────────────
ALLOWED_ORIGINS = [
    "https://obilly-portfolio.vercel.app",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CORS(app, resources={r"/api/*": {"origins": ALLOWED_ORIGINS}}, supports_credentials=True)

SUPABASE_URL    = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY    = os.getenv("SUPABASE_KEY", "")
ADMIN_PASSWORD  = os.getenv("ADMIN_PASSWORD", "")
JWT_SECRET      = os.getenv("JWT_SECRET", "changeme")
JWT_EXPIRY_HOURS = int(os.getenv("JWT_EXPIRY_HOURS", "24"))

supabase_client: Client = None

def get_supabase() -> Client:
    global supabase_client
    if supabase_client is None:
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return supabase_client

# ── JWT helpers ────────────────────────────────────────────────────────────────
def generate_token() -> str:
    payload = {
        "sub": "admin",
        "iat": datetime.datetime.now(datetime.timezone.utc),
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=JWT_EXPIRY_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def verify_token(token: str) -> bool:
    try:
        jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return True
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False

def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error": "Token manquant"}), 401
        token = auth.split(" ", 1)[1]
        if not verify_token(token):
            return jsonify({"error": "Token invalide ou expire"}), 401
        return f(*args, **kwargs)
    return decorated

# ── Sante ──────────────────────────────────────────────────────────────────────
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "online", "message": "API Flask operationnelle"}), 200

# ── Auth ────────────────────────────────────────────────────────────────────────
@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    if data.get("password") == ADMIN_PASSWORD:
        token = generate_token()
        return jsonify({"success": True, "token": token, "expires_in": f"{JWT_EXPIRY_HOURS}h"}), 200
    return jsonify({"error": "Mot de passe incorrect"}), 401

@app.route("/api/auth/verify", methods=["GET"])
def verify():
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer ") and verify_token(auth.split(" ", 1)[1]):
        return jsonify({"valid": True}), 200
    return jsonify({"valid": False}), 401

# ── Projets ────────────────────────────────────────────────────────────────────
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
        data.pop("id", None); data.pop("created_at", None)
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

# ── Competences ────────────────────────────────────────────────────────────────
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
        level = int(data["level"])
        if not (0 <= level <= 100):
            return jsonify({"error": "level doit etre entre 0 et 100"}), 400
        payload = {
            "name": data["name"].strip(),
            "level": level,
            "tooltip_fr": data.get("tooltip_fr", "").strip(),
            "tooltip_en": data.get("tooltip_en", "").strip(),
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
        data.pop("id", None); data.pop("created_at", None)
        if "level" in data:
            level = int(data["level"])
            if not (0 <= level <= 100):
                return jsonify({"error": "level doit etre entre 0 et 100"}), 400
            data["level"] = level
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

# ── Contenu textuel ────────────────────────────────────────────────────────────
@app.route("/api/content", methods=["GET"])
def get_content():
    try:
        res = get_supabase().table("content").select("*").execute()
        result = {row["key"]: {"value_fr": row["value_fr"], "value_en": row["value_en"]} for row in res.data}
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/content/<string:key>", methods=["PUT"])
@require_admin
def update_content(key):
    try:
        data = request.get_json() or {}
        payload = {}
        if "value_fr" in data:
            payload["value_fr"] = data["value_fr"].strip()
        if "value_en" in data:
            payload["value_en"] = data["value_en"].strip()
        if not payload:
            return jsonify({"error": "value_fr ou value_en requis"}), 400
        res = get_supabase().table("content").update(payload).eq("key", key).execute()
        return jsonify(res.data[0] if res.data else {}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── Services ───────────────────────────────────────────────────────────────────
@app.route("/api/services", methods=["GET"])
def get_services():
    try:
        res = get_supabase().table("services").select("*").order("order_index").execute()
        return jsonify(res.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/services", methods=["POST"])
@require_admin
def create_service():
    try:
        data = request.get_json() or {}
        text_fr = data.get("text_fr", "").strip()
        text_en = data.get("text_en", "").strip()

        if not text_fr and (data.get("title_fr") or data.get("description_fr")):
            t = data.get("title_fr", "").strip()
            d = data.get("description_fr", "").strip()
            text_fr = f"{t}
---
{d}" if d else t

        if not text_en and (data.get("title_en") or data.get("description_en")):
            t = data.get("title_en", "").strip()
            d = data.get("description_en", "").strip()
            text_en = f"{t}
---
{d}" if d else t

        if not text_fr or not text_en:
            return jsonify({"error": "'text_fr' et 'text_en' sont obligatoires"}), 400

        payload = {
            "text_fr": text_fr,
            "text_en": text_en,
            "order_index": int(data.get("order_index", 0)),
        }
        res = get_supabase().table("services").insert(payload).execute()
        return jsonify(res.data[0] if res.data else payload), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/services/<int:sid>", methods=["PUT"])
@require_admin
def update_service(sid):
    try:
        data = request.get_json() or {}
        data.pop("id", None); data.pop("created_at", None)

        payload = {}
        if "text_fr" in data:
            payload["text_fr"] = data["text_fr"]
        elif "title_fr" in data or "description_fr" in data:
            t = data.get("title_fr", "").strip()
            d = data.get("description_fr", "").strip()
            payload["text_fr"] = f"{t}
---
{d}" if d else t

        if "text_en" in data:
            payload["text_en"] = data["text_en"]
        elif "title_en" in data or "description_en" in data:
            t = data.get("title_en", "").strip()
            d = data.get("description_en", "").strip()
            payload["text_en"] = f"{t}
---
{d}" if d else t

        if "order_index" in data:
            payload["order_index"] = int(data["order_index"])

        res = get_supabase().table("services").update(payload).eq("id", sid).execute()
        return jsonify(res.data[0] if res.data else {}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/services/<int:sid>", methods=["DELETE"])
@require_admin
def delete_service(sid):
    try:
        get_supabase().table("services").delete().eq("id", sid).execute()
        return jsonify({"message": f"Service {sid} supprime"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    print(f"Serveur Flask sur http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
