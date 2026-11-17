"""Code du travail R. 4216-5 à R. 4216-13 — Dégagements des lieux de travail (maître d'ouvrage)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "CDT_R4216-8_degagements",
    "titre": "Lieux de travail : dégagements",
    "articles": ["CDT:R4216-8", "CDT:R4216-5", "CDT:R4216-11", "CDT:R4216-9", "CDT:R4216-13"],
    "fiche": "",
    "legende": "Moins de 20 personnes : 1 dégagement. 20 à 50 : 1 + accessoire (ou 1 de 2 UP). 51 à 100 : 2 ou 1 + accessoire, 2 UP. Au-delà : 2 dégagements jusqu'à 500 (+1 par 500), UP selon le tableau. Escalier à 40 m au plus, débouché à moins de 20 m d'une sortie, cul-de-sac de 10 m au plus.",
    "ecarts": ["Planche ajoutée : l'ancien recueil ne traitait pas le code du travail. En rénovation dans un immeuble existant, 0,90 m peut être ramené à 0,80 m."],
}

ROUGE = "#C1121F"
VERT = "#15803D"


def dessiner():
    s = Scene(1600, 1160)
    s.cartouche("Lieux de travail : dégagements", "Règles du maître d'ouvrage — code du travail", "R. 4216-5 à R. 4216-13")
    x0, y0 = 40, 110
    rows = [("Effectif", "Dégagements", "Unités de passage"), ("moins de 20", "1", "1"), ("20 à 50", "1 + 1 accessoire  ou  1 (*)", "1  ou  2"),
            ("51 à 100", "2  ou  1 + 1 accessoire", "2"), ("101 à 200", "2", "3"), ("201 à 300", "2", "4"), ("301 à 400", "2", "5"), ("401 à 500", "2", "6"),
            ("au-delà", "+1 par 500 ou fraction", "1 UP par 100 ou fraction")]
    cw = [220, 340, 260]
    for i, r in enumerate(rows):
        y = y0 + i * 58
        s.items.append(f'<rect x="{x0}" y="{y}" width="{sum(cw)}" height="58" fill="{"#1F2A37" if i == 0 else ("#F7F8FA" if i % 2 else "#FFFFFF")}" stroke="#E5E7EB"/>')
        xx = x0
        for j, c in enumerate(r):
            s.texte(xx + 16, y + 36, c, 17 if i else 16, "#FFFFFF" if i == 0 else (TRAIT if j == 0 else ROUGE if j == 2 else TRAIT), gras=(i == 0 or j == 0))
            xx += cw[j]
    s.texte(x0, y0 + 9 * 58 + 30, "(*) si le parcours vers l'extérieur ne dépasse pas 25 m et hors sous-sol.", 15, "#4B5563")
    s.texte(x0, y0 + 9 * 58 + 54, "UP : 0,60 m ; 1 UP = 0,90 m, 2 UP = 1,40 m. Accessoire : 0,60 m au moins (sortie, escalier, coursive…).", 15, "#4B5563")
    # schéma distances
    k = 7.5
    ox, oy = 940, 160
    s.items.append(f'<rect x="{ox}" y="{oy}" width="{80 * k}" height="{50 * k}" fill="{SOL_INT}" stroke="{TRAIT}" stroke-width="3"/>')
    s.items.append(f'<rect x="{ox + 70 * k}" y="{oy}" width="{10 * k}" height="{12 * k}" fill="#D6E6F7" stroke="{TRAIT}" stroke-width="2.4"/>')
    s.texte(ox + 75 * k, oy + 6 * k + 6, "esc.", 14, "#1D4ED8", gras=True, ancre="middle")
    s.items.append(f'<rect x="{ox}" y="{oy + 38 * k}" width="{20 * k}" height="{12 * k}" fill="#FCE7C8" stroke="{TRAIT}" stroke-width="2"/>')
    pts = [(ox + 5 * k, oy + 30 * k), (ox + 40 * k, oy + 30 * k), (ox + 40 * k, oy + 6 * k), (ox + 70 * k, oy + 6 * k)]
    mid = f"q{len(s.defs)}"; s.defs.append(f'<marker id="{mid}" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="4" markerHeight="4" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{VERT}"/></marker>')
    s.items.append(f'<polyline points="{" ".join(f"{a},{b}" for a, b in pts)}" fill="none" stroke="{VERT}" stroke-width="5" stroke-dasharray="12 7" marker-end="url(#{mid})"/>')
    s.items.append(f'<circle cx="{pts[0][0]}" cy="{pts[0][1]}" r="8" fill="{ROUGE}"/>')
    s.etiquette(ox + 40 * k, oy + 20 * k, "≤ 40 m jusqu'à l'escalier\n(étage, sous-sol)", VERT, 17)
    s.items.append(f'<line x1="{ox + 10 * k}" y1="{oy + 38 * k}" x2="{ox + 10 * k}" y2="{oy + 48 * k}" stroke="{ROUGE}" stroke-width="3"/>')
    s.etiquette(ox + 34 * k, oy + 44 * k, "cul-de-sac ≤ 10 m", "#B45309", 16)
    s.texte(ox, oy + 50 * k + 34, "Au rez-de-chaussée : débouché de l'escalier à moins de 20 m d'une sortie.", 16, TRAIT)
    s.texte(ox, oy + 50 * k + 60, "Sous-sol > 100 pers. : effectif arrondi à la centaine, + 10 % par mètre", 16, TRAIT)
    s.texte(ox, oy + 50 * k + 84, "au-delà de 2 m de profondeur (R. 4216-9).", 16, TRAIT)
    s.texte(ox, oy + 50 * k + 120, "Désenfumage : locaux > 300 m² (rdc, étage), > 100 m² aveugles", 16, TRAIT)
    s.texte(ox, oy + 50 * k + 144, "ou en sous-sol, et tous les escaliers (R. 4216-13).", 16, TRAIT)
    s.bandeau([
        ("Ces règles s'imposent au maître d'ouvrage qui construit ou aménage des lieux de travail (articles R. 4216-1 et suivants).", 18, TRAIT),
        ("Aucune saillie ni dépôt ne doit réduire la largeur réglementaire ; aménagements fixes admis jusqu'à 1,10 m s'ils dépassent de 0,10 m au plus.", 18, TRAIT),
        ("Bâtiment dont le dernier niveau est à plus de 8 m : structure SF 1 h, planchers CF 1 h, isolement des tiers CF 1 h (R. 4216-24).", 18, TRAIT),
    ])
    return s
