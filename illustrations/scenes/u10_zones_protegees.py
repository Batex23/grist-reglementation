"""Type U — U 10, U 16, U 26 : zones protégées et zones de mise à l'abri."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "U10_zones-protegees",
    "titre": "Type U : zones protégées et zones de mise à l'abri",
    "articles": ["ERP:U 10", "ERP:U 16", "ERP:U 26"],
    "fiche": "",
    "legende": "Niveaux avec locaux à sommeil recoupés par une cloison CF 1 h de façade à façade : au moins deux zones protégées de capacité comparable. Au-delà de 20 lits, chaque zone protégée est divisée en zones de mise à l'abri de 20 lits au plus (cloison CF 1 h, blocs-portes PF ½ h à ferme-porte ou fermeture automatique).",
    "ecarts": [
        "Portes des chambres d'au moins 1,10 m (hors psychiatrie) et circulations de 2 UP entre escaliers et sorties (U 16).",
        "Circulations des niveaux à sommeil désenfumées mécaniquement quelle que soit leur longueur (naturel possible en R+1 après avis), asservies à la détection de la zone sinistrée (U 26).",
    ],
}

ROUGE = "#C1121F"
ORANGE = "#B45309"


def dessiner():
    s = Scene(1600, 1160, echelle=17.5, origine=(300, 300))
    s.cartouche("Type U : zones protégées et zones de mise à l'abri", "Établissements de soins — niveau d'hospitalisation", "U 10 · U 16 · U 26")
    h = 1.1
    L, P = 64, 16
    s.sol(-2, -2, L + 4, P + 4, "#E5E7EB", trait=None)
    cols = ["#FBF3E4", "#FDE7C8", "#EAF2FB", "#D6E6F7"]
    for i in range(4):
        s.sol(16 * i, 0, 16, P, cols[i], ep=1.2)
    s.sol(0, 6.5, L, 3, "#E9F3EA", ep=1.2)
    v = [mur(0, 0, L, 0, h), mur(0, 0, 0, P, h), mur(L, 0, L, P, h), mur(0, P, L, P, h)]
    for x in range(4, L, 4):
        if x % 16 == 0:
            continue
        v += [mur(x, 0, x, 6.5, h), mur(x, 9.5, x, P, h)]
    for x0 in range(0, L, 4):
        for yc in (6.5, 9.5):
            v += [mur(x0, yc, x0 + 1.2, yc, h, pal=MUR_PF), mur(x0 + 2.6, yc, x0 + 4, yc, h, pal=MUR_PF)]
    v += [mur(32, 0, 32, 6.5, h + 0.3, ep=0.45, pal=MUR_CF), mur(32, 9.5, 32, P, h + 0.3, ep=0.45, pal=MUR_CF)]
    for x in (16, 48):
        v += [mur(x, 0, x, 6.5, h + 0.15, ep=0.35, pal=("#FDE2B8", "#F7C27A", "#E0A04A")), mur(x, 9.5, x, P, h + 0.15, ep=0.35, pal=("#FDE2B8", "#F7C27A", "#E0A04A"))]
    s.volumes(v)
    for x in (16, 32, 48):
        s.boite(x - 0.2, 6.5, 0, 0.4, 3, 2.1, MUR_CF if x == 32 else ("#FDE2B8", "#F7C27A", "#E0A04A"), ep=1.4, opacite=0.6)
    for x0 in range(0, L, 4):
        for y0 in (2.5, 12.5):
            s.boite(x0 + 0.8, y0 - 0.9, 0, 2.2, 1.0, 0.5, ("#FFFFFF", "#E5E7EB", "#D1D5DB"), ep=1)
    u, v_ = s.p(16, 3, h); s.pastille(u, v_ - 90, "zone protégée 1", ROUGE, taille=16)
    u, v_ = s.p(48, 3, h); s.pastille(u, v_ - 90, "zone protégée 2", "#1D4ED8", taille=16)
    for i, x in enumerate((8, 24, 40, 56)):
        u, v_ = s.p(x, 16, 0); s.texte(u, v_ + 26, "≤ 20 lits", 15, ORANGE, gras=True, ancre="middle")
    s.repere((32, 13, 1.4), "cloison CF 1 h de façade à façade\nentre zones protégées", du=180, dv=-180, couleur=ROUGE, taille=17)
    s.repere((48, 3, 1.25), "zones de mise à l'abri : cloison CF 1 h,\nblocs-portes PF ½ h (E 30-C) à ferme-porte\nou fermeture automatique", du=150, dv=-150, couleur=ORANGE, taille=17)
    s.repere((6, 6.5, 1.1), "portes des chambres ≥ 1,10 m", du=-40, dv=-150, couleur="#374151", taille=17)
    s.repere((20, 8, 0), "circulations de 2 UP, désenfumage\nmécanique asservi à la détection", du=-60, dv=230, couleur="#15803D", taille=17)
    s.bandeau([
        ("Tous les niveaux comportant des locaux à sommeil sont recoupés, quelle que soit leur longueur, en au moins deux zones protégées isolées", 18, TRAIT),
        ("entre elles (cloison CF 1 h, EI ou REI 60) ; passage d'une zone à l'autre uniquement par des portes situées sur les circulations.", 18, TRAIT),
        ("Au-delà de 20 lits par zone protégée : zones de mise à l'abri de 20 lits au plus, de capacité comparable. Effectif : U 2.", 18, TRAIT),
    ])
    return s
