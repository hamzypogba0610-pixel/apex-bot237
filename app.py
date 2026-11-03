from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from src.nba_fetcher import get_stats_equipes
from src.models.baseline import analyser_match
from src.decision.edge import prendre_decision

app = FastAPI(title="APEX-BI")

# On prépare l'outil pour lire le HTML
templates = Jinja2Templates(directory="templates")

class MatchDemande(BaseModel):
    equipe_A: str
    equipe_B: str
    marche: str
    ligne: float
    cote_over: float
    cote_under: float

# LA PAGE D'ACCUEIL (Affiche le HTML)
@app.get("/")
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

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
    
    analyse_sportive = analyser_match(stats_A, stats_B, demande.marche, demande.ligne)
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
