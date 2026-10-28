"""
Tâche d'arrière-plan (Background Thread) qui interroge périodiquement Supabase
tant que le serveur Flask tourne, afin de maintenir la base de données active.
"""

import os
import time
import threading
from routes.health import ping_supabase_tables

# Intervalle par défaut : toutes les 6 heures (21600 secondes)
KEEP_ALIVE_INTERVAL_SECONDS = int(os.getenv("KEEP_ALIVE_INTERVAL_SECONDS", "21600"))
_worker_started = False


def _keep_alive_loop() -> None:
    while True:
        try:
            ping_supabase_tables()
            print("[Keep-Alive] Ping Supabase exécuté avec succès.")
        except Exception as exc:
            print(f"[Keep-Alive] Erreur lors du ping Supabase : {exc}")
        time.sleep(KEEP_ALIVE_INTERVAL_SECONDS)


def start_supabase_keep_alive() -> None:
    """Démarre un thread démon en arrière-plan pour pinger Supabase régulièrement."""
    global _worker_started
    if _worker_started:
        return
    _worker_started = True
    thread = threading.Thread(target=_keep_alive_loop, name="SupabaseKeepAlive", daemon=True)
    thread.start()
