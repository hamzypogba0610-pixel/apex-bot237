def analyser_match(stats_equipe_A, stats_equipe_B, marche, ligne):
    # 1. On cherche la bonne statistique selon le marché
    if "passe" in marche.lower() or "assist" in marche.lower():
        cle = "passes_par_match"
    elif "rebond" in marche.lower():
        cle = "rebonds_par_match"
    elif "faute" in marche.lower():
        cle = "fautes_par_match"
    else:
        return {"erreur": "Marché inconnu. Utilise 'passes', 'rebonds' ou 'fautes'."}

    # 2. Le calcul basique : Stats A + Stats B
    total_attendu = stats_equipe_A[cle] + stats_equipe_B[cle]

    # 3. On compare avec la ligne (Over/Under)
    if total_attendu > ligne:
        prediction = "OVER"
    else:
        prediction = "UNDER"

    return {
        "total_attendu": round(total_attendu, 1),
        "ligne": ligne,
        "prediction_basique": prediction
    }
