"""
Routes CRUD pour la gestion des projets (/api/projects/*).
"""

from flask import Blueprint, request, jsonify
from database import get_supabase
from middlewares.auth import require_admin

projects_bp = Blueprint("projects", __name__)


@projects_bp.route("/api/projects", methods=["GET"])
def get_projects():
    try:
        res = get_supabase().table("projects").select("*").order("order_index").execute()
        return jsonify(res.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@projects_bp.route("/api/projects", methods=["POST"])
@require_admin
def create_project():
    try:
        data = request.get_json() or {}
        for field in ["name_fr", "name_en", "description_fr", "description_en"]:
            if not data.get(field):
                return jsonify({"error": f"'{field}' est obligatoire"}), 400

        name_fr = data["name_fr"].strip()
        name_en = data["name_en"].strip()

        # Prévention des doublons
        existing = get_supabase().table("projects").select("id, name_fr, name_en").execute()
        for item in (existing.data or []):
            item_fr = (item.get("name_fr") or "").strip().lower()
            item_en = (item.get("name_en") or "").strip().lower()
            if (name_fr and item_fr == name_fr.lower()) or (name_en and item_en == name_en.lower()):
                return jsonify({"error": f"Un projet avec ce nom existe deja (id={item['id']})"}), 409

        payload = {
            "name_fr": name_fr,
            "name_en": name_en,
            "description_fr": data["description_fr"],
            "description_en": data["description_en"],
            "stack": data.get("stack", []),
            "link": data.get("link", "#"),
            "order_index": int(data.get("order_index", 0)),
        }
        res = get_supabase().table("projects").insert(payload).execute()
        return jsonify(res.data[0] if res.data else payload), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@projects_bp.route("/api/projects/<int:pid>", methods=["PUT"])
@require_admin
def update_project(pid: int):
    try:
        data = request.get_json() or {}
        data.pop("id", None)
        data.pop("created_at", None)
        res = get_supabase().table("projects").update(data).eq("id", pid).execute()
        return jsonify(res.data[0] if res.data else {}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@projects_bp.route("/api/projects/<int:pid>", methods=["DELETE"])
@require_admin
def delete_project(pid: int):
    try:
        get_supabase().table("projects").delete().eq("id", pid).execute()
        return jsonify({"message": f"Projet {pid} supprime"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
