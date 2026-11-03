from fastapi import FastAPI
from pydantic import BaseModel
from src.nba_fetcher import get_stats_equipes

app = FastAPI(title="APEX-BI")

# 1. On prépare la forme de la lettre (ce que tu vas nous envoyer)
class CoteSaisie(BaseModel):
    nom_match: str
    marche: str
    ligne: float
    cote_over: float
    cote_under: float

# Une petite mémoire temporaire pour stocker tes cotes
memoire_cotes = []

@app.get("/")
def root():
    return {"message": "APEX-BI bot is alive", "version": "0.1.0"}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/stats-equipes")
def stats_equipes():
    data = get_stats_equipes()
    return {"equipes": data}

# 2. LA BOÎTE AUX LETTRES (La fameuse route POST)
@app.post("/ajouter-cote")
def ajouter_cote(cote: CoteSaisie):
    # On range la lettre dans la mémoire
    nouvelle_cote = cote.model_dump() # On transforme la lettre en dictionnaire
    memoire_cotes.append(nouvelle_cote)
    return {
        "message": "Cote bien reçue !", 
        "cote_enregistree": nouvelle_cote,
        "total_cotes_en_memoire": len(memoire_cotes)
    }

# 3. Pour vérifier que tes lettres sont bien arrivées
@app.get("/voir-cotes")
def voir_cotes():
    return {"toutes_les_cotes": memoire_cotes}
