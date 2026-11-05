from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from src.nba_fetcher import get_stats_equipe
from src.models.baseline import analyser_match
from src.decision.edge import prendre_decision
from src.database import sauvegarder_analyse

app = FastAPI(title="APEX-BI")
templates = Jinja2Templates(directory="templates")

class MatchDemande(BaseModel):
    equipe_A: str
    equipe_B: str
    marche: str
    ligne: float
    cote_over: float
    cote_under: float

@app.get("/")
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.post("/analyser")
def analyser(demande: MatchDemande):
    try:
        # On ne cherche que les deux équipes demandées (beaucoup plus rapide !)
        stats_A = get_stats_equipe(demande.equipe_A)
        stats_B = get_stats_equipe(demande.equipe_B)

        if not stats_A or not stats_B or "erreur" in stats_A or "erreur" in stats_B:
            raise HTTPException(status_code=404, detail="Équipe non trouvée ou stats indisponibles.")
        
        analyse_sportive = analyser_match(stats_A, stats_B, demande.marche, demande.ligne)
        decision_financiere = prendre_decision(
            total_attendu=analyse_sportive["total_attendu"],
            ligne=demande.ligne,
            cote_over=demande.cote_over,
            cote_under=demande.cote_under
        )
        
        resultat_final = {
            "match": f"{stats_A['equipe']} vs {stats_B['equipe']}",
            "marche": demande.marche,
            "analyse_sportive": analyse_sportive,
            "decision_financiere": decision_financiere
        }

        sauvegarder_analyse(resultat_final)
        
        return resultat_final
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
