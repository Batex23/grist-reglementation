"""CO 3 — Façade accessible et baies accessibles."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "CO3_baies-accessibles",
    "titre": "Façade et baies accessibles",
    "articles": ["ERP:CO 3"],
    "fiche": "C.5",
    "legende": "Façade accessible : une sortie normale au niveau d'accès et des baies accessibles à chaque niveau. Baie ouvrante d'au moins 1,30 × 0,90 m ; en façade aveugle ou à châssis fixes, baies de 1,80 × 0,90 m tous les 10 à 20 m, décalées de 4 m d'un niveau à l'autre.",
    "ecarts": [],
}

ROUGE = "#C1121F"
ACCES = ("#FFE9A8", "#FFD15C", "#F2B705")


def panneau(s, x, y, z, larg=0.9, haut=1.8):
    """Panneau d'accès sur la face +x (repéré de l'extérieur)."""
    s.poly([(x, y - larg / 2, z), (x, y + larg / 2, z), (x, y + larg / 2, z + haut), (x, y - larg / 2, z + haut)], ACCES[1], trait=ROUGE, ep=2.6)
    u, v = s.p(x, y, z + haut + 0.55)
    s.items.append(f'<path d="M{u - 8:.1f},{v + 5:.1f} L{u + 8:.1f},{v + 5:.1f} L{u:.1f},{v - 9:.1f} z" fill="{ROUGE}" stroke="{TRAIT}" stroke-width="1.2"/>')


def dessiner():
    s = Scene(1600, 1160, echelle=19, origine=(760, 345))
    s.cartouche("Façade et baies accessibles", "Accès des secours à tous les niveaux recevant du public — ERP", "CO 3")

    s.sol(-4, -4, 32, 38, VERT_GAZON, trait=None)
    for (x, y) in [(-2, 2), (4, -2)]:
        s.icone("arbre_01", (x, y, 0), 60)
    s.sol(20, -4, 4, 38, ENROBE_CLAIR, ep=1.4)            # voie le long de la façade aveugle
    s.sol(-4, 32, 24, 2, ENROBE_CLAIR, ep=1.4)            # voie le long de la façade courante

    H = 12
    s.boite(0, 0, 0, 16, 30, H, ("#E6E8EC", "#D9C2A6", "#B7BDC6"))
    # façade +y (à gauche) : baies ouvrantes à chaque niveau
    s.fenetres_y(0, 30, 0, 16, H, 5, 4, larg=0.9 * 1.3, haut=1.3 * 1.2, marge_bas=1.0)
    s.poly([(7.4, 30, 0), (8.6, 30, 0), (8.6, 30, 2.3), (7.4, 30, 2.3)], "#3F8F5A", ep=1.6)   # sortie normale
    # façade +x (à droite) : façade aveugle (bardage, châssis fixes)
    for k in range(1, 15):
        s.ligne((16, k * 2, 0), (16, k * 2, H), "#9CA3AF", 1)
    for z in (3, 6, 9):
        s.ligne((16, 0, z), (16, 30, z), "#9CA3AF", 1)
    for z, ys in ((3.4, (4, 18)), (6.4, (8, 22)), (9.4, (4, 18))):
        for y in ys:
            panneau(s, 16, y, z)
    s.poly([(16, 26.4, 0), (16, 28.0, 0), (16, 28.0, 2.3), (16, 26.4, 2.3)], "#3F8F5A", ep=1.6)

    # cotes sur la façade aveugle
    s.cote((16, 4, 5.4), (16, 18, 5.4), "10 à 20 m", rappel=False, dy_txt=-30, dx_txt=-20)
    s.cote((16, 4, 3.0), (16, 8, 3.0), "≥ 4 m", rappel=False, dy_txt=34, dx_txt=10)
    s.ligne((16, 8, 3.0), (16, 8, 6.4), ROUGE, 1.4, "4 3")
    s.repere((16, 18.45, 4.3), "panneau ouvrant\n≥ 1,80 × 0,90 m\nrepérable de l'extérieur", du=250, dv=90, couleur=ROUGE, taille=18)
    s.repere((2.0, 30, 9.6), "baie ouvrante\n≥ 1,30 × 0,90 m", du=-150, dv=40, couleur="#1D4ED8", taille=18)
    s.repere((8, 30, 1.2), "sortie normale\nau niveau d'accès", du=-210, dv=40, couleur="#15803D", taille=18)

    s.icone("SP_bea_01", (22, 27, 0), 150, ancre=(0.5, 0.85))
    for (x, y) in [(26, 30), (26, 4)]:
        s.icone("arbre_01", (x, y, 0), 60)

    u, v = s.p(0, 30, H); s.pastille(u - 30, v - 34, "Façade courante", "#1F2A37", taille=17)
    u, v = s.p(16, 2, H); s.pastille(u + 40, v - 30, "Façade aveugle ou à châssis fixes", "#1F2A37", taille=17, ancre="start")

    s.bandeau([
        ("Façade accessible : permet aux secours d'intervenir à tous les niveaux recevant du public ; une sortie normale au niveau d'accès", 19, TRAIT),
        ("et des baies accessibles à chaque niveau. Baie accessible : baie ouvrante d'au moins 1,30 m de haut et 0,90 m de large.", 19, TRAIT),
        ("Façade aveugle ou à châssis fixes : panneaux de 1,80 × 0,90 m, espacés de 10 à 20 m sur un même niveau, décalés d'au moins 4 m", 19, TRAIT),
        ("en projection horizontale d'un niveau à l'autre, ouvrables de l'extérieur et de l'intérieur, aisément repérables par les secours.", 19, TRAIT),
    ])
    return s
