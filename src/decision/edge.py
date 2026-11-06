def calculer_proba_marche(cote_over, cote_under):
    proba_brute_over = 1 / cote_over
    proba_brute_under = 1 / cote_under
    total_proba = proba_brute_over + proba_brute_under
    return proba_brute_over / total_proba, proba_brute_under / total_proba

def prendre_decision(p_over_modele, p_under_modele, cote_over, cote_under):
    # On calcule les probabilités du bookmaker (dé-margées)
    p_over_marche, p_under_marche = calculer_proba_marche(cote_over, cote_under)
    
    # On calcule l'EV avec les VRAIES probabilités du monstre
    ev_over = (p_over_modele * cote_over) - 1
    ev_under = (p_under_modele * cote_under) - 1
    
    # Le robot décide (Seuil de refus : EV < 3%)
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
        "p_over_modele": p_over_modele,
        "p_under_modele": p_under_modele,
        "p_over_marche": round(p_over_marche, 3),
        "ev_over": round(ev_over, 3),
        "ev_under": round(ev_under, 3),
        "decision": decision,
        "ev_choisie": round(ev_choisie, 3)
    }
