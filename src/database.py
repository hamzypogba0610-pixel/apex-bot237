import os
from supabase import create_client, Client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

def get_supabase() -> Client:
    if url and key:
        return create_client(url, key)
    return None

def sauvegarder_analyse(data_analyse):
    supabase = get_supabase()
    if not supabase:
        return False
    try:
        nouvelle_ligne = {
            "match": data_analyse["match"],
            "marche": data_analyse["marche"],
            "total_attendu": data_analyse["analyse_sportive"]["total_attendu"],
            "ligne": data_analyse["analyse_sportive"]["ligne"],
            "decision": data_analyse["decision_financiere"]["decision"],
            "ev": data_analyse["decision_financiere"]["ev_choisie"]
        }
        supabase.table("historique_paris").insert(nouvelle_ligne).execute()
        return True
    except Exception as e:
        print(f"Erreur d'écriture : {e}")
        return False

# NOUVEAU : Fonction pour lire l'historique
def lire_historique():
    supabase = get_supabase()
    if not supabase:
        return []
    try:
        # On demande les 50 derniers paris, du plus récent au plus ancien
        reponse = supabase.table("historique_paris").select("*").order("date_creation", desc=True).limit(50).execute()
        return reponse.data
    except Exception as e:
        print(f"Erreur de lecture : {e}")
        return []
