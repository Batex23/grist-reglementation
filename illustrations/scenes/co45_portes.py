"""CO 44 à CO 48 — Portes : sens d'ouverture, saillie, va-et-vient, cul-de-sac."""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "CO45_portes",
    "titre": "Manœuvre des portes",
    "articles": ["ERP:CO 45", "ERP:CO 44", "ERP:CO 46", "ERP:CO 47", "ERP:CO 48"],
    "fiche": "C.15",
    "legende": "Portes des locaux de plus de 50 personnes et des escaliers dans le sens de l'évacuation ; aucune saillie dans le dégagement ; portes de recoupement utilisées dans les deux sens en va-et-vient, vitrées à hauteur de vue ; locaux en cul-de-sac signalés « sans issue ».",
    "ecarts": [
        "Verrouillage des issues de secours (CO 46) : dispositif électromagnétique, déverrouillage par boîtier à bris de glace ou dispositif de contrôle d'issues (T1 ≤ 8 s, T2 ≤ 3 min avec service de sécurité), et par le SSI (MS 60).",
        "Portes coupe-feu maintenues ouvertes : fermeture automatique conforme à la norme, plaque « Porte coupe-feu — ne mettez pas d'obstacle à la fermeture » (CO 47).",
    ],
}

ROUGE = "#C1121F"
VERT = "#15803D"
MURC = "#3F3F46"


def panneau(s, x0, y0, titre, ok):
    s.items.append(f'<rect x="{x0}" y="{y0}" width="740" height="400" rx="12" fill="#FFFFFF" stroke="#D1D5DB" stroke-width="1.5"/>')
    s.texte(x0 + 24, y0 + 38, titre, 20, TRAIT, gras=True)


def mur2d(s, x1, y1, x2, y2, ep=12):
    s.items.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{MURC}" stroke-width="{ep}" stroke-linecap="butt"/>')


def porte2d(s, hx, hy, r, a0, a1, couleur=VERT, sens=1):
    ex, ey = hx + r * math.cos(math.radians(a1)), hy + r * math.sin(math.radians(a1))
    sx, sy = hx + r * math.cos(math.radians(a0)), hy + r * math.sin(math.radians(a0))
    large = 0
    sweep = 1 if (a1 - a0) % 360 < 180 else 0
    s.items.append(f'<line x1="{hx}" y1="{hy}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{couleur}" stroke-width="5" stroke-linecap="round"/>')
    s.items.append(f'<path d="M{sx:.1f},{sy:.1f} A{r},{r} 0 {large} {sweep} {ex:.1f},{ey:.1f}" fill="none" stroke="{couleur}" stroke-width="2" stroke-dasharray="7 5"/>')


def fleche2d(s, x1, y1, x2, y2, c=VERT):
    mid = f"f{len(s.defs)}"
    s.defs.append(f'<marker id="{mid}" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="4" markerHeight="4" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>')
    s.items.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="6" marker-end="url(#{mid})"/>')


def croix(s, x, y):
    s.items.append(f'<circle cx="{x}" cy="{y}" r="22" fill="{ROUGE}"/><path d="M{x - 10},{y - 10} L{x + 10},{y + 10} M{x + 10},{y - 10} L{x - 10},{y + 10}" stroke="#fff" stroke-width="5" stroke-linecap="round"/>')


def coche(s, x, y):
    s.items.append(f'<circle cx="{x}" cy="{y}" r="22" fill="{VERT}"/><path d="M{x - 11},{y} L{x - 3},{y + 9} L{x + 12},{y - 9}" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>')


