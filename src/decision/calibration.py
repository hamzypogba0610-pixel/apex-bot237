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

    # CORRECTION : On va chercher les paramètres dans 'map_'
    def get_parametres(self):
        if not self.est_entraine:
            return None
        # map_ est une liste [a, b, m]. 
        # Si un paramètre n'a pas été ajusté (car mis à None), on le remplace par 0 pour la sauvegarde.
        a = self.modele.map_[0] if self.modele.map_[0] is not None else 0.0
        b = self.modele.map_[1] if self.modele.map_[1] is not None else 0.0
        m = self.modele.map_[2] if self.modele.map_[2] is not None else 0.0
        return float(a), float(b), float(m)

    # CORRECTION : On restaure en recréant le tiroir 'map_'
    def restaurer(self, param_a, param_b, param_m):
        self.modele.map_ = [param_a, param_b, param_m]
        self.est_entraine = True
        print("Calibrateur restauré depuis la mémoire.")
