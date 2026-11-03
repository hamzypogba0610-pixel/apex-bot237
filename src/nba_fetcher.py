import requests

def get_stats_equipes():
    try:
        # 1. On récupère la liste des équipes (avec leur ID secret)
        url_teams = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams"
        response_teams = requests.get(url_teams, timeout=20)
        response_teams.raise_for_status()
        
        equipes_brutes = response_teams.json().get("sports", [{}])[0].get("leagues", [{}])[0].get("teams", [])
        
        resultats = []
        
        # 2. Pour chaque équipe, on va chercher ses stats
        for equipe in equipes_brutes:
            infos = equipe.get("team", {})
            team_id = infos.get("id")
            nom_equipe = infos.get("displayName")
            
            # On demande les stats de la saison en cours (season=2025)
            url_stats = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/{team_id}/statistics?season=2025"
            response_stats = requests.get(url_stats, timeout=10)
            
            # Si on a bien les stats, on les range
            if response_stats.status_code == 200:
                data_stats = response_stats.json()
                # On fouille dans les catégories "general" et "offensive" pour trouver nos chiffres
                stats_list = []
                for categorie in data_stats.get("results", {}).get("stats", {}).get("categories", []):
                    stats_list.extend(categorie.get("stats", []))
                
                # On transforme la liste en dictionnaire facile à lire
                stats_dict = {stat["name"]: stat["value"] for stat in stats_list}
                
                resultats.append({
                    "equipe": nom_equipe,
                    "passes_par_match": round(stats_dict.get("avgAssists", 0), 1),
                    "rebonds_par_match": round(stats_dict.get("avgRebounds", 0), 1),
                    "fautes_par_match": round(stats_dict.get("avgFouls", 0), 1)
                })
            else:
                resultats.append({"equipe": nom_equipe, "erreur": "Stats indisponibles"})
                
        return resultats
    except Exception as e:
        return {"erreur_espn": str(e)}
