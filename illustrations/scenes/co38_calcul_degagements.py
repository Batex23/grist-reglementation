"""CO 38 — Calcul des dégagements (nombre et largeur selon l'effectif)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "CO38_calcul-degagements",
    "titre": "Nombre et largeur des dégagements",
    "articles": ["ERP:CO 38"],
    "fiche": "C.15",
    "legende": "De 1 à 19 personnes : 1 dégagement d'1 UP. De 20 à 50 : 2 dégagements (1 UP + accessoire). De 51 à 100 : 2 × 1 UP ou 2 UP + accessoire. Au-delà : 2 dégagements jusqu'à 500, +1 par 500 ; 1 UP par 100 personnes, +1 UP jusqu'à 500.",
    "ecarts": [],
}

VERT = "#15803D"
GRISF = "#9CA3AF"


def porte(s, x, y, up, accessoire=False):
    w = 26 + 22 * up
    fill = "#FFFFFF" if accessoire else VERT
    s.items.append(f'<rect x="{x}" y="{y}" width="{w}" height="40" rx="5" fill="{fill}" stroke="{VERT if accessoire else TRAIT}" stroke-width="2" {"stroke-dasharray=\"6 4\"" if accessoire else ""}/>')
    s.texte(x + w / 2, y + 26, "acc." if accessoire else f"{up} UP", 15, VERT if accessoire else "#FFFFFF", gras=True, ancre="middle")
    return x + w + 12


def dessiner():
    s = Scene(1600, 1160)
    s.cartouche("Nombre et largeur des dégagements", "Desserte des niveaux, locaux, secteurs ou compartiments selon l'effectif — ERP", "CO 38")
    x0, y0, rh = 40, 120, 132
    cols = [40, 250, 980]
    s.items.append(f'<rect x="{x0}" y="{y0}" width="1520" height="46" rx="8" fill="#1F2A37"/>')
    for c, t in zip(cols, ["Effectif", "Dégagements exigés", "Exemple"]):
        s.texte(c + 18, y0 + 30, t, 18, "#FFFFFF", gras=True)
    lignes = [
        ("1 à 19", "1 dégagement d'1 UP", [(1, False)], ""),
        ("20 à 50", "2 dégagements : 1 UP + 1 accessoire, vers l'extérieur ou des locaux différents\nnon en cul-de-sac. En étage : escalier 1 UP + accessoire si > 8 m ou compartiments.\nEn sous-sol : escalier 1 UP + accessoire.", [(1, False), (0, True)], ""),
        ("51 à 100", "2 dégagements d'1 UP\nou 1 dégagement de 2 UP + 1 accessoire", [(1, False), (1, False)], "ou  2 UP + acc."),
        ("101 à 500", "2 dégagements ; 1 UP par 100 personnes ou fraction,\nmajoré d'1 UP", [(2, False), (2, False)], "300 pers. : 3 + 1 = 4 UP"),
        ("plus de 500", "2 dégagements + 1 par 500 personnes ou fraction au-delà\nde 500 ; 1 UP par 100 personnes ou fraction", [(3, False), (3, False), (3, False), (3, False)], "1 200 pers. : 4 dég., 12 UP"),
    ]
    y = y0 + 46
    for i, (eff, regle, portes, ex) in enumerate(lignes):
        s.items.append(f'<rect x="{x0}" y="{y}" width="1520" height="{rh}" fill="{"#FFFFFF" if i % 2 else "#F7F8FA"}" stroke="#E5E7EB" stroke-width="1"/>')
        s.texte(cols[0] + 18, y + 54, eff, 30, TRAIT, gras=True)
        s.texte(cols[0] + 18, y + 82, "personnes", 15, "#6B7280")
        for k, l in enumerate(regle.split("\n")):
            s.texte(cols[1] + 18, y + 36 + k * 26, l, 17, TRAIT)
        xx = cols[2] + 18
        for up, acc in portes:
            xx = porte(s, xx, y + 26, up, acc)
        if ex:
            s.texte(cols[2] + 18, y + 104, ex, 16, "#374151", gras=True)
        y += rh
    s.legende(40, y + 22, [(VERT, "dégagement normal (UP : unité de passage de 0,60 m)"), ("#FFFFFF", "dégagement accessoire (CO 41)")], taille=16)
    s.bandeau([
        ("Les escaliers desservant un niveau se calculent sur l'effectif cumulé de ce niveau et des niveaux situés au-dessus (étages)", 19, TRAIT),
        ("ou au-dessous (sous-sols) — CO 38 § 2. Sous-sol à plus de 2 m recevant plus de 100 personnes : effectif majoré (CO 39).", 19, TRAIT),
        ("Au-delà de 200 personnes, dégagements normaux de 2 UP au moins (CO 36 § 3).", 19, TRAIT),
    ])
    return s
