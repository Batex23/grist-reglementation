"""Habitation, arrêté du 31 janvier 1986, art. 4 — Voie engins et voie échelles."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "HAB4_voie-echelles",
    "titre": "Voie échelles en habitation",
    "articles": ["HAB:4", "HAB:3"],
    "fiche": "C.3",
    "legende": "Voie échelles : longueur ≥ 10 m, largeur ≥ 4 m, pente ≤ 10 %, poinçonnement 100 kN sur Ø 0,20 m. Parallèle à la façade : bord à plus de 1 m et à moins de 8 m (échelle de 30 m ; 6 m pour 24 m, 3 m pour 18 m). Perpendiculaire : extrémité à moins de 1 m de la façade.",
    "ecarts": [
        "Ce sont ces valeurs (1 à 8 m, 100 kN sur Ø 20 cm) que l'ancienne fiche ERP C.3 reprenait : elles sont propres à l'habitation. Voie engins habitation : 130 kN (40 + 90 kN, essieux à 4,50 m), hauteur libre 3,50 m (3,30 + 0,20).",
    ],
}

ROUGE = "#C1121F"


def dessiner():
    s = Scene(1600, 1160, echelle=13, origine=(640, 420))
    s.cartouche("Voie échelles en habitation", "Mise en station des échelles aériennes — bâtiments d'habitation", "Arrêté 31/01/1986 art. 4")
    jaune = s.motif("hj", "#E0A800")
    s.sol(-12, -6, 70, 46, VERT_GAZON, trait=None)
    s.sol(-12, 30, 70, 8, ENROBE, ep=1.4)
    H = 20
    s.boite(0, 0, 0, 30, 12, H, BEIGE)
    s.fenetres_y(0, 12, 0, 30, H, 9, 7)
    s.fenetres_x(30, 0, 0, 12, H, 4, 7)
    # voie parallèle
    s.sol(-6, 16, 42, 4, ENROBE_CLAIR, ep=1.4)
    s.sol(6, 16, 14, 4, "#F6D365", ep=2.2); s.sol(6, 16, 14, 4, jaune, trait=None)
    s.sol(36, 16, 4, 14, ENROBE_CLAIR, ep=1.4)
    # voie perpendiculaire (côté pignon x = 30)
    s.sol(31, 2, 10, 4, "#F6D365", ep=2.2); s.sol(31, 2, 10, 4, jaune, trait=None)
    s.sol(41, 2, 3, 28, ENROBE_CLAIR, ep=1.4)
    s.icone("SP_bea_02", (13, 18, 0), 190, ancre=(0.52, 0.80))
    s.icone("SP_bea_01", (36, 4, 0), 170, ancre=(0.5, 0.85))
    s.ligne((13, 18, 3.4), (10, 12, 17.5), "#1D4ED8", 3, "10 7")
    s.cote((20, 12, 0), (20, 16, 0), "1 à 8 m", decal=(4.5, 0, 0), dx_txt=70)
    s.cote((6, 20, 0), (20, 20, 0), "≥ 10 m", decal=(0, 2.4, 0), dy_txt=8)
    s.cote((6, 16, 0), (6, 20, 0), "≥ 4 m", decal=(-3, 0, 0), dx_txt=-50)
    s.cote((30, 6, 0), (31, 6, 0), "< 1 m", decal=(0, 1.8, 0), dy_txt=26, dx_txt=20)
    s.cote((31, 2, 0), (41, 2, 0), "≥ 10 m", decal=(0, -2, 0), dy_txt=-24)
    s.repere((13, 17.5, 0), "voie parallèle à la façade", du=-260, dv=40, couleur="#8A6200", taille=17)
    s.repere((36, 3, 0), "voie perpendiculaire", du=230, dv=-80, couleur="#8A6200", taille=17)
    s.etiquette(*s.p(36, 34, 0), "voie publique", "#374151", 16, gras=False)

    x0, y0 = 1110, 640
    s.items.append(f'<rect x="{x0}" y="{y0}" width="450" height="200" rx="10" fill="#FFFFFF" stroke="#9CA3AF" stroke-width="1.5"/>')
    s.texte(x0 + 20, y0 + 32, "Distance maximale à la façade", 18, TRAIT, gras=True)
    for i, (e, dd, acc) in enumerate((("échelle de 30 m", "8 m", "6 m"), ("échelle de 24 m", "6 m", "2 m"), ("échelle de 18 m", "3 m", "0 m"))):
        yy = y0 + 70 + 36 * i
        s.texte(x0 + 20, yy, e, 16, TRAIT)
        s.texte(x0 + 250, yy, dd, 17, ROUGE, gras=True)
        s.texte(x0 + 340, yy, acc, 17, "#1D4ED8", gras=True)
    s.texte(x0 + 230, y0 + 186, "voie            point d'accès*", 13, "#4B5563")
    s.bandeau([
        ("Voie échelles : partie de la voie engins longue d'au moins 10 m, large de 4 m (stationnement exclu), pente ≤ 10 %, poinçonnement", 18, TRAIT),
        ("100 kN sur un cercle de 0,20 m de diamètre ; raccordée à la voie publique par une voie engins si elle n'est pas sur la voie publique.", 18, TRAIT),
        ("Voie parallèle : bord le plus proche à plus de 1 m et moins de 8 m de la partie la plus saillante de la façade (échelle de 30 m).", 18, TRAIT),
        ("* 3e famille B traitée en 3e A (décision du maire) : distance horizontale du point d'accès des logements au bord de la voie.", 16, "#4B5563"),
    ])
    return s
