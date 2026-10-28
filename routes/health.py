"""
Route de vérification de l'état du serveur (Healthcheck).
"""

from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)


@health_bp.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "online", "message": "API Flask operationnelle"}), 200
