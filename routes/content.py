"""
Routes pour la gestion des textes éditoriaux du site (/api/content/*).
"""

from flask import Blueprint, request, jsonify
from database import get_supabase
from middlewares.auth import require_admin

content_bp = Blueprint("content", __name__)


@content_bp.route("/api/content", methods=["GET"])
def get_content():
    try:
        res = get_supabase().table("content").select("*").execute()
        result = {
            row["key"]: {"value_fr": row["value_fr"], "value_en": row["value_en"]}
            for row in (res.data or [])
        }
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@content_bp.route("/api/content/<string:key>", methods=["PUT"])
@require_admin
def update_content(key: str):
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
