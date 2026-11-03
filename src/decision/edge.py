import math
from scipy.stats import norm

def calculer_proba_marche(cote_over, cote_under):
    # 1. On enlève la marge du bookmaker (dé-margeage)
    proba_brute_over = 1 / cote_over
    proba_brute_under = 1 / cote_under
    total_proba = proba_brute_over + proba_brute_under
    
    proba_over_marche = proba_brute_over / total_proba
    proba_under_marche = proba_brute_under / total_proba
    
    return proba_over_marche, proba_under_marche

def prendre_decision(total_attendu, ligne, cote_over, cote_under):
    # 2. On calcule la probabilité que le total dépasse la ligne (Loi Normale simplifiée)
    # On estime l'écart-type (l'incertitude) à 5.0 pour l'instant
    ecart_type = 5.0 
    proba_over_modele = 1 - norm.cdf(ligne, loc=total_attendu, scale=ecart_type)
    proba_under_modele = 1 - proba_over_modele
    
    # 3. On calcule les probabilités du bookmaker
    p_over_marche, p_under_marche = calculer_proba_marche(cote_over, cote_under)
    
    # 4. On calcule l'Avantage (Edge) et la Valeur Espérée (EV)
    ev_over = (proba_over_modele * cote_over) - 1
    ev_under = (proba_under_modele * cote_under) - 1
    
    # 5. Le robot décide (Seuil de refus : EV < 3% comme dans le dossier)
    if ev_over > 0.03:
        decision = "PARIER OVER"
        ev_choisie = ev_over
    elif ev_under > 0.03:
        decision = "PARIER UNDER"
        ev_choisie = ev_under
    else:
        decision = "REFUS"
        ev_choisie = max(ev_over, ev_under)

    return {
        "p_over_modele": round(proba_over_modele, 3),
        "p_under_modele": round(proba_under_modele, 3),
        "p_over_marche": round(p_over_marche, 3),
        "ev_over": round(ev_over, 3),
        "ev_under": round(ev_under, 3),
        "decision": decision,
        "ev_choisie": round(ev_choisie, 3)
  }
