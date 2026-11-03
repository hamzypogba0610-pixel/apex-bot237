import requests

def get_stats_equipes():
    try:
        # On va directement à la source ESPN, qui est plus fiable pour les serveurs
        url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams"
        
        # On fait la demande
        response = requests.get(url, timeout=20)
        response.raise_for_status() # Vérifie que tout va bien
        
        data = response.json()
        
        # On prépare notre liste de résultats
        equipes = []
        for equipe in data.get("sports", [{}])[0].get("leagues", [{}])[0].get("teams", []):
            infos = equipe.get("team", {})
            equipes.append({
                "nom": infos.get("displayName"),
                "abreviation": infos.get("abbreviation"),
                "ville": infos.get("location")
            })
            
        return equipes
    except Exception as e:
        return {"erreur_espn": str(e)}
