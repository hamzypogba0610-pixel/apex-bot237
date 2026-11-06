from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from src.nba_fetcher import get_stats_equipe
from src.models.baseline import analyser_match_simulation # NOUVEAU NOM
from src.decision.edge import prendre_decision
from src.database import sauvegarder_analyse, lire_historique

app = FastAPI(title="APEX-BI")
templates = Jinja2Templates(directory="templates")

class MatchDemande(BaseModel):
    equipe_A: str
    equipe_B: str
    marche: str
    ligne: float
    cote_over: float
    cote_under: float
    avantage_terrain: str

@app.get("/")
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/historique")
def page_historique(request: Request):
    paris = lire_historique()
    return templates.TemplateResponse("historique.html", {"request": request, "paris": paris})

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.post("/analyser")
def analyser(demande: MatchDemande):
    try:
        stats_A = get_stats_equipe(demande.equipe_A)
        stats_B = get_stats_equipe(demande.equipe_B)

        if not stats_A or not stats_B or "erreur" in stats_A or "erreur" in stats_B:
            raise HTTPException(status_code=404, detail="Équipe non trouvée.")
        
        # 1. Le monstre simule 10 000 matchs
        analyse_monte_carlo = analyser_match_simulation(
            stats_A, stats_B, demande.marche, demande.ligne, demande.avantage_terrain
        )
        
        # 2. Le banquier prend la décision avec les vraies probabilités
        decision_financiere = prendre_decision(
            p_over_modele=analyse_monte_carlo["p_over_modele"],
            p_under_modele=analyse_monte_carlo["p_under_modele"],
            cote_over=demande.cote_over,
            cote_under=demande.cote_under
        )
        
        resultat_final = {
            "match": f"{stats_A['equipe']} vs {stats_B['equipe']}",
            "marche": demande.marche,
            "analyse_sportive": analyse_monte_carlo, # On renvoie les résultats de la simulation
            "decision_financiere": decision_financiere
        }

        sauvegarder_analyse(resultat_final)
        return resultat_final
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
