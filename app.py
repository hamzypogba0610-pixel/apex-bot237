from fastapi import FastAPI
from src.nba_fetcher import get_stats_equipes

app = FastAPI(title="APEX-BI")

@app.get("/")
def root():
    return {"message": "APEX-BI bot is alive", "version": "0.1.0"}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/stats-equipes")
def stats_equipes():
    try:
        data = get_stats_equipes()
        return {"equipes": data}
    except Exception as e:
        return {"erreur_bot": str(e)}
