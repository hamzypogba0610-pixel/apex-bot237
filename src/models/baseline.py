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

    # 3. LE NOUVEAU NIVEAU 1 : On applique le bonus/malus de terrain (environ 2%)
    if avantage_terrain == "domicile_A":
        total_A = total_A * 1.02  # +2% pour l'équipe A
        total_B = total_B * 0.98  # -2% pour l'équipe B (fatigue du voyage)
    elif avantage_terrain == "domicile_B":
        total_A = total_A * 0.98
        total_B = total_B * 1.02

    # 4. Le calcul final
    total_attendu = total_A + total_B

    # 5. On compare avec la ligne (Over/Under)
    if total_attendu > ligne:
        prediction = "OVER"
    else:
        prediction = "UNDER"

    return {
        "total_attendu": round(total_attendu, 1),
        "ligne": ligne,
        "prediction_basique": prediction
        }
