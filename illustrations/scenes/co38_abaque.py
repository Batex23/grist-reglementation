"""CO 38 — Abaque : nombre de dégagements et d'unités de passage selon l'effectif."""
import math
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "CO38_abaque-degagements",
    "titre": "Abaque des dégagements (1er groupe)",
    "articles": ["ERP:CO 38", "ERP:CO 36"],
    "fiche": "",
    "legende": "Nombre de dégagements et nombre total d'unités de passage selon l'effectif, de 1 à 2 500 personnes. Jusqu'à 500 personnes : 2 dégagements, 1 UP par 100 personnes ou fraction, majoré d'1 UP. Au-delà : 1 dégagement de plus par 500 personnes ou fraction, 1 UP par 100 personnes ou fraction.",
    "ecarts": [
        "Au-delà de 200 personnes, chaque dégagement normal a au moins 2 UP ; un dégagement d'1 UP reste admis s'il n'est compté qu'une fois, soit dans le nombre de dégagements, soit dans le nombre d'UP (CO 36 § 3).",
        "Effectif à prendre pour les escaliers : niveau desservi et niveaux au-dessus (étages) ou au-dessous (sous-sols), CO 38 § 2.",
    ],
}

ROUGE = "#C1121F"
NOIR = "#1F2A37"


def calcul(n):
    if n <= 19:
        return 1, 1, "1"
    if n <= 50:
        return 1, 1, "1 + a"
    if n <= 100:
        return 2, 2, "2"
    if n <= 500:
        return 2, math.ceil(n / 100) + 1, "2"
    d = 2 + math.ceil((n - 500) / 500)
    return d, math.ceil(n / 100), str(d)


def barre(s, x, base, w, h, faces, ep=1.4):
    dx, dy = 9, 6
    s.items.append(f'<polygon points="{x},{base} {x},{base - h} {x + w},{base - h} {x + w},{base}" fill="{faces[1]}" stroke="{TRAIT}" stroke-width="{ep}" stroke-linejoin="round"/>')
    s.items.append(f'<polygon points="{x},{base - h} {x + dx},{base - h - dy} {x + w + dx},{base - h - dy} {x + w},{base - h}" fill="{faces[0]}" stroke="{TRAIT}" stroke-width="{ep}" stroke-linejoin="round"/>')
    s.items.append(f'<polygon points="{x + w},{base} {x + w},{base - h} {x + w + dx},{base - h - dy} {x + w + dx},{base - dy}" fill="{faces[2]}" stroke="{TRAIT}" stroke-width="{ep}" stroke-linejoin="round"/>')


