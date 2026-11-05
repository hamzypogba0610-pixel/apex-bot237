import requests

def get_stats_equipe(nom_recherche):
    try:
        # 1. On trouve l'ID de l'équipe
        url_teams = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams"
        response = requests.get(url_teams, timeout=10)
        equipes = response.json().get("sports", [{}])[0].get("leagues", [{}])[0].get("teams", [])
        
        team_id = None
        nom_complet = None
        for eq in equipes:
            infos = eq.get("team", {})
            if nom_recherche.lower() in infos.get("displayName", "").lower():
                team_id = infos.get("id")
                nom_complet = infos.get("displayName")
                break
                
        if not team_id:
            return None
            
        # 2. On ne récupère les stats QUE pour cette équipe
        url_stats = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/{team_id}/statistics?season=2025"
        res_stats = requests.get(url_stats, timeout=10)
        
        if res_stats.status_code == 200:
            data = res_stats.json()
            stats_list = []
            for cat in data.get("results", {}).get("stats", {}).get("categories", []):
                stats_list.extend(cat.get("stats", []))
            
            stats_dict = {s["name"]: s["value"] for s in stats_list}
            return {
                "equipe": nom_complet,
                "passes_par_match": round(stats_dict.get("avgAssists", 0), 1),
                "rebonds_par_match": round(stats_dict.get("avgRebounds", 0), 1),
                "fautes_par_match": round(stats_dict.get("avgFouls", 0), 1)
            }
        return None
    except Exception as e:
        return {"erreur": str(e)}
