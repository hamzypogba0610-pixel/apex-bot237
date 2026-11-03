from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.nba_fetcher import get_stats_equipes
from src.models.baseline import analyser_match

app = FastAPI(title="APEX-BI")

class MatchDemande(BaseModel):
    equipe_A: str
    equipe_B: str
    marche: str
    ligne: float

@app.get("/")
def root():
    return {"message": "APEX-BI bot is alive", "version": "0.2.0"}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/stats-equipes")
def stats_equipes():
    return {"equipes": get_stats_equipes()}

@app.post("/analyser")
def analyser(demande: MatchDemande):
    # 1. On va chercher les stats de toutes les équipes
    stats = get_stats_equipes()
    
    # 2. On cherche les deux équipes demandées (recherche simplifiée)
    stats_A = next((e for e in stats if demande.equipe_A.lower() in e["equipe"].lower()), None)
    stats_B = next((e for e in stats if demande.equipe_B.lower() in e["equipe"].lower()), None)

    if not stats_A or not stats_B:
        raise HTTPException(status_code=404, detail="Équipe non trouvée. Vérifie l'orthographe (ex: 'Lakers', 'Celtics').")
    
    # 3. On demande au cerveau de faire le calcul
    resultat = analyser_match(stats_A, stats_B, demande.marche, demande.ligne)
    
    return {
        "match": f"{stats_A['equipe']} vs {stats_B['equipe']}",
        "marche": demande.marche,
        "analyse": resultat
}
