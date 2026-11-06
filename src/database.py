import os
import pickle
import base64
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

# NOUVEAU : Sauvegarder l'objet entier en base64
def sauvegarder_parametres_calibration(objet_modele):
    supabase = get_supabase()
    if not supabase: return False
    try:
        # On transforme l'objet Python en texte (pickle) puis en texte lisible (base64)
        objet_serialise = base64.b64encode(pickle.dumps(objet_modele)).decode('utf-8')
        
        data = {"id": 1, "parametres_serialises": objet_serialise}
        supabase.table("calibration_params").upsert(data).execute()
        return True
    except Exception as e:
        print(f"Erreur sauvegarde cerveau : {e}")
        return False

# NOUVEAU : Charger l'objet entier
def charger_parametres_calibration():
    supabase = get_supabase()
    if not supabase: return None
    try:
        reponse = supabase.table("calibration_params").select("*").eq("id", 1).execute()
        if reponse.data and reponse.data[0].get("parametres_serialises"):
            # On décode le texte pour retrouver l'objet Python
            objet_serialise = reponse.data[0]["parametres_serialises"]
            objet_modele = pickle.loads(base64.b64decode(objet_serialise.encode('utf-8')))
            return objet_modele
        return None
    except Exception as e:
        print(f"Erreur chargement cerveau : {e}")
        return None