def dessiner():
    s = Scene(1600, 1160)
    s.cartouche("Manœuvre des portes", "Sens d'ouverture et disposition des portes — ERP", "CO 44 à CO 48")
    # 1 — sens de la sortie
    x0, y0 = 40, 110
    panneau(s, x0, y0, "Plus de 50 personnes : ouverture dans le sens de la sortie", True)
    mur2d(s, x0 + 60, y0 + 240, x0 + 300, y0 + 240); mur2d(s, x0 + 400, y0 + 240, x0 + 680, y0 + 240)
    porte2d(s, x0 + 300, y0 + 240, 100, 0, 90)
    s.texte(x0 + 80, y0 + 140, "Local > 50 personnes", 17, "#4B5563")
    s.texte(x0 + 80, y0 + 370, "Dégagement / extérieur", 17, "#4B5563")
    fleche2d(s, x0 + 560, y0 + 120, x0 + 560, y0 + 330)
    coche(s, x0 + 670, y0 + 90)
    s.texte(x0 + 420, y0 + 380, "toutes les portes d'escalier aussi", 15, "#4B5563")
    # 2 — pas de saillie dans le dégagement
    x0 = 820
    panneau(s, x0, y0, "Aucune saillie de la porte dans le dégagement", True)
    s.items.append(f'<rect x="{x0 + 40}" y="{y0 + 250}" width="660" height="90" fill="#E9F3EA"/>')
    mur2d(s, x0 + 40, y0 + 250, x0 + 180, y0 + 250); mur2d(s, x0 + 280, y0 + 250, x0 + 400, y0 + 250)
    mur2d(s, x0 + 400, y0 + 250, x0 + 520, y0 + 250); mur2d(s, x0 + 620, y0 + 250, x0 + 700, y0 + 250)
    mur2d(s, x0 + 40, y0 + 340, x0 + 700, y0 + 340)
    porte2d(s, x0 + 180, y0 + 250, 95, 0, 90, ROUGE)              # saillie : interdit
    croix(s, x0 + 230, y0 + 380 - 10)
    mur2d(s, x0 + 520, y0 + 250, x0 + 520, y0 + 160); mur2d(s, x0 + 620, y0 + 250, x0 + 620, y0 + 160)
    porte2d(s, x0 + 520, y0 + 160, 98, 0, -90 + 360, VERT)          # porte en retrait : admis
    s.items.append(f'<line x1="{x0 + 520}" y1="{y0 + 160}" x2="{x0 + 618}" y2="{y0 + 160}" stroke="{VERT}" stroke-width="5"/>')
    coche(s, x0 + 570, y0 + 380 - 10)
    s.texte(x0 + 330, y0 + 298, "dégagement", 16, "#15803D", ancre="middle")
    s.texte(x0 + 24, y0 + 66, "sauf porte se développant jusqu'à la paroi ou placée en retrait", 15, "#4B5563")
    # 3 — va-et-vient
    x0, y0 = 40, 540
    panneau(s, x0, y0, "Recoupement utilisé dans les deux sens : va-et-vient", True)
    s.items.append(f'<rect x="{x0 + 40}" y="{y0 + 170}" width="660" height="130" fill="#E9F3EA"/>')
    mur2d(s, x0 + 40, y0 + 170, x0 + 700, y0 + 170); mur2d(s, x0 + 40, y0 + 300, x0 + 700, y0 + 300)
    mur2d(s, x0 + 370, y0 + 170, x0 + 370, y0 + 178, 12)
    for (hy, a1) in ((y0 + 172, 50), (y0 + 298, -50)):
        porte2d(s, x0 + 370, hy, 64, 90 if hy < y0 + 200 else -90, a1, "#B45309")
        porte2d(s, x0 + 370, hy, 64, 90 if hy < y0 + 200 else -90, 180 - a1 if hy < y0 + 200 else -180 - a1, "#B45309")
    fleche2d(s, x0 + 120, y0 + 236, x0 + 280, y0 + 236); fleche2d(s, x0 + 620, y0 + 236, x0 + 460, y0 + 236)
    s.texte(x0 + 24, y0 + 340, "Partie vitrée à hauteur de vue, vitrage transparent (ni rouge ni orange).", 16, TRAIT)
    s.texte(x0 + 24, y0 + 366, "Largeur offerte : celle de CO 36 et CO 38, tolérance - 5 %.", 16, TRAIT)
    # 4 — cul-de-sac
    x0 = 820
    panneau(s, x0, y0, "Local en cul-de-sac confondable avec une issue", True)
    s.items.append(f'<rect x="{x0 + 40}" y="{y0 + 250}" width="660" height="90" fill="#E9F3EA"/>')
    mur2d(s, x0 + 40, y0 + 250, x0 + 300, y0 + 250); mur2d(s, x0 + 400, y0 + 250, x0 + 700, y0 + 250)
    mur2d(s, x0 + 40, y0 + 340, x0 + 700, y0 + 340)
    porte2d(s, x0 + 300, y0 + 250, 100, 0, -90)
    s.texte(x0 + 150, y0 + 150, "Local en cul-de-sac", 17, "#4B5563")
    s.items.append(f'<rect x="{x0 + 450}" y="{y0 + 120}" width="200" height="60" rx="6" fill="#FFFFFF" stroke="{TRAIT}" stroke-width="2.4"/>')
    s.texte(x0 + 550, y0 + 160, "SANS ISSUE", 22, TRAIT, gras=True, ancre="middle")
    s.texte(x0 + 24, y0 + 380, "Porte débattant vers l'extérieur du local ; inscription non lumineuse, couleur verte interdite.", 15, TRAIT)
    s.bandeau([
        ("Portes ouvrables de l'intérieur par simple poussée ou un seul dispositif facile par vantail (barre anti-panique conforme aux normes).", 18, TRAIT),
        ("Tambours non automatiques et tourniquets : pas des sorties normales, doublés par une porte d'1 UP « Sortie de secours » (CO 48).", 18, TRAIT),
        ("Portes automatiques : en cas de coupure, ouverture totale par poussée vers l'extérieur (≥ 90°) ou effacement latéral ; coulissantes", 18, TRAIT),
        ("non motorisées interdites sur les issues d'évacuation du public.", 18, TRAIT),
    ])
    return s
