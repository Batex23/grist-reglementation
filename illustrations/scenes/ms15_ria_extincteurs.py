"""MS 14 à MS 16, MS 38, MS 39 — RIA et extincteurs."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "MS39_ria-extincteurs",
    "titre": "RIA et extincteurs",
    "articles": ["ERP:MS 39", "ERP:MS 38", "ERP:MS 14", "ERP:MS 15", "ERP:MS 16"],
    "fiche": "MS 2-2 · MS 2-5",
    "legende": "Extincteurs : 1 pour 200 m² et par niveau (2 au moins par établissement), eau pulvérisée de 6 L au moins, rouges, accrochés poignée à 1,20 m au plus, dans les dégagements. RIA (DN 19/6, 25/8, 33/12) numérotés, à l'extérieur et près des locaux à protéger ; locaux à risques importants battus par deux jets.",
    "ecarts": [
        "La règle actuelle est d'un extincteur pour 200 m² et par niveau (MS 39) ; l'ancienne fiche citait la norme APSAD (1 pour 150 m² en industriel, 250 m² en tertiaire, 10 m de distance maximale), qui n'est pas réglementaire en ERP.",
        "Classes de feu A, B, C, D et F (feux d'huiles de cuisson) marquées sur l'extincteur ; vérification annuelle et révision décennale, étiquette datée (MS 38).",
        "Diamètres des RIA : DN 19/6, 25/8 ou 33/12 (ancienne fiche : DN 19, 25 ou 40).",
    ],
}

ROUGE = "#C1121F"


def dessiner():
    s = Scene(1600, 1160, echelle=24, origine=(560, 240))
    s.cartouche("RIA et extincteurs", "Moyens de première intervention — ERP", "MS 14 à MS 16 · MS 38 · MS 39")
    h = 2.6
    L, P = 28, 18
    s.sol(-1, -1, L + 2, P + 2, "#E5E7EB", trait=None)
    s.sol(0, 0, L, P, SOL_INT, ep=1.4)
    s.sol(0, 7, L, 3, "#E9F3EA", ep=1.2)
    s.sol(0, 0, 9, 7, "#FCE3E1", ep=1.2)                                   # local à risques importants
    v = [dict(x=-0.25, y=0, z=0, dx=0.25, dy=P, dz=h, pal=MUR), dict(x=0, y=-0.25, z=0, dx=L, dy=0.25, dz=h, pal=MUR),
         dict(x=0, y=6.9, z=0, dx=4, dy=0.25, dz=h, pal=MUR_CF), dict(x=5.4, y=6.9, z=0, dx=3.6, dy=0.25, dz=h, pal=MUR_CF),
         dict(x=8.9, y=0, z=0, dx=0.25, dy=7, dz=h, pal=MUR_CF), dict(x=9, y=6.9, z=0, dx=19, dy=0.25, dz=1.2, pal=MUR),
         dict(x=0, y=10, z=0, dx=L, dy=0.25, dz=0.8, pal=MUR)]
    s.volumes(v)
    # RIA dans la circulation (deux, pour battre le local à risques)
    for x in (2.5, 12):
        s.boite(x - 0.5, 7.15, 0.9, 1.0, 0.35, 1.0, ("#F87171", "#EF4444", "#B91C1C"), ep=1.6)
        u, vv = s.p(x, 7.5, 1.4); s.items.append(f'<circle cx="{u:.1f}" cy="{vv:.1f}" r="11" fill="#FEE2E2" stroke="{TRAIT}" stroke-width="2"/>')
    for (x0, a) in ((2.5, 4.5), (12, 3.5)):
        s.chemin([(x0, 7.2, 0.9), (a, 3.5, 0.6)], "#2563EB", 3, "6 5")
    # extincteurs
    for (x, y) in [(6, 7.3), (18, 7.3), (24, 7.3), (20, 14)]:
        s.boite(x - 0.15, y, 0.6, 0.3, 0.3, 0.7, ("#F87171", "#EF4444", "#B91C1C"), ep=1.4)
    s.personne((15, 8.5, 0), 30, 5); s.personne((22, 14, 0), 30, 2, True)
    s.repere((12, 7.3, 1.9), "RIA numéroté, signalé, coffret\nsans condamnation, hors gel", du=260, dv=-150, couleur=ROUGE, taille=17)
    s.repere((4.5, 3.5, 0.6), "local à risques importants :\ntout point battu par 2 jets", du=-330, dv=60, couleur=ROUGE, taille=17)
    s.repere((24, 7.45, 1.3), "extincteurs dans les dégagements,\n1 pour 200 m² et par niveau,\npoignée à 1,20 m au plus", du=200, dv=60, couleur=ROUGE, taille=17)

    x0, y0 = 40, 720
    s.items.append(f'<rect x="{x0}" y="{y0}" width="760" height="230" rx="10" fill="#FFFFFF" stroke="#9CA3AF" stroke-width="1.5"/>')
    s.texte(x0 + 20, y0 + 34, "Classes de feu (marquage de l'extincteur)", 18, TRAIT, gras=True)
    rows = [("A", "solides (bois, papier, tissus…)"), ("B", "liquides ou solides liquéfiables"), ("C", "gaz"), ("D", "métaux"), ("F", "huiles et graisses de cuisson")]
    for i, (c, t) in enumerate(rows):
        yy = y0 + 64 + 32 * i
        s.items.append(f'<rect x="{x0 + 20}" y="{yy - 20}" width="34" height="26" rx="5" fill="{ROUGE}"/>')
        s.texte(x0 + 37, yy, c, 18, "#FFFFFF", gras=True, ancre="middle")
        s.texte(x0 + 70, yy, t, 16, TRAIT)
    s.texte(x0 + 420, y0 + 64, "Extincteur rouge, eau ≥ 6 L,", 16, TRAIT)
    s.texte(x0 + 420, y0 + 90, "efficacité attestée par essai,", 16, TRAIT)
    s.texte(x0 + 420, y0 + 116, "vérification annuelle,", 16, TRAIT)
    s.texte(x0 + 420, y0 + 142, "révision tous les 10 ans,", 16, TRAIT)
    s.texte(x0 + 420, y0 + 168, "plan d'implantation au registre.", 16, TRAIT)
    s.bandeau([
        ("RIA : composition et installation conformes aux normes (NF EN 671-1, NF S 62-201), alimentés par une canalisation en pression desservie", 18, TRAIT),
        ("par les conduites publiques (réservoirs exceptionnellement), placés à l'intérieur, au plus près et à l'extérieur des locaux à protéger.", 18, TRAIT),
        ("Extincteurs appropriés aux risques, notamment électriques ; deux au moins par établissement.", 18, TRAIT),
    ])
    return s
