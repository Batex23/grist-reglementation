"""CO 9 — Isolement entre un ERP et un tiers superposés."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "CO9_superposition",
    "titre": "Isolement — ERP et tiers superposés",
    "articles": ["ERP:CO 9", "ERP:CO 12"],
    "fiche": "C.6",
    "legende": "Le plancher séparatif est CF 1 h ou 2 h si le dernier niveau de l'ERP est à 8 m au plus, CF 2 h ou 3 h au-delà, selon que la partie inférieure est à risques courants ou particuliers ; la structure située dessous a la même stabilité au feu.",
    "ecarts": [],
}

ROUGE = "#C1121F"


def dessiner():
    s = Scene(1600, 1160, echelle=17, origine=(600, 390))
    s.cartouche("Isolement — superposition", "ERP et tiers superposés dans un même bâtiment", "CO 9 · CO 12 § 2")
    H1, H2 = 7, 14
    s.sol(-6, -6, 38, 34, VERT_GAZON, trait=None)
    s.sol(-6, 22, 38, 6, ENROBE, ep=1.2)
    # partie basse : tiers (commerce, parking…)
    s.boite(0, 0, 0, 22, 16, H1, GRIS)
    s.fenetres_y(0, 16, 0, 22, H1, 6, 2)
    s.fenetres_x(22, 0, 0, 16, H1, 4, 2)
    # plancher séparatif
    s.boite(-0.4, -0.4, H1, 22.8, 16.8, 0.7, ("#F28B82", "#E06A60", "#C24E45"), ep=2.4)
    # partie haute : ERP
    s.boite(0, 0, H1 + 0.7, 22, 16, H2 - H1 - 0.7, BEIGE)
    s.fenetres_y(0, 16, H1 + 0.7, 22, H2 - H1 - 0.7, 6, 2)
    s.fenetres_x(22, 0, H1 + 0.7, 16, H2 - H1 - 0.7, 4, 2)
    # poteaux de la partie basse (structure SF = CF du plancher)
    for x in (5.5, 11, 16.5):
        s.ligne((x, 16, 0.2), (x, 16, H1 - 0.2), "#1D4ED8", 4)
    s.repere((11, 16, 3.2), "structure sous le plancher :\nSF de même degré que le plancher", du=-200, dv=170, couleur="#1D4ED8", taille=18)
    s.repere((22.4, 8, H1 + 0.35), "plancher séparatif CF", du=250, dv=-60, couleur=ROUGE, taille=19)
    u, v = s.p(11, 8, H2); s.pastille(u, v, "ERP", ROUGE, taille=20)
    u, v = s.p(22, 8, H1 / 2); s.pastille(u + 70, v + 30, "Tiers", "#4B5563", taille=20)

    # tableau
    x0, y0, cw, rh = 980, 640, [250, 160, 160], 54
    rows = [("Partie inférieure", "ERP ≤ 8 m", "ERP > 8 m"),
            ("à risques courants", "CF 1 h", "CF 2 h"),
            ("à risques particuliers", "CF 2 h", "CF 3 h")]
    s.items.append(f'<rect x="{x0}" y="{y0}" width="{sum(cw)}" height="{rh * 3}" rx="8" fill="#FFFFFF" stroke="#9CA3AF" stroke-width="1.5"/>')
    s.items.append(f'<rect x="{x0}" y="{y0}" width="{sum(cw)}" height="{rh}" rx="8" fill="#1F2A37"/>')
    for i, r in enumerate(rows):
        xx = x0
        for j, c in enumerate(r):
            col = "#FFFFFF" if i == 0 else (ROUGE if j else TRAIT)
            s.texte(xx + 14, y0 + i * rh + 34, c, 16 if i == 0 else 19, col, gras=(i == 0 or j > 0))
            xx += cw[j]
        if i:
            s.items.append(f'<line x1="{x0}" y1="{y0 + i * rh}" x2="{x0 + sum(cw)}" y2="{y0 + i * rh}" stroke="#E5E7EB" stroke-width="1.5"/>')
    s.texte(x0, y0 - 34, "Degré coupe-feu du plancher séparatif", 18, TRAIT, gras=True)
    s.texte(x0, y0 - 12, "selon la hauteur du plancher bas du dernier niveau de l'ERP", 15, "#4B5563")

    s.bandeau([
        ("Le plancher séparant l'ERP d'un tiers superposé est CF 1 h (partie inférieure à risques courants) ou CF 2 h (à risques particuliers)", 19, TRAIT),
        ("lorsque le plancher bas du niveau le plus haut de l'ERP est à 8 m au plus ; CF 2 h ou CF 3 h au-delà de 8 m.", 19, TRAIT),
        ("Un ERP ne s'installe dans un bâtiment à occupations multiples que si la structure située sous ce plancher a une stabilité au feu", 19, TRAIT),
        ("au moins égale au degré coupe-feu du plancher (CO 12 § 2). Équivalences : CF 1 h = REI 60, CF 2 h = REI 120, CF 3 h = REI 180.", 17, "#4B5563"),
    ])
    return s
