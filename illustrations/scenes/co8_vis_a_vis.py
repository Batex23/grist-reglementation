"""CO 8 — Isolement entre un ERP et un bâtiment tiers en vis-à-vis."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "CO8_vis-a-vis",
    "titre": "Isolement — bâtiments en vis-à-vis",
    "articles": ["ERP:CO 8"],
    "fiche": "C.6",
    "legende": "Façades séparées par moins de 8 m : l'une est PF 1 h (CF 1 h avec sommeil au-dessus du 1er étage), baies PF ½ h. Pas d'exigence à partir de 4 m si le dernier niveau accessible est à moins de 8 m et sans sommeil au-dessus du 1er étage.",
    "ecarts": [],
}

ROUGE = "#C1121F"


def dessiner():
    s = Scene(1600, 1160, echelle=17, origine=(560, 330))
    s.cartouche("Isolement — vis-à-vis", "ERP et bâtiment tiers séparés par une aire libre", "CO 8")
    hr = s.motif("hr", ROUGE, 2.2, 12, 45)
    H = 12

    s.sol(-8, -8, 50, 34, VERT_GAZON, trait=None)
    s.sol(16, -8, 7, 34, "#E7E1D3", ep=1.2)                 # aire libre
    s.boite(0, 0, 0, 16, 16, H, BEIGE)
    s.fenetres_y(0, 16, 0, 16, H, 5, 4)
    # façade de l'ERP en vis-à-vis : PF 1 h, baies PF ½ h
    s.poly([(16, 0, 0), (16, 16, 0), (16, 16, H), (16, 0, H)], hr, trait=ROUGE, ep=2.6)
    for y in (3, 8, 13):
        for z in (1, 4, 7, 10):
            s.poly([(16, y - 0.7, z), (16, y + 0.7, z), (16, y + 0.7, z + 1.4), (16, y - 0.7, z + 1.4)], "#D9776F", trait=ROUGE, ep=1.6)
    s.boite_fantome(23, 0, 0, 14, 16, 15)

    s.cote((16, 16, 0), (23, 16, 0), "< 8 m", decal=(0, 2.5, 0), dy_txt=26)
    s.repere((16, 6, 8.6), "façade PF 1 h\n(CF 1 h si sommeil\nau-dessus du 1er étage)", du=-360, dv=-170, couleur=ROUGE, taille=18)
    s.repere((16, 13, 4.7), "baies obturées\npar des éléments PF ½ h", du=-330, dv=150, couleur=ROUGE, taille=18)
    u, v = s.p(8, 8, H); s.pastille(u, v, "ERP", ROUGE, taille=20)
    u, v = s.p(30, 8, 15); s.pastille(u, v, "Tiers", "#4B5563", taille=20)
    u, v = s.p(19.5, -6, 0); s.etiquette(u, v - 10, "aire libre", "#8A6200", 18)

    s.bandeau([
        ("Aire libre de moins de 8 m entre les façades : la façade de l'un des bâtiments est PF 1 h, baies obturées par des éléments PF ½ h.", 19, TRAIT),
        ("Bâtiment avec locaux à sommeil au-dessus du 1er étage : façade CF 1 h, baies PF ½ h.", 19, TRAIT),
        ("Aucune exigence si l'aire libre fait au moins 4 m, le dernier niveau accessible est à moins de 8 m et sans sommeil au-dessus du 1er étage.", 19, TRAIT),
        ("Les parois de façade limitant un escalier protégé relèvent de CO 53, jamais de cet article.", 17, "#4B5563"),
    ])
    return s
