"""CO 16 à CO 18 — Protection des couvertures contre un feu extérieur."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "CO17_couvertures",
    "titre": "Couvertures et feu extérieur",
    "articles": ["ERP:CO 17", "ERP:CO 16", "ERP:CO 18"],
    "fiche": "C.8",
    "legende": "Au-delà de 12 m du bâtiment voisin ou de la limite de parcelle : aucune exigence. En deçà : couverture M 0, ou M 1 à M 3 sur support continu, ou classement T 30 (d ≤ 8 m) / T 15 (8 à 12 m), indice 1 ou 2 selon la catégorie et le sommeil.",
    "ecarts": [
        "Le règlement cite encore l'essai de l'arrêté du 10 septembre 1970 (classes T 30 / T 15). Équivalence européenne courante : BROOF (t3) (arrêté du 14 février 2003).",
        "Éclairages zénithaux et exutoires : M 3 si moins de 25 % de la surface, M 4 si moins de 10 % (CO 18).",
    ],
}

ROUGE = "#C1121F"


def dessiner():
    s = Scene(1600, 1160, echelle=14, origine=(600, 300))
    s.cartouche("Couvertures et feu extérieur", "Protection de la toiture selon la distance au voisin ou à la limite de parcelle", "CO 17")
    s.sol(-8, -4, 56, 32, VERT_GAZON, trait=None)
    # limite de parcelle en x = 0, voisin à gauche
    s.boite(-6, 2, 0, 5, 18, 9, GRIS)
    s.ligne((0, -4, 0), (0, 28, 0), ROUGE, 3, "14 8")
    H = 7
    s.boite(2, 2, 0, 40, 18, H, BEIGE)
    s.fenetres_y(2, 20, 0, 40, H, 9, 2)
    s.fenetres_x(42, 2, 0, 18, H, 4, 2)
    # zones de toiture selon d
    zones = [(2, 8, "#F28B82"), (8, 12, "#FBC27A"), (12, 42, "#CDE7C1")]
    for x0, x1, c in zones:
        s.sol(x0, 2, x1 - x0, 18, c, ep=1.6, z=H)
    s.cote((0, 2, H), (8, 2, H), "8 m", decal=(0, -3, 0), dy_txt=-22)
    s.cote((8, 2, H), (12, 2, H), "12 m", decal=(0, -3, 0), dy_txt=-22, dx_txt=6)
    for x, t, c in ((5, "d ≤ 8 m : T 30", "#9B1C1C"), (10, "8 < d ≤ 12 m : T 15", "#8A4B00"), (28, "d > 12 m : aucune exigence", "#2F6B2A")):
        u, v = s.p(x, 11, H); s.pastille(u, v, t, "#FFFFFF", c, taille=16)
    s.repere((0, 26, 0), "limite de parcelle\nou bâtiment voisin", du=60, dv=110, couleur=ROUGE, taille=17)
    s.legende(40, 790, [("#F28B82", "classe T 30"), ("#FBC27A", "classe T 15"), ("#CDE7C1", "pas d'exigence")], taille=16, titre="Couverture ni M 0 ni M 1-M 3 sur support continu :", largeur=470)
    s.texte(600, 830, "Indice 1 : 1re catégorie, ou 2e à 4e avec locaux à sommeil", 17, TRAIT)
    s.texte(600, 858, "Indice 2 : 2e à 4e catégories sans sommeil", 17, TRAIT)
    s.texte(600, 900, "Couvertures formant plafond (coques, coupoles) : M 2 quelle que soit d", 17, "#4B5563")
    s.bandeau([
        ("Couverture en M 0, ou M 1 à M 3 posée sur support continu M 0 ou en bois (ou équivalent) : admise quelle que soit la distance.", 18, TRAIT),
        ("Autres couvertures : classe T 30 jusqu'à 8 m, T 15 de 8 à 12 m, mesurés depuis le bâtiment voisin ou la limite de parcelle.", 18, TRAIT),
        ("Contiguïté avec un tiers : dispositions d'isolement de CO 7 (§ 2 et 3). Vitrages de toiture : éviter leur chute sur le public (CO 18 § 2).", 18, TRAIT),
    ])
    return s
