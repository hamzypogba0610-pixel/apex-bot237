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
    if not supabase: return False
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

def lire_historique():
    supabase = get_supabase()
    if not supabase: return []
    try:
        reponse = supabase.table("historique_paris").select("*").order("date_creation", desc=True).limit(50).execute()
        return reponse.data
    except Exception as e:
        print(f"Erreur de lecture : {e}")
        return []

def mettre_a_jour_resultat(id_pari, resultat):
    supabase = get_supabase()
    if not supabase: return False
    try:
        supabase.table("historique_paris").update({"resultat_reel": resultat}).eq("id", id_pari).execute()
        return True
    except Exception as e:
        print(f"Erreur de mise à jour : {e}")
        return False

def recuperer_donnees_calibration():
    supabase = get_supabase()
    if not supabase: return [], []
    try:
        reponse = supabase.table("historique_paris").select("ev, resultat_reel").not_.is_("resultat_reel", "null").execute()
        probas_brutes = []
        resultats = []
        for ligne in reponse.data:
            proba_approx = 0.5 + (ligne["ev"] / 2)
            probas_brutes.append(min(max(proba_approx, 0.01), 0.99))
            resultats.append(ligne["resultat_reel"])
        return probas_brutes, resultats
    except Exception as e:
        print(f"Erreur de récupération : {e}")
        return [], []

# NOUVEAU : Sauvegarder les paramètres du cerveau
def sauvegarder_parametres_calibration(param_a, param_b, param_m):
    supabase = get_supabase()
    if not supabase: return False
    try:
        data = {"id": 1, "param_a": float(param_a), "param_b": float(param_b), "param_m": float(param_m)}
        # Upsert (met à jour si existe, crée sinon)
        supabase.table("calibration_params").upsert(data).execute()
        return True
    except Exception as e:
        print(f"Erreur sauvegarde cerveau : {e}")
        return False

# NOUVEAU : Charger les paramètres du cerveau
def charger_parametres_calibration():
    supabase = get_supabase()
    if not supabase: return None
    try:
        reponse = supabase.table("calibration_params").select("*").eq("id", 1).execute()
        if reponse.data:
            return reponse.data[0]
        return None
    except Exception as e:
        print(f"Erreur chargement cerveau : {e}")
        return None
