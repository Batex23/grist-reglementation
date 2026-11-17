"""CO 2 § 2 — Section de voie utilisable pour la mise en station des échelles aériennes (voie échelles)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "CO2_voie-echelles",
    "titre": "Voie échelles",
    "articles": ["ERP:CO 2"],
    "fiche": "C.3",
    "legende": "Section de voie engins pour la mise en station des échelles aériennes : longueur ≥ 10 m, chaussée ≥ 4 m, pente ≤ 10 %, point d'accès en façade tous les 20 m au plus.",
    "ecarts": [
        "L'ancienne fiche indiquait une distance voie–façade de 1 à 8 m et une force portante de 100 kN sur Ø 20 cm : ces valeurs viennent de l'arrêté habitation du 31 janvier 1986 (art. 4), pas de CO 2. En ERP, la position est définie par l'objectif : atteindre un point d'accès d'où toutes les baies sont accessibles.",
        "Force portante de la voie engins : 160 kN (90 kN par essieu, essieux à 3,60 m), et non 130 kN.",
    ],
}


def dessiner():
    s = Scene(1600, 1160, echelle=15.5, origine=(740, 430))
    s.cartouche("Voie échelles", "Section de voie pour la mise en station des échelles aériennes — ERP", "CO 2 § 2")

    # sol
    s.sol(-10, -6, 58, 50, VERT_GAZON, trait=None)
    # voie publique
    s.sol(-10, 33, 58, 9, ENROBE, ep=1.6)
    for x in range(-8, 46, 6):
        s.sol(x, 37.3, 3, 0.4, "#FFFFFF", trait=None)
    # voie engins privée (chaussée 3 m) le long de la façade + raccordement
    s.sol(-4, 18, 44, 3, ENROBE_CLAIR)
    s.sol(37, 21, 3, 12, ENROBE_CLAIR)
    # section voie échelles : chaussée portée à 4 m sur 14 m
    s.sol(4, 17, 14, 4, "#F6D365", ep=2.4)
    s.sol(4, 17, 14, 4, "url(#hach)", trait=None)

    # bâtiment R+5 (façade desservie tournée vers la voie)
    s.boite(0, 0, 0, 30, 12, 18, BEIGE)
    s.fenetres_y(0, 12, 0, 30, 18, 10, 6)
    s.fenetres_x(30, 0, 0, 12, 18, 4, 6)
    # points d'accès (balcons) au 5e étage
    for xb in (6, 24):
        s.boite(xb - 2.2, 12, 14.8, 4.4, 1.8, 0.4, GRIS)
        s.poly([(xb - 2.2, 13.8, 15.2), (xb + 2.2, 13.8, 15.2), (xb + 2.2, 13.8, 16.3), (xb - 2.2, 13.8, 16.3)], "#FFFFFF", ep=1.8, opacite=0.6)
        s.poly([(xb + 2.2, 12, 15.2), (xb + 2.2, 13.8, 15.2), (xb + 2.2, 13.8, 16.3), (xb + 2.2, 12, 16.3)], "#FFFFFF", ep=1.8, opacite=0.6)

    # végétation
    for (x, y) in [(-6, 10), (34, 8), (44, 14)]:
        s.icone("arbre_01", (x, y, 0), 62)
    s.icone("buisson_01", (22, 15, 0), 40)

    # échelle aérienne en station
    s.icone("SP_bea_02", (11, 19.2, 0), 205, ancre=(0.52, 0.80))
    s.icone("SP_fpt_02", (26, 36.5, 0), 140, ancre=(0.5, 0.80))
    s.icone("homme101", (8, 29, 0), 24)

    # portée de l'échelle vers le point d'accès
    s.ligne((11, 19, 3.4), (6, 13.8, 15.4), "#1D4ED8", 3, "10 7")
    s.repere((5, 13.8, 15.6), "point d'accès\n(balcon, coursive…)", du=-200, dv=40, couleur="#1D4ED8", taille=19)

    # cotes
    s.cote((4, 21, 0), (18, 21, 0), "L ≥ 10 m", decal=(0, 2.4, 0), dy_txt=4)
    s.cote((18, 17, 0), (18, 21, 0), "chaussée\n≥ 4 m", decal=(2.6, 0, 0), dx_txt=64, dy_txt=-8)
    s.cote((6, 13.8, 16.3), (24, 13.8, 16.3), "≤ 20 m entre 2 points d'accès", decal=(0, 0, 3.2), pos=0.62, dy_txt=-30, dx_txt=40)
    u, v = s.p(18, 21, 0); s.etiquette(u + 70, v + 58, "pente ≤ 10 %", couleur="#C1121F", taille=20)
    s.repere((6, 20.5, 0), "section « voie échelles »", du=-150, dv=-60, couleur="#8A6200", taille=18)

    # légendes
    u, v = s.p(33, 19.5, 0); s.etiquette(u + 40, v + 26, "voie engins (chaussée ≥ 3 m)", couleur="#374151", taille=18, gras=False)
    s.etiquette(*s.p(10, 39.5, 0), "voie publique", couleur="#374151", taille=18, gras=False)
    s.items.append(f'<rect x="0" y="{s.h - 178}" width="{s.w}" height="178" fill="#F3F4F6"/>')
    s.texte(40, s.h - 136, "La voie échelles est une partie de la voie engins : longueur ≥ 10 m, chaussée libre ≥ 4 m, pente ≤ 10 %.", 21)
    s.texte(40, s.h - 106, "Sa position doit permettre aux échelles d'atteindre un point d'accès d'où les sapeurs-pompiers", 21)
    s.texte(40, s.h - 78, "atteignent toutes les baies de la façade ; 20 m au plus entre deux points d'accès.", 21)
    s.texte(40, s.h - 46, "Hors voie publique : raccordée par une voie engins. En impasse : largeur 10 m, chaussée libre 7 m.", 19, "#4B5563")
    s.defs.append('<pattern id="hach" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(30)"><line x1="0" y1="0" x2="0" y2="14" stroke="#E0A800" stroke-width="3"/></pattern>')

    return s
