def analyser_match(stats_equipe_A, stats_equipe_B, marche, ligne, avantage_terrain):
    # 1. On cherche la bonne statistique selon le marché
    if "passe" in marche.lower() or "assist" in marche.lower():
        cle = "passes_par_match"
    elif "rebond" in marche.lower():
        cle = "rebonds_par_match"
    elif "faute" in marche.lower():
        cle = "fautes_par_match"
    else:
        return {"erreur": "Marché inconnu."}

    # 2. On récupère les stats de base
    total_A = stats_equipe_A[cle]
    total_B = stats_equipe_B[cle]
    total_attendu = total_A + total_B

    # 3. LE NOUVEAU NIVEAU 1 : On applique un boost de rythme (environ 3%) 
    # si l'une des deux équipes joue à la maison
    if avantage_terrain in ["domicile_A", "domicile_B"]:
        total_attendu = total_attendu * 1.03 
        # (On augmente le total de 3% pour représenter l'énergie de la salle)

    # 4. On compare avec la ligne (Over/Under)
    if total_attendu > ligne:
        prediction = "OVER"
    else:
        prediction = "UNDER"

    return {
        "total_attendu": round(total_attendu, 1),
        "ligne": ligne,
        "prediction_basique": prediction
    }
