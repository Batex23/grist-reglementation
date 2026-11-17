"""Type W — W 1 à W 8 : administrations, banques, bureaux (coupe)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "W3_bureaux",
    "titre": "Type W : administrations, banques, bureaux",
    "articles": ["ERP:W 2", "ERP:W 3", "ERP:W 4", "ERP:W 8", "ERP:W 1"],
    "fiche": "",
    "legende": "Effectif du public : déclaration, ou 1 personne pour 10 m² de locaux aménagés pour le public (halls, guichets, attente), ou 1 pour 100 m² de plancher si l'aménagement n'est pas prévu. Compartiments de 800 m² au plus. Escaliers non protégés si 3 niveaux au plus, ou escalier monumental d'un hall isolé.",
    "ecarts": [
        "Locaux à risques importants : archives et stockage de papier, imprimerie ; risques moyens : réserves, reprographie, conservation informatique, dépôts d'au moins 150 L de liquides inflammables (W 4).",
        "Assujettis : 100 personnes en sous-sol, 100 en étages, 200 au total (W 1). Salles de coffres admises à plus de 6 m de profondeur (W 5).",
    ],
}

ROUGE = "#C1121F"
VIOLET = "#6D28D9"


def dessiner():
    s = Scene(1600, 1160)
    s.cartouche("Type W : administrations, banques, bureaux", "Effectif, compartiments et escaliers — coupe", "W 2 · W 3 · W 8")
    s.coupe(330, 760, 23)
    s.items.append('<rect x="0" y="100" width="1600" height="660" fill="#EEF5FB"/>')
    s.items.append('<rect x="0" y="760" width="1600" height="210" fill="#C9B79C"/>')
    hn = 3.6
    s.c_rect(0, 0, 50, 3 * hn, "#FBF8F2")
    for k in range(4):
        s.c_rect(-0.3, k * hn - 0.15, 50.6, 0.3, BETON[1], ep=1.4) if k in (0, 3) else s.c_rect(16, k * hn - 0.15, 34.3, 0.3, BETON[1], ep=1.4)
    s.c_rect(-0.3, 0, 0.3, 3 * hn, BEIGE[1]); s.c_rect(50, 0, 0.3, 3 * hn, BEIGE[1])
    # hall triple hauteur isolé + escalier monumental
    s.c_rect(0, 0.15, 16, 3 * hn - 0.3, "#EDE9FE", trait=None)
    s.c_rect(15.85, 0.15, 0.3, 3 * hn - 0.3, "#FDE2B8", trait="#B45309", ep=1.6)
    for i in range(12):
        s.c_rect(3 + i * 0.8, 0.15 + i * 0.3, 0.8, 0.3, BETON[0], ep=1)
    s.c_rect(12.6, hn - 0.15, 3.25, 0.3, BETON[1], ep=1)
    for i in range(12):
        s.c_rect(12.6 - (i + 1) * 0.8, hn + 0.15 + i * 0.3, 0.8, 0.3, BETON[0], ep=1)
    s.c_rect(0, 2 * hn - 0.15, 3.0, 0.3, BETON[1], ep=1)
    # compartiment au R+2
    s.c_rect(16.15, 2 * hn + 0.15, 33.85, hn - 0.3, "#FBF3E4", trait=None)
    s.c_rect(33, 2 * hn + 0.15, 0.3, hn - 0.3, MUR_PF[1], trait="#B45309", ep=1.6)
    # archives (risques importants) au R+1
    s.c_rect(40, hn + 0.15, 10, hn - 0.3, "#FCE3E1", trait=ROUGE, ep=2)
    s.c_texte(45, hn + 1.6, "archives", 16, ROUGE, True)
    # guichets
    s.c_rect(22, 0.15, 12, 1.1, "#D4B88E", ep=1.4)
    for x in (24, 28, 32):
        s.c_image("homme105", x, 0.15, 26)
    for x in (6, 10):
        s.c_image("femme206", x, 0.15, 26)
    s.c_texte(8, 2 * hn + 1.8, "hall", 18, VIOLET, True)
    s.c_texte(30, 2 * hn + 1.8, "compartiment ≤ 800 m²", 17, "#B45309", True)
    s.c_texte(30, hn + 1.8, "bureaux", 17, "#374151", True)
    s.c_repere(8, 2.0, "escalier monumental non protégé, dans un hall\nisolé (CO 24), ne desservant que des niveaux\ns'ouvrant sur ce hall (W 8)", 60, -400, VIOLET)
    s.c_repere(28, 1.0, "guichets, salles d'attente :\n1 personne pour 10 m² (W 2)", 200, 120, "#B45309")
    s.c_repere(45, hn + 2.6, "local à risques importants\n(archives, stockage de papier)", -60, -330, ROUGE)
    s.c_cote_v(-2, 0, 3 * hn, "3 niveaux dont le RDC :\nescaliers non protégés\nadmis (W 8)", "#374151", dx=-14)
    s.bandeau([
        ("Effectif du public selon la déclaration du maître d'ouvrage, ou à défaut : 1 personne pour 10 m² des locaux spécialement aménagés", 18, TRAIT),
        ("pour recevoir du public (halls, guichets, salles d'attente) ; 1 personne pour 100 m² de plancher si les aménagements ne sont pas prévus.", 18, TRAIT),
        ("Locaux à risques particuliers sans communication directe avec le public si les escaliers ne sont pas protégés. Patios : IT 263 (W 6).", 18, TRAIT),
    ])
    return s
