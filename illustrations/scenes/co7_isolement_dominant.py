"""CO 7 § 1 et § 2 — Isolement latéral : façade dominant la couverture d'un tiers contigu."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "CO7_isolement-facade-dominante",
    "titre": "Isolement latéral — façade dominante",
    "articles": ["ERP:CO 7", "ERP:CO 6"],
    "fiche": "C.6",
    "legende": "Paroi d'isolement CF 2 h (3 h si risques particuliers). Si une façade domine la couverture de l'autre : façade CF 2 h sur 8 m au-dessus de la ligne d'héberge, ou toiture basse PF ½ h sur 4 m.",
    "ecarts": [
        "Équivalences européennes (arrêté du 22 mars 2004) : CF 2 h = EI 120 (REI 120 si la paroi est porteuse), PF ½ h = E 30.",
    ],
}

ROUGE = "#C1121F"
CF = ("#F7C6C2", "#EE9D96", "#D9776F")


def dessiner():
    s = Scene(1600, 1160, echelle=15, origine=(600, 470))
    s.cartouche("Isolement latéral — façade dominante", "ERP contigu à un bâtiment tiers plus haut", "CO 7 § 1-2")
    h1 = s.motif("h1", ROUGE, 2.4, 12, 45)
    h2 = s.motif("h2", "#1D4ED8", 2.4, 12, -45)

    s.sol(-8, -8, 50, 34, VERT_GAZON, trait=None)
    s.sol(-8, 18, 50, 6, ENROBE, ep=1.2)

    # tiers (haut) à gauche, ERP (bas) à droite, paroi commune en x = 14
    s.boite(0, 0, 0, 14, 14, 22, GRIS)
    s.fenetres_y(0, 14, 0, 14, 22, 4, 6)
    # façade du tiers au-dessus de la couverture de l'ERP (face +x, z 7 → 22)
    s.poly([(14, 0, 7), (14, 14, 7), (14, 14, 15), (14, 0, 15)], h1, trait=ROUGE, ep=2.6)
    for y in (3.5, 10.5):
        s.poly([(14, y - 0.8, 9.5), (14, y + 0.8, 9.5), (14, y + 0.8, 11.5), (14, y - 0.8, 11.5)], CF[2], trait=ROUGE, ep=2)
    # ERP
    s.boite(14, 0, 0, 20, 14, 7, BEIGE)
    s.fenetres_y(14, 14, 0, 20, 7, 6, 2)
    s.fenetres_x(34, 0, 0, 14, 7, 4, 2)
    s.sol(14, 0, 4, 14, h2, trait="#1D4ED8", ep=2.4, z=7)
    # paroi d'isolement (trait de coupe sur la façade avant)
    s.ligne((14, 14, 0), (14, 14, 7), ROUGE, 6)
    s.ligne((14, 14, 7), (14, 0, 7), "#111111", 3)

    s.cote((14, 0, 7), (14, 0, 15), "8 m", decal=(0, -2.5, 0), dx_txt=-40)
    s.cote((14, 0, 7.05), (18, 0, 7.05), "4 m", decal=(0, -1.5, 0), dy_txt=-26, dx_txt=20)
    s.repere((14, 14, 3.5), "paroi d'isolement CF 2 h\n(3 h si risques particuliers)", du=-260, dv=150, couleur=ROUGE, taille=18)
    s.repere((14, 7, 13.2), "façade CF 2 h sur 8 m\nbaies PF 2 h", du=330, dv=-40, couleur=ROUGE, taille=18)
    s.repere((16, 9, 7), "ou toiture PF ½ h sur 4 m\n(PF 1 h sur 8 m si un bâtiment\nest à risques particuliers)", du=330, dv=-10, couleur="#1D4ED8", taille=18)
    s.repere((14, 0, 7), "ligne d'héberge", du=330, dv=-150, couleur=TRAIT, taille=17)
    u, v = s.p(7, 7, 22); s.pastille(u, v - 26, "Tiers", "#4B5563", taille=20)
    u, v = s.p(24, 7, 7); s.pastille(u, v - 14, "ERP", ROUGE, taille=20)
    for (x, y) in [(38, 4), (38, 12)]:
        s.icone("arbre_01", (x, y, 0), 56)

    s.bandeau([
        ("Isolement latéral par une paroi CF 2 h (3 h si l'un des bâtiments abrite une exploitation à risques particuliers d'incendie) ;", 19, TRAIT),
        ("structures indépendantes ou de même stabilité au feu que le degré coupe-feu de la paroi.", 19, TRAIT),
        ("Façade dominant la couverture de l'autre bâtiment : façade CF 2 h sur 8 m au-dessus de la ligne d'héberge, baies PF 2 h ;", 19, TRAIT),
        ("ou toiture la plus basse PF ½ h sur 4 m depuis la façade (PF 1 h sur 8 m si un des bâtiments est à risques particuliers).", 19, TRAIT),
    ])
    return s
