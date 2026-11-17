"""Type PS — PS 6, PS 8, PS 16, PS 18 : structure, isolement (coupe)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "PS8_structure-isolement",
    "titre": "Parcs de stationnement : structure et isolement",
    "articles": ["ERP:PS 6", "ERP:PS 8", "ERP:PS 16", "ERP:PS 5"],
    "fiche": "",
    "legende": "Structure R 120 et planchers REI 120 (R 90 / REI 90 sprinklé ; R 60 si ≤ 2 niveaux, sprinklé et non surmonté). Paroi d'isolement avec un tiers contigu : CF du degré le plus exigeant, 1 h au moins (4 h avec un IGH) ; plancher avec un tiers superposé : REI 90. Intercommunication par sas de 3 m², portes PF ½ h vers l'intérieur.",
    "ecarts": [
        "Planchers les plus haut et bas à 28 m au plus du niveau de référence ; ascenseur pompiers au-delà de 7 niveaux en infrastructure (PS 5, PS 24).",
        "Parois en M 0 / A2-s2, d0 ; revêtements M 1 / B-s3, d0 (PS 16). Désenfumage naturel limité aux niveaux de référence et adjacents, 12 dm² par véhicule (PS 18).",
    ],
}

ROUGE = "#C1121F"
BLEU = "#1D4ED8"


def dessiner():
    s = Scene(1600, 1160)
    s.cartouche("Parcs de stationnement : structure et isolement", "Parc en infrastructure sous un bâtiment, contigu à un tiers — coupe", "PS 6 · PS 8")
    s.coupe(120, 560, 26)
    s.items.append('<rect x="0" y="100" width="1600" height="460" fill="#EEF5FB"/>')
    s.items.append('<rect x="0" y="560" width="1600" height="420" fill="#C9B79C"/>')
    s.items.append('<line x1="0" y1="560" x2="1600" y2="560" stroke="#4B7F33" stroke-width="8"/>')
    # bâtiment au-dessus (ERP / habitation)
    s.c_rect(0, 0.4, 30, 14, BEIGE[1])
    for z in (3.9, 7.4, 10.9):
        s.c_rect(0, z, 30, 0.3, BETON[1], ep=1.2)
    for x in range(2, 30, 4):
        for z in (1.5, 5, 8.5, 12):
            s.c_rect(x, z, 1.4, 1.4, BLEU_VITRE[1], ep=1.2)
    s.c_texte(15, 15.2, "bâtiment au-dessus (ERP, habitation…)", 17, "#374151", True)
    # dalle d'isolement
    s.c_rect(-0.5, 0, 31, 0.4, "#F28B82", ep=2)
    # parc 2 niveaux
    s.c_rect(0, -6.4, 30, 6.4, "#ECEEF1")
    s.c_rect(-0.5, -3.3, 31, 0.3, BETON[1], ep=1.4)
    s.c_rect(-0.5, -6.8, 31, 0.4, BETON[1], ep=1.4)
    for x in (6, 12, 18, 24):
        s.c_rect(x - 0.2, -6.4, 0.4, 6.4, BLEU, trait=None)
    for (x, z, c) in [(3, -6.4, "#EF4444"), (9, -6.4, "#3B82F6"), (14, -3.0, "#F59E0B"), (20, -3.0, "#EF4444")]:
        s.c_rect(x, z, 4.2, 1.4, c, ep=1.4)
    s.c_texte(26, -2.0, "parc − 1", 16, "#374151", True)
    s.c_texte(26, -5.3, "parc − 2", 16, "#374151", True)
    # tiers contigu
    s.c_rect(31, -6.8, 0.6, 15, "#F7C6C2", trait=ROUGE, ep=2)
    s.c_rect(31.6, -6.8, 14, 15, GRIS[1])
    for z in (0.4, 3.9):
        s.c_rect(31.6, z, 14, 0.3, BETON[1], ep=1.2)
    s.c_texte(38.6, 6, "tiers contigu", 17, "#374151", True)
    # sas d'intercommunication au niveau −1
    s.c_rect(28, -3.0, 3, 2.6, "#FDE2E2", trait=ROUGE, ep=2)
    s.c_repere(15, 0.2, "plancher d'isolement avec un tiers superposé :\nCF 1 h ½ (REI 90)", -60, -400, ROUGE)
    s.c_repere(12, -4.5, "structure SF 2 h (R 120), planchers REI 120 ;\nR 90 / REI 90 si sprinklé ; R 60 si ≤ 2 niveaux,\nsprinklé et non surmonté", -60, 300, BLEU)
    s.c_repere(31.3, 4, "paroi avec un tiers contigu : CF du degré le plus\nexigeant, 1 h au moins (4 h si IGH)", 150, -260, ROUGE)
    s.c_repere(29.5, -1.7, "sas ≥ 3 m², largeur ≥ 0,90 m, parois du degré\ndu mur, 2 portes PF ½ h (E 30-C) vers l'intérieur", 330, 220, ROUGE)
    s.c_cote_v(-1.5, -6.4, 0, "", "#374151")
    s.c_texte(-1.5, -8.0, "≤ 28 m sous le niveau de référence", 15, "#374151", ancre="start")
    s.bandeau([
        ("Les parcs sont des établissements à risques courants (PS 8). Vis-à-vis à moins de 8 m : façade PF 1 h, baies PF ½ h ; CF 1 h si le tiers", 18, TRAIT),
        ("a des locaux à sommeil au-dessus du 1er étage ; pas d'exigence à 4 m si le niveau le plus haut accessible est à moins de 8 m.", 18, TRAIT),
        ("Parcs de plus de 10 véhicules de 3,5 t au plus (PS 1). Voie engins au niveau de référence (PS 5). Visite de réception au-delà de 250 véhicules (PS 33).", 18, TRAIT),
    ])
    return s
