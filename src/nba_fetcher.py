import requests

def get_stats_equipes():
    try:
        # On va chercher le grand tableau des classements de la NBA
        url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/standings"
        
        response = requests.get(url, timeout=20)
        response.raise_for_status() 
        
        data = response.json()
        
        equipes = []
        # On fouille dans les données pour trouver les stats de chaque équipe
        for conference in data.get("children", []):
            for entry in conference.get("standings", {}).get("entries", []):
                nom = entry.get("team", {}).get("displayName")
                
                # Les stats sont cachées dans une liste, on les range dans un dictionnaire
                stats_brutes = entry.get("stats", [])
                stats_dict = {stat["name"]: stat["value"] for stat in stats_brutes}
                
                equipes.append({
                    "equipe": nom,
                    "passes_par_match": stats_dict.get("avgAssists", 0),
                    "rebonds_par_match": stats_dict.get("avgRebounds", 0),
                    "fautes_par_match": stats_dict.get("avgFouls", 0)
                })
            
        return equipes
    except Exception as e:
        return {"erreur_espn": str(e)}
