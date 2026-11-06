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

def lire_historique():
    supabase = get_supabase()
    if not supabase:
        return []
    try:
        reponse = supabase.table("historique_paris").select("*").order("date_creation", desc=True).limit(50).execute()
        return reponse.data
    except Exception as e:
        print(f"Erreur de lecture : {e}")
        return []

# NOUVEAU : Mettre à jour le résultat réel (1 = Gagné, 0 = Perdu)
def mettre_a_jour_resultat(id_pari, resultat):
    supabase = get_supabase()
    if not supabase:
        return False
    try:
        supabase.table("historique_paris").update({"resultat_reel": resultat}).eq("id", id_pari).execute()
        return True
    except Exception as e:
        print(f"Erreur de mise à jour : {e}")
        return False

# NOUVEAU : Récupérer les données pour entraîner le calibrateur
def recuperer_donnees_calibration():
    supabase = get_supabase()
    if not supabase:
        return [], []
    try:
        # On ne prend que les paris où on a un résultat (1 ou 0), pas les REFUS
        reponse = supabase.table("historique_paris").select("ev, resultat_reel").not_.is_("resultat_reel", "null").execute()
        
        probas_brutes = []
        resultats = []
        for ligne in reponse.data:
            # Attention : on a besoin des probabilités brutes du modèle, pas de l'EV.
            # Pour faire simple, on va utiliser une approximation basée sur l'EV pour l'instant.
            # (Dans une version future, on stockera directement p_over_modele)
            proba_approx = 0.5 + (ligne["ev"] / 2) # Formule approximative de secours
            probas_brutes.append(min(max(proba_approx, 0.01), 0.99))
            resultats.append(ligne["resultat_reel"])
            
        return probas_brutes, resultats
    except Exception as e:
        print(f"Erreur de récupération : {e}")
        return [], []
