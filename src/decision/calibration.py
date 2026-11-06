import numpy as np
from betacal import BetaCalibration

class CalibrateurAPEX:
    def __init__(self):
        self.modele = BetaCalibration(parameters="abm")
        self.est_entraine = False

    def entrainer(self, probabilites_brutes, resultats_reels):
        p = np.array(probabilites_brutes)
        y = np.array(resultats_reels)
        self.modele.fit(p, y)
        self.est_entraine = True
        print(f"Calibrateur entraîné sur {len(p)} échantillons.")

    def calibrer(self, probabilite_brute):
        if not self.est_entraine:
            return probabilite_brute
        p_array = np.array([[probabilite_brute]])
        p_calibree = self.modele.predict(p_array)[0]
        return float(np.clip(p_calibree, 0.0, 1.0))

    # NOUVEAU : On ne cherche plus les attributs, on renvoie l'objet lui-même
    def get_objet_modele(self):
        if not self.est_entraine:
            return None
        return self.modele

    # NOUVEAU : On restaure l'objet complet
    def restaurer_objet(self, objet_modele):
        self.modele = objet_modele
        self.est_entraine = True
        print("Calibrateur restauré depuis la mémoire (objet complet).")
