"""CO 43 — Répartition des sorties et distances maximales au rez-de-chaussée."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "CO43_distances-rdc",
    "titre": "Distances à parcourir au rez-de-chaussée",
    "articles": ["ERP:CO 43"],
    "fiche": "C.15",
    "legende": "Au rez-de-chaussée, de tout point d'un local jusqu'à une sortie sur l'extérieur ou un dégagement protégé : 50 m au plus s'il y a le choix entre plusieurs sorties, 30 m sinon. Deux portes distantes de moins de 5 m comptent pour un seul dégagement.",
    "ecarts": [
        "La règle des 5 m entre portes (CO 43 § 3) a été ajoutée au règlement ; elle ne figurait pas sur l'ancienne fiche.",
    ],
}

ROUGE = "#C1121F"
VERT = "#15803D"


def sortie(s, x, y, z=0, axe="x"):
    if axe == "x":
        s.poly([(x - 0.8, y, z), (x + 0.8, y, z), (x + 0.8, y, z + 2.1), (x - 0.8, y, z + 2.1)], "#3F8F5A", ep=1.6)
    else:
        s.poly([(x, y - 0.8, z), (x, y + 0.8, z), (x, y + 0.8, z + 2.1), (x, y - 0.8, z + 2.1)], "#2F7A4B", ep=1.6)


def dessiner():
    s = Scene(1600, 1160, echelle=14, origine=(500, 220))
    s.cartouche("Distances à parcourir au rez-de-chaussée", "Répartition des sorties — ERP", "CO 43")
    L, P, h = 60, 34, 0.8
    s.sol(-3, -3, L + 6, P + 8, VERT_GAZON, trait=None)
    s.sol(0, 0, L, P, SOL_INT, ep=1.4)
    s.sol(40, 0, 20, 14, "#FCE7C8", ep=1.2)                      # partie sans choix de sortie
    v = [mur(0, 0, L, 0, h), mur(0, 0, 0, P, h), mur(L, 0, L, 14, h), mur(L, 15.6, L, P, h)]
    v += [mur(0, P, 12, P, h), mur(13.6, P, 46, P, h), mur(47.6, P, L, P, h)]
    v += [mur(40, 0, 40, 6, h), mur(40, 8, 40, 14, h), mur(40, 14, L, 14, h)]
    s.volumes(v)
    sortie(s, 12.8, P); sortie(s, 46.8, P); sortie(s, L, 14.8, axe="y")
    # points les plus défavorables
    s.chemin([(4, 4, 0.1), (4, 28, 0.1), (12.8, 28, 0.1), (12.8, P + 1, 0.1)], VERT, 4.5, "12 7")
    s.chemin([(56, 3, 0.1), (42, 3, 0.1), (42, 7, 0.1), (38, 7, 0.1), (38, 24, 0.1), (46.8, 24, 0.1), (46.8, P + 1, 0.1)], "#B45309", 4.5, "12 7")
    for pt in [(4, 4), (56, 3)]:
        u, v_ = s.p(*pt, 0); s.items.append(f'<circle cx="{u:.1f}" cy="{v_:.1f}" r="7" fill="{ROUGE}" stroke="{TRAIT}" stroke-width="1.6"/>')
    u, v_ = s.p(4, 16, 0); s.etiquette(u - 120, v_, "≤ 50 m\nchoix entre\nplusieurs sorties", VERT, 18)
    u, v_ = s.p(38, 16, 0); s.etiquette(u + 160, v_ + 30, "≤ 30 m\npas de choix\n(partie en cul-de-sac)", "#B45309", 18)
    s.repere((L, 14.8, 1.2), "sortie unique\nde cette partie", du=170, dv=-110, couleur="#2F7A4B", taille=17)

    # encart règle des 5 m
    x0, y0 = 1070, 770
    s.items.append(f'<rect x="{x0}" y="{y0}" width="500" height="250" rx="10" fill="#FFFFFF" stroke="#9CA3AF" stroke-width="1.5"/>')
    s.texte(x0 + 20, y0 + 34, "Portes à moins de 5 m l'une de l'autre", 18, TRAIT, gras=True)
    yb = y0 + 120
    s.items.append(f'<line x1="{x0 + 40}" y1="{yb}" x2="{x0 + 460}" y2="{yb}" stroke="{TRAIT}" stroke-width="8"/>')
    for xd in (x0 + 140, x0 + 300):
        s.items.append(f'<line x1="{xd}" y1="{yb}" x2="{xd + 60}" y2="{yb}" stroke="#FFFFFF" stroke-width="10"/>')
        s.items.append(f'<path d="M{xd},{yb} L{xd},{yb - 60} A60,60 0 0 1 {xd + 60},{yb}" fill="none" stroke="{VERT}" stroke-width="2.4"/>')
    s.items.append(f'<line x1="{x0 + 200}" y1="{yb + 26}" x2="{x0 + 300}" y2="{yb + 26}" stroke="{ROUGE}" stroke-width="2.4"/>')
    s.texte(x0 + 250, yb + 52, "< 5 m", 18, ROUGE, gras=True, ancre="middle")
    s.texte(x0 + 20, y0 + 210, "= un seul dégagement totalisant leurs UP", 17, TRAIT)
    s.texte(x0 + 20, y0 + 234, "(locaux de plus de 10 m de dimension)", 15, "#4B5563")

    s.bandeau([
        ("Distance mesurée suivant l'axe des circulations, de tout point d'un local jusqu'à une sortie sur l'extérieur ou un dégagement protégé", 18, TRAIT),
        ("menant à l'extérieur dont toutes les portes intérieures ont un ferme-porte : 50 m au plus si le choix existe entre plusieurs sorties, 30 m sinon.", 18, TRAIT),
        ("Sorties judicieusement réparties pour ne pas être soumises en même temps aux effets d'un sinistre.", 18, TRAIT),
    ])
    return s
