"""
Routes CRUD pour la gestion du catalogue de services (/api/services/*).
"""

from flask import Blueprint, request, jsonify
from database import get_supabase
from middlewares.auth import require_admin

services_bp = Blueprint("services", __name__)

# Délimiteur utilisé pour stocker Titre + Description dans text_fr / text_en
SERVICE_DELIMITER = "\n---\n"


@services_bp.route("/api/services", methods=["GET"])
def get_services():
    try:
        res = get_supabase().table("services").select("*").order("order_index").execute()
        return jsonify(res.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@services_bp.route("/api/services", methods=["POST"])
@require_admin
def create_service():
    try:
        data = request.get_json() or {}
        text_fr = data.get("text_fr", "").strip()
        text_en = data.get("text_en", "").strip()

        if not text_fr and (data.get("title_fr") or data.get("description_fr")):
            t = data.get("title_fr", "").strip()
            d = data.get("description_fr", "").strip()
            text_fr = f"{t}{SERVICE_DELIMITER}{d}" if d else t

        if not text_en and (data.get("title_en") or data.get("description_en")):
            t = data.get("title_en", "").strip()
            d = data.get("description_en", "").strip()
            text_en = f"{t}{SERVICE_DELIMITER}{d}" if d else t

        if not text_fr or not text_en:
            return jsonify({"error": "'text_fr' et 'text_en' sont obligatoires"}), 400

        # Prévention des doublons sur le titre
        title_only = text_fr.split(SERVICE_DELIMITER)[0].strip().lower()
        existing = get_supabase().table("services").select("id, text_fr").execute()
        for item in (existing.data or []):
            item_title = (item.get("text_fr") or "").split(SERVICE_DELIMITER)[0].strip().lower()
            if item_title == title_only:
                return jsonify({"error": f"Un service avec ce titre existe deja (id={item['id']})"}), 409

        payload = {
            "text_fr": text_fr,
            "text_en": text_en,
            "order_index": int(data.get("order_index", 0)),
        }
        res = get_supabase().table("services").insert(payload).execute()
        return jsonify(res.data[0] if res.data else payload), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@services_bp.route("/api/services/<int:sid>", methods=["PUT"])
@require_admin
def update_service(sid: int):
    try:
        data = request.get_json() or {}
        data.pop("id", None)
        data.pop("created_at", None)

        payload = {}
        if "text_fr" in data:
            payload["text_fr"] = data["text_fr"]
        elif "title_fr" in data or "description_fr" in data:
            t = data.get("title_fr", "").strip()
            d = data.get("description_fr", "").strip()
            payload["text_fr"] = f"{t}{SERVICE_DELIMITER}{d}" if d else t

        if "text_en" in data:
            payload["text_en"] = data["text_en"]
        elif "title_en" in data or "description_en" in data:
            t = data.get("title_en", "").strip()
            d = data.get("description_en", "").strip()
            payload["text_en"] = f"{t}{SERVICE_DELIMITER}{d}" if d else t

        if "order_index" in data:
            payload["order_index"] = int(data["order_index"])

        res = get_supabase().table("services").update(payload).eq("id", sid).execute()
        return jsonify(res.data[0] if res.data else {}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@services_bp.route("/api/services/<int:sid>", methods=["DELETE"])
@require_admin
def delete_service(sid: int):
    try:
        get_supabase().table("services").delete().eq("id", sid).execute()
        return jsonify({"message": f"Service {sid} supprime"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
