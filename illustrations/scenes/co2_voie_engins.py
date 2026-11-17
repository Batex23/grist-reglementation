"""CO 2 § 1 — Voie utilisable par les engins de secours (voie engins)."""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "CO2_voie-engins",
    "titre": "Voie engins",
    "articles": ["ERP:CO 2"],
    "fiche": "C.2",
    "legende": "Voie de 8 m au moins, chaussée de 3 m (6 m si la largeur exigée atteint 12 m), hauteur libre 3,50 m, rayon intérieur 11 m avec surlargeur S = 15/R, pente < 15 %, force portante 160 kN.",
    "ecarts": [
        "Force portante : 160 kN (90 kN par essieu, essieux distants d'au moins 3,60 m). Les anciennes fiches mentionnaient 130 kN.",
        "Le panneau indiquant le tonnage limite autorisé est obligatoire en permanence (CO 2 § 4).",
    ],
}

ROUGE = "#C1121F"


def arc(cx, cy, r, a0, a1, n=24):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * k / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * k / n)), 0) for k in range(n + 1)]


def dessiner():
    s = Scene(1600, 1160, echelle=18.5, origine=(640, 262))
    s.cartouche("Voie engins", "Voie utilisable par les engins de secours — ERP", "CO 2 § 1")

    s.sol(-4, -12, 50, 44, VERT_GAZON, trait=None)
    s.sol(-4, 28, 50, 4, ENROBE, ep=1.4)                       # voie publique
    for x in range(-2, 44, 6):
        s.sol(x, 29.8, 3, 0.4, "#FFFFFF", trait=None)

    # emprise de la voie (8 m) : accotements stabilisés
    acc = "#D9D4C7"
    s.sol(5, 14, 8, 14, acc, ep=1.2)
    s.poly(arc(23.5, 14, 18.5, 180, 270) + arc(23.5, 14, 10.5, 270, 180), acc, ep=1.2)
    s.sol(23.5, -4.5, 22.5, 8, acc, ep=1.2)
    # chaussée 3 m, virage avec surlargeur S = 15/R
    R, S = 11.0, 15 / 11.0
    s.sol(7.5, 14, 3, 14, ENROBE_CLAIR, ep=1.6)
    s.poly(arc(21.5, 14, R + 3 + S, 180, 270) + arc(21.5, 14, R, 270, 180), ENROBE_CLAIR, ep=1.6)
    s.sol(21.5, 0, 24.5, 3, ENROBE_CLAIR, ep=1.6)

    # bâtiment desservi à l'arrière et engin en station
    s.boite(26, -12, 0, 20, 6.5, 10, BEIGE)
    s.fenetres_y(26, -5.5, 0, 20, 10, 6, 3)
    s.icone("SP_fpt_02", (36, 1.5, 0), 170, ancre=(0.5, 0.80))
    for (x, y) in [(-1, -8), (0, 6), (18, -9)]:
        s.icone("arbre_01", (x, y, 0), 54)

    # rayon et surlargeur
    s.ligne((21.5, 14, 0), (21.5 - R * math.cos(math.radians(40)), 14 - R * math.sin(math.radians(40)), 0), ROUGE, 2.2)
    s.etiquette(*s.p(19, 8.5, 0), "R ≥ 11 m", ROUGE, 20)
    u, v = s.p(21.5 - (R + 3 + S) * math.cos(math.radians(50)), 14 - (R + 3 + S) * math.sin(math.radians(50)), 0)
    s.etiquette(u - 120, v - 40, "surlargeur S = 15 / R\n(virage de rayon < 50 m)", ROUGE, 17, gras=False)
    s.items.append(f'<circle cx="{s.p(21.5, 14)[0]:.1f}" cy="{s.p(21.5, 14)[1]:.1f}" r="4" fill="{ROUGE}"/>')

    # portique / passage couvert : hauteur libre 3,50 m
    for xp in (4.6, 13.0):
        s.boite(xp, 20, 0, 0.4, 0.4, 4.0, GRIS, ep=1.6)
    s.boite(4.6, 20, 3.5, 8.8, 0.4, 0.5, GRIS, ep=1.6)
    s.cote((13.2, 20.4, 0), (13.2, 20.4, 3.5), "hauteur libre\n3,50 m", rappel=False, dx_txt=40, dy_txt=-112)

    # largeurs
    s.cote((5, 24, 0), (13, 24, 0), "voie ≥ 8 m", rappel=False, dy_txt=30, dx_txt=-140)
    s.cote((7.5, 21, 0), (10.5, 21, 0), "chaussée ≥ 3 m", rappel=False, dy_txt=-40, dx_txt=-140)
    u, v = s.p(13, 18, 0); s.etiquette(u + 70, v + 4, "pente < 15 %", ROUGE, 19)

    # panneau de tonnage
    pu, pv = s.p(19, 27.2, 0)
    s.items.append(f'<line x1="{pu:.1f}" y1="{pv:.1f}" x2="{pu:.1f}" y2="{pv - 70:.1f}" stroke="#4B5563" stroke-width="4"/>')
    s.items.append(f'<circle cx="{pu:.1f}" cy="{pv - 86:.1f}" r="21" fill="#FFFFFF" stroke="{ROUGE}" stroke-width="6"/>')
    s.texte(pu, pv - 80, "16 t", 14, TRAIT, gras=True, ancre="middle")
    s.etiquette(pu + 150, pv - 86, "panneau du tonnage limite\n(visible en permanence)", "#374151", 16, gras=False)
    s.items.append(f'<line x1="{pu + 22:.1f}" y1="{pv - 86:.1f}" x2="{pu + 40:.1f}" y2="{pv - 86:.1f}" stroke="#374151" stroke-width="1.6"/>')

    # encart force portante
    x0, y0 = 1070, 690
    s.items.append(f'<rect x="{x0}" y="{y0}" width="490" height="300" rx="10" fill="#FFFFFF" stroke="#9CA3AF" stroke-width="1.5"/>')
    s.texte(x0 + 20, y0 + 34, "Force portante", 21, TRAIT, gras=True)
    bx, by = x0 + 60, y0 + 196
    s.items.append(f'<rect x="{bx}" y="{by - 58}" width="250" height="52" rx="5" fill="#E8352D" stroke="{TRAIT}" stroke-width="2.4"/>')
    s.items.append(f'<rect x="{bx + 250}" y="{by - 78}" width="80" height="72" rx="6" fill="#E8352D" stroke="{TRAIT}" stroke-width="2.4"/>')
    s.items.append(f'<rect x="{bx + 270}" y="{by - 70}" width="48" height="26" rx="3" fill="{BLEU_VITRE[1]}" stroke="{TRAIT}" stroke-width="1.6"/>')
    for wx in (bx + 60, bx + 290):
        s.items.append(f'<circle cx="{wx}" cy="{by}" r="18" fill="#2B2B2B" stroke="{TRAIT}" stroke-width="2"/><circle cx="{wx}" cy="{by}" r="7" fill="#9CA3AF"/>')
        s.items.append(f'<line x1="{wx}" y1="{by - 125}" x2="{wx}" y2="{by - 92}" stroke="{ROUGE}" stroke-width="3"/>')
        s.items.append(f'<path d="M{wx - 7},{by - 100} L{wx},{by - 88} L{wx + 7},{by - 100} z" fill="{ROUGE}"/>')
        s.texte(wx, by - 130, "≤ 90 kN", 16, ROUGE, gras=True, ancre="middle")
    s.items.append(f'<line x1="{bx + 60}" y1="{by + 36}" x2="{bx + 290}" y2="{by + 36}" stroke="{ROUGE}" stroke-width="2.2"/>')
    s.texte(bx + 175, by + 60, "essieux distants ≥ 3,60 m", 16, ROUGE, gras=True, ancre="middle")
    s.texte(x0 + 20, y0 + 284, "Véhicule de 160 kN · poinçonnement 80 N/cm² sur 0,20 m²", 15.5, "#374151")

    s.bandeau([
        ("Voie d'au moins 8 m ; chaussée hors stationnement de 3 m (largeur exigée de 8 à 12 m) ou de 6 m (largeur exigée ≥ 12 m).", 19, TRAIT),
        ("Chaussée réduite à 3 m sans accotements admise sur moins de 20 m, sauf dans les sections « voie échelles ».", 19, TRAIT),
        ("Hauteur libre 3,50 m · rayon intérieur 11 m · surlargeur S = 15/R si R < 50 m · pente < 15 % · tonnage signalé (§ 4).", 19, TRAIT),
    ])
    return s
