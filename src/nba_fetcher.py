from nba_api.stats.endpoints import leaguedashteamstats

def get_stats_equipes(saison="2023-24"):
    try:
        # On crée une fausse identité de navigateur web
        custom_headers = {
            'Host': 'stats.nba.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Referer': 'https://www.nba.com/'
        }

        # On demande les stats en utilisant cette fausse identité
        stats = leaguedashteamstats.LeagueDashTeamStats(
            season=saison,
            per_mode_detailed='PerGame', 
            measure_type_detailed_defense='Base',
            timeout=30,          # On garde 30s de limite
            headers=custom_headers # On glisse la fausse carte d'identité ici
        )
        data = stats.get_data_frames()[0]
        
        colonnes_utiles = ['TEAM_NAME', 'AST', 'REB', 'PF']
        resultat = data[colonnes_utiles].to_dict(orient="records")
        
        return resultat
    except Exception as e:
        return {"erreur_nba": str(e)}
