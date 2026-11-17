"""CO 1 § 3 — Desserte des bâtiments selon la hauteur du plancher bas du dernier niveau accessible au public."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "CO1_desserte",
    "titre": "Desserte des bâtiments",
    "articles": ["ERP:CO 1", "ERP:CO 3"],
    "fiche": "C.1",
    "legende": "Plancher bas du dernier niveau accessible au public à 8 m au plus : voie engins ou espace libre. Au-delà de 8 m : voie échelles (ou espaces libres en distribution par secteurs, CO 5).",
    "ecarts": [
        "La règle se lit sur le plancher bas du dernier niveau accessible au public, et non sur la hauteur du bâtiment ou du dernier plancher.",
    ],
}


def dessiner():
    s = Scene(1600, 1160, echelle=14.5, origine=(640, 250))
    s.cartouche("Desserte des bâtiments", "Choix de la desserte selon la hauteur du dernier niveau accessible au public — ERP", "CO 1 § 3")
    jaune = s.motif("hj", "#E0A800")

    s.sol(-12, -8, 72, 40, VERT_GAZON, trait=None)
    s.sol(-12, 25, 72, 7, ENROBE, ep=1.4)
    for x in range(-10, 58, 6):
        s.sol(x, 28.3, 3, 0.4, "#FFFFFF", trait=None)
    s.sol(-6, 14, 60, 3.2, ENROBE_CLAIR)           # voie engins
    s.sol(-6, 17.2, 3.2, 7.8, ENROBE_CLAIR)        # raccordement à la voie publique
    s.sol(50.8, 17.2, 3.2, 7.8, ENROBE_CLAIR)
    s.sol(32, 13.4, 14, 4, "#F6D365", ep=2.2)      # section voie échelles
    s.sol(32, 13.4, 14, 4, jaune, trait=None)

    # A : R+1
    s.boite(0, 0, 0, 16, 10, 7, BEIGE)
    s.fenetres_y(0, 10, 0, 16, 7, 5, 2)
    s.fenetres_x(16, 0, 0, 10, 7, 3, 2)
    s.poly([(0, 10, 3.5), (16, 10, 3.5), (16, 0, 3.5)], "none", trait="#C1121F", ep=3, tirets="10 6")
    # B : R+4
    s.boite(31, 0, 0, 16, 11, 15, BEIGE)
    s.fenetres_y(31, 11, 0, 16, 15, 5, 5)
    s.fenetres_x(47, 0, 0, 11, 15, 3, 5)
    s.poly([(31, 11, 12), (47, 11, 12), (47, 0, 12)], "none", trait="#C1121F", ep=3, tirets="10 6")
    for xb in (34, 44):
        s.boite(xb - 1.6, 11, 11.8, 3.2, 1.4, 0.35, GRIS)

    for (x, y) in [(-9, 11), (23, -5), (54, 6)]:
        s.icone("arbre_01", (x, y, 0), 56)

    s.icone("SP_fpt_02", (7, 15.6, 0), 128, ancre=(0.5, 0.80))
    s.icone("SP_bea_02", (39, 15.4, 0), 184, ancre=(0.52, 0.80))
    s.ligne((39, 15.4, 3.4), (34, 12.4, 12.2), "#1D4ED8", 3, "10 7")

    s.cote((0, 10, 0), (0, 10, 3.5), "≤ 8 m", decal=(-2.5, 0, 0), dx_txt=-50)
    s.cote((31, 11, 0), (31, 11, 12), "> 8 m", decal=(-2.5, 0, 0), dx_txt=-50)
    s.repere((6, 10, 3.5), "plancher bas du dernier\nniveau accessible au public", du=-170, dv=-190, couleur="#C1121F", taille=17)
    s.repere((40, 11, 12), "plancher bas du dernier\nniveau accessible au public", du=150, dv=-230, couleur="#C1121F", taille=17)

    u, v = s.p(10, 21, 0); s.etiquette(u - 40, v + 26, "voie engins\nou espace libre", "#374151", 18, gras=False)
    u, v = s.p(46, 17.4, 0); s.etiquette(u + 60, v + 40, "voie échelles", "#8A6200", 19)
    s.etiquette(*s.p(46, 31, 0), "voie publique", "#374151", 16, gras=False)
    s.pastille(*s.p(8, 5, 9.5), "A", "#1F2A37", taille=26)
    s.pastille(*s.p(39, 5.5, 17.5), "B", "#1F2A37", taille=26)

    s.bandeau([
        ("A — Plancher bas du dernier niveau accessible au public à 8 m au plus : desserte par une voie engins (CO 2 § 1)", 20, TRAIT),
        ("     ou par un espace libre (CO 2 § 3).", 20, TRAIT),
        ("B — À plus de 8 m : desserte par une voie échelles (CO 2 § 2) ; en distribution par secteurs, espaces libres possibles (CO 5).", 20, TRAIT),
        ("La distribution intérieure se choisit entre cloisonnement traditionnel, secteurs ou compartiments (CO 1 § 2) ; la desserte en découle.", 18, "#4B5563"),
    ])
    return s
