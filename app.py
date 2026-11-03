from fastapi import FastAPI
from src.nba_fetcher import get_stats_equipes  # On appelle notre bibliothécaire

app = FastAPI(title="APEX-BI")

@app.get("/")
def root():
    return {"message": "APEX-BI bot is alive", "version": "0.1.0"}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

# Nouvelle route pour voir les stats !
@app.get("/stats-equipes")
def stats_equipes():
    # Le robot demande au bibliothécaire de ramener les stats
    data = get_stats_equipes()
    return {"equipes": data}
