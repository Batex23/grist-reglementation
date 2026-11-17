"""CO 2 § 3 — Espace libre."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "CO2_espace-libre",
    "titre": "Espace libre",
    "articles": ["ERP:CO 2", "ERP:CO 5"],
    "fiche": "C.4",
    "legende": "Espace sans obstacle dont la plus petite dimension vaut au moins la largeur totale des sorties qui y débouchent (8 m minimum), issues à moins de 60 m d'une voie engins, accès de 1,80 m ou 3 m.",
    "ecarts": [
        "La page de l'ancienne fiche (C.4) était vierge : planche entièrement redessinée d'après le texte de CO 2 § 3.",
    ],
}

ROUGE = "#C1121F"
DALLAGE = "#E7E1D3"


def dessiner():
    s = Scene(1600, 1160, echelle=17, origine=(700, 250))
    s.cartouche("Espace libre", "Desserte par un espace libre — ERP", "CO 2 § 3")

    s.sol(-12, -8, 58, 50, VERT_GAZON, trait=None)
    s.sol(-12, 36, 58, 6, ENROBE, ep=1.4)                  # voie engins
    s.sol(0, 12, 32, 11, DALLAGE, ep=1.8)                 # espace libre
    for k in range(1, 8):
        s.ligne((0, 12 + k * 11 / 8, 0), (32, 12 + k * 11 / 8, 0), "#D6CEBC", 1)
    s.sol(25, 23, 3, 13, DALLAGE, ep=1.6)                 # accès depuis la voie

    s.boite(0, 0, 0, 32, 12, 7, BEIGE)
    s.fenetres_y(0, 12, 3.5, 32, 3.5, 8, 1, marge_bas=1.0)
    s.fenetres_x(32, 0, 0, 12, 7, 3, 2)
    for xd in (5, 15, 25):                                # sorties
        s.poly([(xd - 1, 12, 0), (xd + 1, 12, 0), (xd + 1, 12, 2.3), (xd - 1, 12, 2.3)], "#3F8F5A", ep=1.6)
        s.icone("homme105" if xd != 15 else "femme206", (xd + 0.8, 15.5, 0), 26)
    s.icone("homme106", (10, 19, 0), 26)
    s.icone("femme205", (20, 17.5, 0), 26)

    for (x, y) in [(-8, 4), (-6, 22), (38, 6), (38, 20), (12, 30)]:
        s.icone("arbre_01", (x, y, 0), 56)
    s.icone("SP_fpt_02", (38, 38.6, 0), 140, ancre=(0.5, 0.80))

    # cotes
    s.cote((0, 12, 0), (0, 23, 0), "≥ 8 m\net ≥ largeur totale\ndes sorties", decal=(-3, 0, 0), dx_txt=-110, dy_txt=-10)
    s.cote((25, 30, 0), (28, 30, 0), "accès ≥ 1,80 m (≤ 8 m)\n≥ 3 m (> 8 m)", rappel=False, dx_txt=190, dy_txt=-20)
    s.chemin([(15, 12.4, 0), (15, 21, 0), (26.5, 21, 0), (26.5, 35.5, 0)], "#15803D", 4.5, "12 6")
    u, v = s.p(26.5, 27, 0); s.etiquette(u - 140, v + 40, "issue à moins de 60 m\nd'une voie engins", "#15803D", 18)
    s.etiquette(*s.p(8, 39, 0), "voie engins", "#374151", 17, gras=False)
    u, v = s.p(6, 23, 0); s.etiquette(u - 70, v + 52, "espace libre\nsans obstacle à l'écoulement du public", "#8A6200", 18)

    s.bandeau([
        ("Plus petite dimension au moins égale à la largeur totale des sorties de l'établissement sur cet espace, sans être inférieure à 8 m.", 19, TRAIT),
        ("Aucun obstacle à l'écoulement du public ; accès et mise en œuvre faciles du matériel de sauvetage et de lutte contre le feu.", 19, TRAIT),
        ("Issues à moins de 60 m d'une voie engins ; accès depuis cette voie de 1,80 m (dernier niveau ≤ 8 m) ou 3 m (> 8 m).", 19, TRAIT),
        ("Au-delà de 8 m, en distribution par secteurs, l'espace libre doit permettre la mise en station d'une échelle aérienne (CO 5).", 17, "#4B5563"),
    ])
    return s
