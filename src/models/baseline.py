import numpy as np

def analyser_match_simulation(stats_equipe_A, stats_equipe_B, marche, ligne, avantage_terrain, n_simulations=10000):
    # 1. On cherche la statistique
    if "passe" in marche.lower() or "assist" in marche.lower():
        cle = "passes_par_match"
    elif "rebond" in marche.lower():
        cle = "rebonds_par_match"
    elif "faute" in marche.lower():
        cle = "fautes_par_match"
    else:
        return {"erreur": "Marché inconnu."}

    # 2. On récupère les moyennes de base
    moyenne_A = stats_equipe_A[cle]
    moyenne_B = stats_equipe_B[cle]

    # 3. L'avantage du terrain (On booste l'équipe à la maison, on pénalise un peu le voyageur)
    if avantage_terrain == "domicile_A":
        moyenne_A *= 1.03
        moyenne_B *= 0.98 
    elif avantage_terrain == "domicile_B":
        moyenne_A *= 0.98
        moyenne_B *= 1.03

    # 4. LA FORMULE MAGIQUE (Loi de Poisson)
    # Le robot simule 10 000 matchs pour l'équipe A, et 10 000 pour l'équipe B
    simulations_A = np.random.poisson(lam=moyenne_A, size=n_simulations)
    simulations_B = np.random.poisson(lam=moyenne_B, size=n_simulations)

    # 5. On additionne les deux pour avoir le total du match
    simulations_totales = simulations_A + simulations_B

    # 6. On calcule la moyenne de nos simulations et on compte les Over
    moyenne_totale = np.mean(simulations_totales)
    over_reussis = np.sum(simulations_totales > ligne)
    p_over = over_reussis / n_simulations

    return {
        "total_attendu": round(moyenne_totale, 1),
        "p_over_modele": round(p_over, 4),
        "p_under_modele": round(1 - p_over, 4),
        "ligne": ligne
    }
