from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.nba_fetcher import get_stats_equipes
from src.models.baseline import analyser_match
from src.decision.edge import prendre_decision

app = FastAPI(title="APEX-BI")

class MatchDemande(BaseModel):
    equipe_A: str
    equipe_B: str
    marche: str
    ligne: float
    cote_over: float
    cote_under: float

@app.get("/")
def root():
    return {"message": "APEX-BI bot is alive", "version": "0.3.0"}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/stats-equipes")
def stats_equipes():
    return {"equipes": get_stats_equipes()}

@app.post("/analyser")
def analyser(demande: MatchDemande):
    stats = get_stats_equipes()
    
    stats_A = next((e for e in stats if demande.equipe_A.lower() in e["equipe"].lower()), None)
    stats_B = next((e for e in stats if demande.equipe_B.lower() in e["equipe"].lower()), None)

    if not stats_A or not stats_B:
        raise HTTPException(status_code=404, detail="Équipe non trouvée.")
    
    # 1. Le calcul basique
    analyse_sportive = analyser_match(stats_A, stats_B, demande.marche, demande.ligne)
    
    # 2. Le calcul financier (le banquier)
    decision_financiere = prendre_decision(
        total_attendu=analyse_sportive["total_attendu"],
        ligne=demande.ligne,
        cote_over=demande.cote_over,
        cote_under=demande.cote_under
    )
    
    return {
        "match": f"{stats_A['equipe']} vs {stats_B['equipe']}",
        "marche": demande.marche,
        "analyse_sportive": analyse_sportive,
        "decision_financiere": decision_financiere
    }
