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

    # NOUVEAU : Récupérer les paramètres pour les sauvegarder
    def get_parametres(self):
        if not self.est_entraine:
            return None
        return float(self.modele.a_[0]), float(self.modele.b_[0]), float(self.modele.m_[0])

    # NOUVEAU : Recharger les paramètres appris
    def restaurer(self, param_a, param_b, param_m):
        self.modele.a_ = np.array([param_a])
        self.modele.b_ = np.array([param_b])
        self.modele.m_ = np.array([param_m])
        self.est_entraine = True
        print("Calibrateur restauré depuis la mémoire.")
