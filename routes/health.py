"""
Routes de vérification de l'état du serveur et maintien en éveil de Supabase (Keep-Alive).
Chaque appel à /api/health ou /api/keep-alive interroge réellement Supabase
afin d'empêcher la mise en pause automatique du projet Supabase après 7 jours d'inactivité.
"""

import datetime
from flask import Blueprint, jsonify
from database import get_supabase

health_bp = Blueprint("health", __name__)


def ping_supabase_tables() -> dict:
    """Exécute des requêtes légères sur les tables Supabase pour simuler une activité réelle."""
    client = get_supabase()
    tables_status = {}
    for table in ("projects", "skills", "services"):
        res = client.table(table).select("id").limit(1).execute()
        tables_status[table] = len(res.data or [])
    res_content = client.table("content").select("key").limit(1).execute()
    tables_status["content"] = len(res_content.data or [])
    return tables_status


@health_bp.route("/api/health", methods=["GET"])
@health_bp.route("/api/keep-alive", methods=["GET"])
def health():
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        tables_checked = ping_supabase_tables()
        return jsonify({
            "status": "online",
            "database": "connected",
            "supabase_active": True,
            "tables_checked": tables_checked,
            "timestamp": now,
            "message": "API Flask operationnelle et Supabase maintenu eveille",
        }), 200
    except Exception as e:
        return jsonify({
            "status": "degraded",
            "database": "error",
            "supabase_active": False,
            "error": str(e),
            "timestamp": now,
            "message": "API Flask operationnelle mais erreur lors du ping Supabase",
        }), 200
