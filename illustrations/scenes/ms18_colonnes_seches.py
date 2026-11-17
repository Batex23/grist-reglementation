"""MS 5, MS 6, MS 18 à MS 21 — Points d'eau et colonnes sèches."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "MS18_colonnes-seches-points-eau",
    "titre": "Colonnes sèches et points d'eau",
    "articles": ["ERP:MS 18", "ERP:MS 19", "ERP:MS 20", "ERP:MS 21", "ERP:MS 5", "ERP:MS 6"],
    "fiche": "MS 2-3",
    "legende": "Colonne sèche dès qu'un local à risques importants est en étage à plus de 18 m de la voie engins : raccord d'alimentation sur la façade la plus proche d'un poteau, à 60 m de cheminement au plus, signalé, prises d'incendie dans les cages d'escalier, vidange et purge.",
    "ecarts": [
        "Défense extérieure contre l'incendie : depuis 2015, besoins en eau fixés par le règlement départemental de DECI (RDDECI 33), et non plus par la circulaire n° 465 de 1951 citée par l'ancienne fiche (60 m³/h sous 1 bar, réserve de 120 m³).",
        "Colonnes en charge (humides) : prévues par les dispositions particulières de certains types et en IGH ; elles ne figurent pas dans les dispositions générales MS.",
    ],
}

ROUGE = "#C1121F"


def dessiner():
    s = Scene(1600, 1160, echelle=11, origine=(640, 440))
    s.cartouche("Colonnes sèches et points d'eau", "Alimentation des moyens des sapeurs-pompiers dans les étages — ERP", "MS 18 à MS 21")
    s.sol(-10, -6, 62, 50, VERT_GAZON, trait=None)
    s.sol(-10, 22, 62, 6, ENROBE, ep=1.4)
    H = 24
    s.boite(0, 0, 0, 22, 14, H, BEIGE)
    s.fenetres_y(0, 14, 0, 22, H, 6, 8)
    s.fenetres_x(22, 0, 0, 14, H, 4, 8)
    # cage d'escalier en façade et colonne
    s.boite(16, 14, 0, 4, 0.2, H, MUR_BLEU, ep=1.6)
    s.ligne((18, 14.3, 0.8), (18, 14.3, H - 0.5), ROUGE, 6)
    for z in range(3, H, 3):
        s.boite(17.6, 14.2, z + 0.8, 0.8, 0.3, 0.5, ("#F87171", "#EF4444", "#B91C1C"), ep=1.2)
    # raccord d'alimentation en façade
    s.boite(17.3, 14.2, 0.6, 1.4, 0.4, 0.9, ("#FCA5A5", "#EF4444", "#991B1B"), ep=1.6)
    u, v = s.p(18, 14.6, 1.05); s.pastille(u + 60, v + 4, "CS", ROUGE, taille=14)
    # poteau d'incendie et engin
    s.icone("pei-rouge", (40, 21, 0), 26)
    s.icone("SP_fpt_02", (30, 25, 0), 140, ancre=(0.5, 0.8))
    s.chemin([(39.5, 21.2, 0.1), (18, 21.2, 0.1), (18, 15, 0.1)], "#2563EB", 4.5, "10 6", fleche=False)
    u, v = s.p(29, 21.2, 0); s.etiquette(u + 150, v - 40, "cheminement ≤ 60 m\nentre poteau et raccord", "#2563EB", 17)
    # local à risques importants en étage > 18 m
    s.poly([(0, 14, 19.5), (8, 14, 19.5), (8, 14, 22), (0, 14, 22)], "#FCA5A5", trait=ROUGE, ep=2.4, opacite=0.85)
    s.cote((0, 14, 0), (0, 14, 19.5), "> 18 m", decal=(-4, 0, 0), dx_txt=-40)
    s.repere((4, 14, 21), "local à risques importants\nen étage", du=-280, dv=20, couleur=ROUGE, taille=17)
    s.repere((18, 14.2, 12.8), "prises d'incendie dans la cage\nd'escalier ou ses accès", du=340, dv=-120, couleur=ROUGE, taille=17)
    s.repere((18, 14.4, 1.3), "raccord d'alimentation signalé, sur la façade\nla plus proche des poteaux, pancarte\nindiquant l'escalier desservi", du=-330, dv=120, couleur=ROUGE, taille=17)
    s.repere((40, 21, 1.6), "point d'eau incendie\n(DECI)", du=170, dv=40, couleur="#B91C1C", taille=17)
    s.bandeau([
        ("Colonnes sèches conformes aux normes (NF S 61-750, NF S 61-759) : raccords d'alimentation facilement accessibles, non regroupés", 18, TRAIT),
        ("sauf cas particulier, prises d'incendie dans les cages d'escalier, dispositif de vidange et de purge d'air.", 18, TRAIT),
        ("Points d'eau : poteaux ou bouches normalisés si les prises publiques sont trop éloignées ou insuffisantes (MS 5) ; besoins fixés selon", 18, TRAIT),
        ("les directives du service d'incendie et de secours — en Gironde, le règlement départemental de DECI (MS 6).", 18, TRAIT),
    ])
    return s
