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

    # 2. On calcule la moyenne attendue
    moyenne_A = stats_equipe_A[cle]
    moyenne_B = stats_equipe_B[cle]
    moyenne_totale = moyenne_A + moyenne_B

    # 3. On applique l'avantage du terrain
    if avantage_terrain in ["domicile_A", "domicile_B"]:
        moyenne_totale = moyenne_totale * 1.03

    # 4. LA MAGIE MONTE-CARLO : On simule 10 000 matchs
    # On estime que la "variance" (le désordre) est d'environ 10% de la moyenne.
    # C'est comme ça que les pros modélisent l'incertitude d'un match.
    ecart_type = moyenne_totale * 0.10
    
    # Le robot crée 10 000 résultats de matchs possibles (loi normale)
    simulations = np.random.normal(loc=moyenne_totale, scale=ecart_type, size=n_simulations)

    # 5. On compte combien de fois la simulation dépasse la ligne
    over_reussis = np.sum(simulations > ligne)
    p_over = over_reussis / n_simulations
    p_under = 1 - p_over

    return {
        "total_attendu": round(moyenne_totale, 1),
        "p_over_modele": round(p_over, 4),
        "p_under_modele": round(p_under, 4),
        "ligne": ligne
    }
