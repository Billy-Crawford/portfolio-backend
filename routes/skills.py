"""
Routes CRUD pour la gestion des compétences (/api/skills/*).
"""

from flask import Blueprint, request, jsonify
from database import get_supabase
from middlewares.auth import require_admin

skills_bp = Blueprint("skills", __name__)


@skills_bp.route("/api/skills", methods=["GET"])
def get_skills():
    try:
        res = get_supabase().table("skills").select("*").order("order_index").execute()
        return jsonify(res.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@skills_bp.route("/api/skills", methods=["POST"])
@require_admin
def create_skill():
    try:
        data = request.get_json() or {}
        if not data.get("name") or data.get("level") is None:
            return jsonify({"error": "'name' et 'level' sont obligatoires"}), 400

        name = data["name"].strip()

        # Prévention des doublons
        existing = get_supabase().table("skills").select("id, name").execute()
        for item in (existing.data or []):
            item_name = (item.get("name") or "").strip().lower()
            if item_name == name.lower():
                return jsonify({"error": f"Une competence avec ce nom existe deja (id={item['id']})"}), 409

        level = int(data["level"])
        if not (0 <= level <= 100):
            return jsonify({"error": "level doit etre entre 0 et 100"}), 400

        payload = {
            "name": name,
            "level": level,
            "tooltip_fr": data.get("tooltip_fr", "").strip(),
            "tooltip_en": data.get("tooltip_en", "").strip(),
            "order_index": int(data.get("order_index", 0)),
        }
        res = get_supabase().table("skills").insert(payload).execute()
        return jsonify(res.data[0] if res.data else payload), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@skills_bp.route("/api/skills/<int:sid>", methods=["PUT"])
@require_admin
def update_skill(sid: int):
    try:
        data = request.get_json() or {}
        data.pop("id", None)
        data.pop("created_at", None)
        if "level" in data:
            level = int(data["level"])
            if not (0 <= level <= 100):
                return jsonify({"error": "level doit etre entre 0 et 100"}), 400
            data["level"] = level
        res = get_supabase().table("skills").update(data).eq("id", sid).execute()
        return jsonify(res.data[0] if res.data else {}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@skills_bp.route("/api/skills/<int:sid>", methods=["DELETE"])
@require_admin
def delete_skill(sid: int):
    try:
        get_supabase().table("skills").delete().eq("id", sid).execute()
        return jsonify({"message": f"Competence {sid} supprimee"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
