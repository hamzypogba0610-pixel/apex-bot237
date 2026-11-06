from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# Importation de nos modules
from src.nba_fetcher import get_stats_equipe
from src.models.baseline import analyser_match_simulation
from src.decision.edge import prendre_decision
from src.decision.calibration import CalibrateurAPEX  # NOUVEAU
from src.database import sauvegarder_analyse, lire_historique

app = FastAPI(title="APEX-BI")
templates = Jinja2Templates(directory="templates")

# Initialisation globale du calibrateur (il est prêt à l'emploi !)
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
        # 1. On récupère les statistiques via l'API ESPN
        stats_A = get_stats_equipe(demande.equipe_A)
        stats_B = get_stats_equipe(demande.equipe_B)

        if not stats_A or not stats_B or "erreur" in stats_A or "erreur" in stats_B:
            raise HTTPException(status_code=404, detail="Équipe non trouvée ou stats indisponibles.")
        
        # 2. Le monstre mathématique (Monte-Carlo + Rythme partagé) fait ses calculs
        analyse_monte_carlo = analyser_match_simulation(
            stats_A, stats_B, demande.marche, demande.ligne, demande.avantage_terrain
        )
        
        # 3. La couche de Calibration (Beta Calibration)
        p_over_brut = analyse_monte_carlo["p_over_modele"]
        p_under_brut = analyse_monte_carlo["p_under_modele"]
        
        # On passe les probabilités brutes au calibrateur
        p_over_calibre = calibrateur.calibrer(p_over_brut)
        p_under_calibre = 1.0 - p_over_calibre # On garde une cohérence parfaite (100%)
        
        # 4. Le banquier (Moteur de décision) calcule l'EV avec les probabilités calibrées
        decision_financiere = prendre_decision(
            p_over_modele=p_over_calibre,
            p_under_modele=p_under_calibre,
            cote_over=demande.cote_over,
            cote_under=demande.cote_under
        )
        
        # 5. On prépare le résultat final
        resultat_final = {
            "match": f"{stats_A['equipe']} vs {stats_B['equipe']}",
            "marche": demande.marche,
            "analyse_sportive": analyse_monte_carlo, # Garde les infos brutes
            "probabilites_calibrees": {
                "p_over": round(p_over_calibre, 4),
                "p_under": round(p_under_calibre, 4)
            },
            "decision_financiere": decision_financiere
        }

        # 6. On sauvegarde dans Supabase
        sauvegarder_analyse(resultat_final)
        
        return resultat_final
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
