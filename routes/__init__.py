"""
Enregistrement centralisé de tous les Blueprints (routes de l'API).
"""

from flask import Flask
from routes.health import health_bp
from routes.auth import auth_bp
from routes.projects import projects_bp
from routes.skills import skills_bp
from routes.content import content_bp
from routes.services import services_bp


def register_routes(app: Flask) -> None:
    """Attache toutes les routes modulaires à l'application Flask."""
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(skills_bp)
    app.register_blueprint(content_bp)
    app.register_blueprint(services_bp)
