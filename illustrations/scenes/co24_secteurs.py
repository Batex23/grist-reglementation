"""CO 24 § 2 et CO 5 — Distribution par secteurs."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "CO24_secteurs",
    "titre": "Distribution par secteurs",
    "articles": ["ERP:CO 24", "ERP:CO 5"],
    "fiche": "C.11",
    "legende": "Autant de secteurs que d'escaliers normaux, de capacité comparable, isolés par une paroi CF 1 h avec un seul bloc-porte va-et-vient PF ½ h ; 800 m² au plus, 20 m au plus en façade accessible, 40 m au plus de profondeur ; une baie accessible par secteur à chaque niveau.",
    "ecarts": [
        "Établissements à risques particuliers : extinction automatique à eau ; locaux à sommeil : SSI de catégorie A (CO 24 § 2).",
    ],
}

ROUGE = "#C1121F"


def dessiner():
    s = Scene(1600, 1160, echelle=15.5, origine=(720, 210))
    s.cartouche("Distribution par secteurs", "Niveau à plus de 8 m desservi par des espaces libres — ERP", "CO 24 § 2 · CO 5")
    L, P, h = 40, 34, 1.6
    s.sol(-4, -4, L + 8, P + 18, VERT_GAZON, trait=None)
    s.sol(0, P + 2, L, 12, "#E7E1D3", ep=1.4)                        # espace libre
    s.sol(0, 0, 20, P, "#FBF3E4", ep=1.4)
    s.sol(20, 0, 20, P, "#EAF2FB", ep=1.4)
    for xs in (8, 28):                                               # un escalier normal par secteur
        s.sol(xs, 2, 4, 6, "#D6E6F7", ep=1.2)
        for k in range(1, 9):
            s.ligne((xs + 0.4, 2 + k * 0.62, 0), (xs + 3.6, 2 + k * 0.62, 0), "#5B7DB1", 1.2)
    v = [mur(0, 0, L, 0, h), mur(0, 0, 0, P, h), mur(L, 0, L, P, h), mur(0, P, 6, P, h), mur(7.4, P, 26, P, h), mur(27.4, P, L, P, h)]
    v += [mur(20, 0, 20, 15, h, ep=0.45, pal=MUR_CF), mur(20, 17, 20, P, h, ep=0.45, pal=MUR_CF)]
    for xs in (8, 28):
        v += [mur(xs, 2, xs, 8, h, pal=MUR_BLEU), mur(xs + 4, 2, xs + 4, 8, h, pal=MUR_BLEU), mur(xs, 8, xs + 1, 8, h, pal=MUR_BLEU), mur(xs + 2.2, 8, xs + 4, 8, h, pal=MUR_BLEU)]
    s.volumes(v)
    s.boite(19.85, 15, 0, 0.3, 2, 2.1, MUR_PF, ep=1.4, opacite=0.85)
    s.arc_sol((20, 15), 1.0, 90, 30, 0, ROUGE, 1.4); s.arc_sol((20, 15), 1.0, 90, 150, 0, ROUGE, 1.4)
    # baies accessibles (une par secteur) et échelles sur l'espace libre
    for xb in (6.7, 26.7):
        s.poly([(xb - 0.7, P, 0), (xb + 0.7, P, 0), (xb + 0.7, P, 1.6), (xb - 0.7, P, 1.6)], "#FFD15C", trait=ROUGE, ep=2)
    s.icone("SP_bea_02", (8, P + 7.5, 0), 175, ancre=(0.52, 0.80))
    s.icone("SP_bea_02", (28, P + 7.5, 0), 175, ancre=(0.52, 0.80))
    s.personne((5, 12, 0), 26, 1); s.personne((14, 22, 0), 26, 2, True); s.personne((26, 20, 0), 26, 3); s.personne((33, 26, 0), 26, 4, True)

    u, v_ = s.p(10, 17, 0); s.pastille(u, v_, "Secteur 1", "#B45309", taille=19)
    u, v_ = s.p(30, 17, 0); s.pastille(u, v_, "Secteur 2", "#1D4ED8", taille=19)
    s.cote((20, P, 0), (L, P, 0), "≤ 20 m en façade accessible", decal=(0, 1.2, 0), dy_txt=40, dx_txt=150)
    s.cote((L, 0, 0), (L, P, 0), "≤ 40 m", decal=(3, 0, 0), dx_txt=40)
    s.repere((20, 25, 1.6), "paroi CF 1 h", du=-300, dv=-60, couleur=ROUGE, taille=18)
    s.repere((20, 16, 2.1), "un seul bloc-porte\nva-et-vient PF ½ h", du=60, dv=-230, couleur=ROUGE, taille=18)
    s.repere((26.7, P, 1.6), "baie accessible\npar secteur", du=280, dv=60, couleur=ROUGE, taille=18)
    s.etiquette(*s.p(36, P + 12, 0), "espace libre (mise en station des échelles)", "#8A6200", 17)
    s.legende(40, 110, [("#FBF3E4", "secteur ≤ 800 m²"), ("#D6E6F7", "un escalier normal par secteur")], taille=16)

    s.bandeau([
        ("Chaque niveau est divisé en autant de secteurs que d'escaliers normaux, de capacités d'accueil du même ordre de grandeur.", 19, TRAIT),
        ("Secteurs isolés par une paroi CF 1 h équipée d'un seul bloc-porte en va-et-vient PF ½ h ; 800 m² au plus par secteur,", 19, TRAIT),
        ("20 m au plus en façade accessible, 40 m au plus pour l'autre dimension (mesures prises en œuvre).", 19, TRAIT),
        ("Les voies échelles peuvent être remplacées par des espaces libres permettant d'atteindre à chaque niveau une baie par secteur (CO 5).", 17, "#4B5563"),
    ])
    return s
