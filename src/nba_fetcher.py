from nba_api.stats.endpoints import leaguedashteamstats

def get_stats_equipes(saison="2023-24"):
    try:
        # Le bibliothécaire demande les stats avec une limite de temps (timeout)
        stats = leaguedashteamstats.LeagueDashTeamStats(
            season=saison,
            per_mode_detailed='PerGame', 
            measure_type_detailed_defense='Base',
            timeout=30  # On donne 30 secondes au serveur NBA pour répondre
        )
        data = stats.get_data_frames()[0]
        
        colonnes_utiles = ['TEAM_NAME', 'AST', 'REB', 'PF']
        resultat = data[colonnes_utiles].to_dict(orient="records")
        
        return resultat
    except Exception as e:
        # Si ça plante, on renvoie le vrai message d'erreur
        return {"erreur_nba": str(e)}
