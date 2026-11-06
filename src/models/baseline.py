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

    # 3. L'avantage du terrain
    if avantage_terrain == "domicile_A":
        moyenne_A *= 1.03
        moyenne_B *= 0.98 
    elif avantage_terrain == "domicile_B":
        moyenne_A *= 0.98
        moyenne_B *= 1.03

    # --- COUCHE 1 : LE RYTHME PARTAGÉ (LA CORRÉLATION) ---
    # Le robot tire au sort l'intensité du match (1.0 = normal, 1.1 = match rapide, 0.9 = match lent)
    # Une loi Normale avec 5% de variation
    rythme_match = np.random.normal(loc=1.0, scale=0.05, size=n_simulations)
    
    # On applique ce rythme aux deux équipes (si le match est rapide, les deux en profitent)
    moyennes_A_simulees = moyenne_A * rythme_match
    moyennes_B_simulees = moyenne_B * rythme_match

    # --- COUCHE 2 : LA SURDISPERSION (LOI BINOMIALE NÉGATIVE) ---
    # On utilise la Binomiale Négative au lieu de Poisson.
    # Le paramètre 'r' (taille) contrôle la "folie" du match. Plus r est petit, plus il y a de surprises.
    r = 15  # Ajustable : r=15 donne une distribution réaliste pour la NBA
    
    # Simulation de l'équipe A (formule mathématique de la Binomiale Négative)
    p_A = r / (r + moyennes_A_simulees)
    sim_A = np.random.negative_binomial(r, p_A, size=n_simulations)

    # Simulation de l'équipe B
    p_B = r / (r + moyennes_B_simulees)
    sim_B = np.random.negative_binomial(r, p_B, size=n_simulations)

    # --- COUCHE 3 : LE TOTAL ET LA PROBABILITÉ ---
    simulations_totales = sim_A + sim_B
    moyenne_totale = np.mean(simulations_totales)
    
    over_reussis = np.sum(simulations_totales > ligne)
    p_over = over_reussis / n_simulations

    return {
        "total_attendu": round(moyenne_totale, 1),
        "p_over_modele": round(p_over, 4),
        "p_under_modele": round(1 - p_over, 4),
        "ligne": ligne
    }
