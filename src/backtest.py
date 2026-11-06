import requests
import random

def lancer_backtest_saison(calibrateur):
    print("Démarrage du Backtest...")
    
    # On va chercher les matchs sur des jours précis de la saison 2023-2024
    dates = ["20240115", "20240116", "20240117", "20240118", "20240119", "20240120"]
    
    probas_brutes = []
    resultats_reels = []
    matchs_traites = 0

    for date in dates:
        url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={date}"
        try:
            reponse = requests.get(url, timeout=10)
            data = reponse.json()
            matchs = data.get("events", [])
            
            for match in matchs:
                competitions = match.get("competitions", [])
                if not competitions: continue
                
                comp = competitions[0]
                equipes = comp.get("competitors", [])
                if len(equipes) != 2: continue
                
                # On récupère les vrais scores
                score_A = int(equipes[0].get("score", 0))
                score_B = int(equipes[1].get("score", 0))
                total_reel = score_A + score_B
                
                if total_reel == 0: continue
                
                # --- LE CŒUR DU BACKTEST ---
                # On simule une prédiction (entre 40% et 60% de chances)
                fausse_proba = 0.5 + random.uniform(-0.10, 0.10)
                # On fixe une ligne de référence (la moyenne NBA est ~220 points)
                fausse_ligne = 220.0 
                
                # Est-ce que le vrai total a dépassé la ligne ?
                resultat_reel = 1 if total_reel > fausse_ligne else 0
                
                probas_brutes.append(fausse_proba)
                resultats_reels.append(resultat_reel)
                matchs_traites += 1
                
        except Exception as e:
            print(f"Erreur sur la date {date}: {e}")
            continue

    if len(probas_brutes) < 10:
        return {"erreur": f"Pas assez de matchs traités ({len(probas_brutes)})."}

    # Entraînement du calibrateur avec ces données
    calibrateur.entrainer(probas_brutes, resultats_reels)
    
    return {
        "status": "success",
        "message": f"Backtest terminé ! {len(probas_brutes)} matchs analysés et calibrateur entraîné.",
        "calibrateur_pret": calibrateur.est_entraine
                }
