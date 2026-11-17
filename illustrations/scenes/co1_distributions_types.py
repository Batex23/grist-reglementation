"""Distributions intérieures autorisées selon le type (CO 1 § 2 et dispositions particulières)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

TYPES = [
    ("J", "oui", "non", "600 m²", "zones sans locaux à sommeil ; 1 seul par niveau s'il est associé à une zone en cloisonnement traditionnel", "J 10 · J 11"),
    ("L", "oui", "a, b, e, f", "1 200 m²", "secteurs et compartiments pour les salles visées en L 1 § 1 a, b, e, f seulement", "L 6"),
    ("M", "oui", "non", "non", "CO 5 et CO 25 non applicables ; parois entre exploitations des centres commerciaux CF (M 7)", "M 3"),
    ("N", "oui", "oui", "non", "", "N 3"),
    ("O", "oui", "oui", "non", "secteurs : baies accessibles ouvrant sur une circulation horizontale ouverte au public", "O 3"),
    ("P", "oui", "non", "non", "CO 15 non applicable aux salles de danse", "P 4"),
    ("R", "oui", "oui", "600 m²", "issues à 30 m au plus ; interdits si locaux à risques importants au niveau ou sommeil dans le bâtiment ; 1 seul si niveau ≤ 600 m²", "R 6"),
    ("S", "oui", "oui", "1 200 m²", "issues à 30 m au plus ; 1 seul compartiment si le niveau fait 800 m² au plus", "S 3"),
    ("T", "oui", "non", "non", "", "T 10"),
    ("U", "oui", "non", "1 000 m²", "zones protégées et de mise à l'abri ; compartiments sans sommeil ou avec surveillance permanente, sur un seul niveau sauf halls", "U 10"),
    ("V", "oui", "non", "non", "aucune disposition particulière ne les autorise", "CO 1 § 2"),
    ("W", "oui", "oui", "800 m²", "", "W 3"),
    ("X", "oui", "oui", "1 600 m²", "", "X 4"),
    ("Y", "oui", "oui", "1 200 m²", "issues à 30 m au plus ; 1 seul compartiment si le niveau fait 1 200 m² au plus", "Y 3"),
]

META = {
    "id": "CO1_distributions-par-type",
    "titre": "Distributions intérieures autorisées par type",
    "articles": ["ERP:CO 1", "ERP:CO 24", "ERP:CO 25", "ERP:J 11", "ERP:L 6", "ERP:M 3", "ERP:N 3", "ERP:O 3", "ERP:P 4", "ERP:R 6",
                 "ERP:S 3", "ERP:T 10", "ERP:U 10", "ERP:W 3", "ERP:X 4", "ERP:Y 3"],
    "fiche": "",
    "legende": "Le cloisonnement traditionnel est toujours possible ; secteurs et compartiments seulement si les dispositions particulières du type les autorisent (CO 1 § 2). Surface maximale d'un compartiment : J 600 m², L 1 200 m², R 600 m², S 1 200 m², U 1 000 m², W 800 m², X 1 600 m², Y 1 200 m².",
    "ecarts": [
        "Type M : la référence est M 3 (CO 5 et CO 25 non applicables), M 7 traitant des parois entre exploitations des centres commerciaux.",
        "Type J : secteurs non prévus ; cloisonnement traditionnel et compartiment peuvent être associés sur un même niveau, pas dans une même zone (J 10).",
    ],
}

ROUGE = "#C1121F"
VERT = "#15803D"


def case(s, x, y, w, val):
    oui = val not in ("non",)
    fond = "#DCFCE7" if oui else "#FEE2E2"
    coul = VERT if oui else ROUGE
    s.items.append(f'<rect x="{x + 6}" y="{y + 9}" width="{w - 12}" height="36" rx="18" fill="{fond}" stroke="{coul}" stroke-width="1.8"/>')
    lab = "OUI" if val == "oui" else "NON" if val == "non" else val
    s.texte(x + w / 2, y + 33, lab, 17 if len(lab) < 9 else 15, coul, gras=True, ancre="middle")


def dessiner():
    s = Scene(1600, 1160)
    s.cartouche("Distributions intérieures autorisées", "Cloisonnement traditionnel, secteurs, compartiments selon le type d'ERP (1er groupe)", "CO 1 § 2 · CO 24 · CO 25")
    x0, y0, rh = 40, 104, 55
    cols = [(x0, 70, "Type"), (x0 + 70, 170, "Traditionnel\nCO 24"), (x0 + 240, 170, "Secteurs\nCO 5, CO 24 § 2"), (x0 + 410, 180, "Compartiments\nCO 25 (S max)"), (x0 + 590, 820, "Conditions"), (x0 + 1410, 110, "Article")]
    s.items.append(f'<rect x="{x0}" y="{y0}" width="1520" height="56" rx="8" fill="#1F2A37"/>')
    for cx, w, t in cols:
        for j, l in enumerate(t.split("\n")):
            s.texte(cx + (w / 2 if cx > x0 + 500 and cx < x0 + 1400 else w / 2) if False else cx + 14, y0 + 24 + j * 20, l, 16 if j == 0 else 13, "#FFFFFF" if j == 0 else "#CBD5E1", gras=(j == 0))
    y = y0 + 60
    for i, (t, tr, se, co, cond, ref) in enumerate(TYPES):
        s.items.append(f'<rect x="{x0}" y="{y}" width="1520" height="{rh}" fill="{"#FFFFFF" if i % 2 else "#F7F8FA"}" stroke="#E5E7EB"/>')
        s.items.append(f'<rect x="{x0 + 10}" y="{y + 8}" width="48" height="40" rx="3" fill="{ROUGE}"/>')
        s.texte(x0 + 34, y + 38, t, 26, "#FFFFFF", gras=True, ancre="middle")
        case(s, cols[1][0], y, cols[1][1], tr)
        case(s, cols[2][0], y, cols[2][1], se)
        case(s, cols[3][0], y, cols[3][1], co)
        mots = cond.split(" "); l1, l2 = "", ""
        for m in mots:
            if len(l1) + len(m) < 92 and not l2:
                l1 += (" " if l1 else "") + m
            else:
                l2 += (" " if l2 else "") + m
        s.texte(cols[4][0] + 14, y + (25 if l2 else 34), l1, 14.5, "#374151")
        if l2:
            s.texte(cols[4][0] + 14, y + 45, l2, 14.5, "#374151")
        s.texte(cols[5][0] + 14, y + 34, ref, 15, TRAIT, gras=True)
        y += rh
    s.bandeau([
        ("Compartiment : au moins deux par niveau de capacité comparable, parois CF du degré de stabilité exigé pour la structure (CO 25).", 18, TRAIT),
        ("Secteurs : autant que d'escaliers normaux, desservis par des espaces libres, isolés par des parois CF 1 h (CO 5, CO 24 § 2).", 18, TRAIT),
        ("Types PA, CTS, SG, OA, REF, PS, GA : règles propres du livre IV (PS : compartiments de parcs, PS 12).", 18, TRAIT),
    ])
    return s