def dessiner():
    s = Scene(1600, 1160)
    s.cartouche("Abaque des dégagements", "Nombre de dégagements et d'unités de passage (UP) selon l'effectif — ERP du 1er groupe", "CO 36 · CO 38")
    seuils = [1, 20, 51, 101, 201, 301, 401, 501, 601, 701, 801, 901, 1001, 1101, 1201, 1301, 1401, 1501, 1601, 1701, 1801, 1901, 2001]
    x0, base, k = 110, 640, 19
    pas = 62
    # grille
    for v in range(0, 26, 5):
        y = base - v * k
        s.items.append(f'<line x1="{x0 - 20}" y1="{y:.1f}" x2="{x0 + pas * len(seuils)}" y2="{y:.1f}" stroke="#E5E7EB" stroke-width="1.2"/>')
        s.texte(x0 - 28, y + 6, str(v), 16, "#6B7280", ancre="end")
    s.items.append(f'<line x1="{x0 - 20}" y1="{base}" x2="{x0 + pas * len(seuils)}" y2="{base}" stroke="{TRAIT}" stroke-width="2"/>')
    # zones
    zones = [(0, 3, "≤ 100", "#F3F4F6"), (3, 7, "101 à 500 : UP + 1", "#FEF2F2"), (7, len(seuils), "plus de 500 : + 1 dégagement par 500, 1 UP par 100", "#F1F5F9")]
    for a, b, t, f in zones:
        s.items.append(f'<rect x="{x0 + a * pas - 8}" y="{base - 25 * k - 40}" width="{(b - a) * pas}" height="{25 * k + 40}" fill="{f}" fill-opacity="0.7"/>')
        s.texte(x0 + a * pas + 2, base - 25 * k - 16, t, 15, "#374151", gras=True)
    for i, n in enumerate(seuils):
        d, up, lab = calcul(n)
        x = x0 + i * pas
        barre(s, x, base, 20, d * k, ("#9FB4D9", "#6E8FC6", "#4A6BA5"))
        barre(s, x + 24, base, 20, up * k, ("#F6B3AE", "#E5534B", "#B42318"))
        s.texte(x + 10, base - d * k - 12, lab, 13, "#2B4A80", gras=True, ancre="middle")
        s.texte(x + 34, base - up * k - 12, str(up), 14, ROUGE, gras=True, ancre="middle")
        s.texte(x + 22, base + 26, f"{n:,}".replace(",", " "), 14, TRAIT, gras=True, ancre="middle")
    s.texte(x0 + pas * len(seuils) / 2, base + 56, "effectif (personnes, début de chaque tranche)", 16, "#4B5563", ancre="middle")
    s.items.append(f'<text x="44" y="{base - 12 * k}" transform="rotate(-90 44 {base - 12 * k})" text-anchor="middle" font-family="Inter, DejaVu Sans, sans-serif" font-size="16" fill="#4B5563">nombre</text>')
    s.legende(130, 190, [("#6E8FC6", "nombre de dégagements (a = accessoire)"), ("#E5534B", "nombre total d'unités de passage")], taille=16)
    # encarts
    y = 740
    boxes = [
        ("1 à 19", "1 dégagement de 1 UP"),
        ("20 à 50", "1 UP + 1 accessoire\n(escalier 1 UP + accessoire\nsi étage > 8 m ou sous-sol)"),
        ("51 à 100", "2 × 1 UP\nou 1 × 2 UP + accessoire"),
        ("101 à 500", "2 dégagements\nUP = centaines arrondies + 1\n234 → 3 + 1 = 4 UP"),
        ("plus de 500", "2 + 1 par 500 ou fraction\nUP = centaines arrondies\n1 234 → 4 dégagements, 13 UP"),
    ]
    bw = 296
    for i, (t, txt) in enumerate(boxes):
        x = 40 + i * (bw + 10)
        s.items.append(f'<rect x="{x}" y="{y}" width="{bw}" height="150" rx="10" fill="#FFFFFF" stroke="#9CA3AF" stroke-width="1.5"/>')
        s.items.append(f'<rect x="{x}" y="{y}" width="{bw}" height="38" rx="10" fill="{NOIR}"/>')
        s.items.append(f'<rect x="{x}" y="{y + 28}" width="{bw}" height="10" fill="{NOIR}"/>')
        s.texte(x + 16, y + 26, t + " personnes", 17, "#FFFFFF", gras=True)
        for j, l in enumerate(txt.split("\n")):
            s.texte(x + 16, y + 68 + j * 25, l, 16, ROUGE if j == 0 else TRAIT, gras=(j == 0))
    s.bandeau([
        ("Plus de 200 personnes : dégagements normaux de 2 UP au moins ; un dégagement d'1 UP est admis s'il n'est compté qu'une seule fois,", 18, TRAIT),
        ("soit dans le nombre de dégagements, soit dans le nombre d'UP (CO 36 § 3). 1 UP = 0,90 m, 2 UP = 1,40 m, puis 0,60 m par UP (CO 36 § 2).", 18, TRAIT),
        ("Escaliers : effectif du niveau desservi cumulé avec celui des niveaux au-dessus (étages) ou au-dessous (sous-sols), CO 38 § 2.", 18, TRAIT),
    ])
    return s
