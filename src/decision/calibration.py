import numpy as np
from betacal import BetaCalibration

class CalibrateurAPEX:
    """
    Couche de calibration Beta pour APEX-BI.
    Ajuste les probabilités brutes du modèle pour les rendre fiables.
    """
    def __init__(self):
        # Initialise le modèle de calibration Beta
        self.modele = BetaCalibration(parameters="abm")
        self.est_entraine = False

    def entrainer(self, probabilites_brutes, resultats_reels):
        """
        Entraîne le calibrateur sur des données historiques.
        
        :param probabilites_brutes: liste/array des probabilités prédites par le modèle (ex: [0.65, 0.42, ...])
        :param resultats_reels: liste/array des résultats binaires (1 si Over gagné, 0 sinon)
        """
        # On s'assure que les données sont bien des tableaux numpy
        p = np.array(probabilites_brutes)
        y = np.array(resultats_reels)
        
        # Ajustement du modèle Beta
        self.modele.fit(p, y)
        self.est_entraine = True
        print(f"Calibrateur entraîné sur {len(p)} échantillons.")

    def calibrer(self, probabilite_brute):
        """
        Prend une probabilité brute et renvoie la probabilité calibrée.
        Si le calibrateur n'est pas entraîné, renvoie la probabilité brute inchangée.
        """
        if not self.est_entraine:
            return probabilite_brute
        
        # BetaCalibration attend un tableau 2D
        p_array = np.array([[probabilite_brute]])
        p_calibree = self.modele.predict(p_array)[0]
        
        # On s'assure que la probabilité reste dans [0, 1]
        return float(np.clip(p_calibree, 0.0, 1.0))
