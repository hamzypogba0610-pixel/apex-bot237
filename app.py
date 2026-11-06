from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from src.nba_fetcher import get_stats_equipe
from src.models.baseline import analyser_match_simulation
from src.decision.edge import prendre_decision
from src.decision.calibration import CalibrateurAPEX
from src.database import sauvegarder_analyse, lire_historique, mettre_a_jour_resultat, recuperer_donnees_calibration

app = FastAPI(title="APEX-BI")
templates = Jinja2Templates(directory="templates")

calibrateur = CalibrateurAPEX()

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
        
        analyse_monte_carlo = analyser_match_simulation(stats_A, stats_B, demande.marche, demande.ligne, demande.avantage_terrain)
        
        p_over_calibre = calibrateur.calibrer(analyse_monte_carlo["p_over_modele"])
        p_under_calibre = 1.0 - p_over_calibre
        
        decision_financiere = prendre_decision(p_over_calibre, p_under_calibre, demande.cote_over, demande.cote_under)
        
        resultat_final = {
            "match": f"{stats_A['equipe']} vs {stats_B['equipe']}",
            "marche": demande.marche,
            "analyse_sportive": analyse_monte_carlo,
            "probabilites_calibrees": {"p_over": round(p_over_calibre, 4), "p_under": round(p_under_calibre, 4)},
            "decision_financiere": decision_financiere
        }
        sauvegarder_analyse(resultat_final)
        return resultat_final
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# NOUVELLE ROUTE : Noter le résultat (1=Gagné, 0=Perdu)
@app.post("/api/noter-resultat/{id_pari}/{resultat}")
def noter_resultat(id_pari: int, resultat: int):
    succes = mettre_a_jour_resultat(id_pari, resultat)
    if succes:
        return {"status": "ok", "message": "Résultat enregistré !"}
    raise HTTPException(status_code=500, detail="Erreur d'enregistrement.")

# NOUVELLE ROUTE : Entraîner le calibrateur
@app.post("/entrainer-calibration")
def entrainer():
    probas, resultats = recuperer_donnees_calibration()
    
    if len(probas) < 10:
        return {"status": "info", "message": f"Pas assez de données pour l'instant ({len(probas)}/10). Continue à noter tes paris !"}
    
    try:
        calibrateur.entrainer(probas, resultats)
        return {"status": "success", "message": f"Calibrateur entraîné sur {len(probas)} paris passés !"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
