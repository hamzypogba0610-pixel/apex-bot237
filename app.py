from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from src.nba_fetcher import get_stats_equipe
from src.models.baseline import analyser_match_simulation
from src.decision.edge import prendre_decision
from src.decision.calibration import CalibrateurAPEX
from src.database import (
    sauvegarder_analyse, lire_historique, mettre_a_jour_resultat,
    recuperer_donnees_calibration, sauvegarder_parametres_calibration, charger_parametres_calibration
)
from src.backtest import lancer_backtest_saison

app = FastAPI(title="APEX-BI")
templates = Jinja2Templates(directory="templates")

calibrateur = CalibrateurAPEX()

@app.on_event("startup")
def startup_event():
    objet_modele = charger_parametres_calibration()
    if objet_modele:
        calibrateur.restaurer_objet(objet_modele)
        print("Cerveau du robot rechargé avec succès depuis Supabase !")
    else:
        print("Aucun cerveau sauvegardé trouvé. Le robot est un nouveau-né.")

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

        # --- NOUVEAU : Calcul des cotes justes ---
        # La cote juste, c'est 1 divisé par la probabilité (ex: 1 / 0.60 = 1.66)
        cote_juste_over = 1 / p_over_calibre if p_over_calibre > 0 else 0
        cote_juste_under = 1 / p_under_calibre if p_under_calibre > 0 else 0

        resultat_final = {
            "match": f"{stats_A['equipe']} vs {stats_B['equipe']}",
            "marche": demande.marche,
            "analyse_sportive": analyse_monte_carlo,
            "probabilites_calibrees": {"p_over": round(p_over_calibre, 4), "p_under": round(p_under_calibre, 4)},
            "cotes_justes": {
                "cote_juste_over": round(cote_juste_over, 2),
                "cote_juste_under": round(cote_juste_under, 2)
            },
            "decision_financiere": decision_financiere
        }
        sauvegarder_analyse(resultat_final)
        return resultat_final
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/noter-resultat/{id_pari}/{resultat}")
def noter_resultat(id_pari: int, resultat: int):
    succes = mettre_a_jour_resultat(id_pari, resultat)
    if succes: return {"status": "ok"}
    raise HTTPException(status_code=500, detail="Erreur.")

@app.post("/entrainer-calibration")
def entrainer():
    probas, resultats = recuperer_donnees_calibration()
    if len(probas) < 10:
        return {"status": "info", "message": f"Pas assez de données ({len(probas)}/10)."}
    try:
        calibrateur.entrainer(probas, resultats)
        objet = calibrateur.get_objet_modele()
        sauvegarder_parametres_calibration(objet)
        return {"status": "success", "message": "Calibrateur entraîné et sauvegardé !"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/lancer-backtest")
def backtest():
    try:
        resultat = lancer_backtest_saison(calibrateur)
        if resultat.get("status") == "success":
            objet = calibrateur.get_objet_modele()
            sauvegarder_parametres_calibration(objet)
            resultat["message"] += " (Cerveau sauvegardé en base de données)"
        return resultat
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Ajoute mettre_a_jour_cloture dans l'import de src.database
from src.database import ..., mettre_a_jour_cloture

# Ajoute cette route à la fin de app.py
@app.post("/api/noter-cloture/{id_pari}")
def noter_cloture(id_pari: int, cote_over: float, cote_under: float):
    succes = mettre_a_jour_cloture(id_pari, cote_over, cote_under)
    if succes: return {"status": "ok"}
    raise HTTPException(status_code=500, detail="Erreur.")
