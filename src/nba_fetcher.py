from nba_api.stats.endpoints import leaguedashteamstats

def get_stats_equipes(saison="2023-24"):
    # Le bibliothécaire demande à la NBA les stats de base de toutes les équipes
    stats = leaguedashteamstats.LeagueDashTeamStats(
        season=saison,
        per_mode_detailed='PerGame', # On demande les moyennes par match
        measure_type_detailed_defense='Base'
    )
    # On transforme la réponse en liste de dictionnaires (facile à lire)
    data = stats.get_data_frames()[0]
    
    # On garde uniquement ce qui nous intéresse pour l'instant :
    # TEAM_NAME (Nom), AST (Passes), REB (Rebonds), PF (Fautes)
    colonnes_utiles = ['TEAM_NAME', 'AST', 'REB', 'PF']
    resultat = data[colonnes_utiles].to_dict(orient="records")
    
    return resultat
