"""CO 49 et CO 52 § 6 — Répartition des escaliers et distances maximales en étage et sous-sol."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "CO49_distances-etage",
    "titre": "Distances à parcourir en étage",
    "articles": ["ERP:CO 49", "ERP:CO 52"],
    "fiche": "C.15",
    "legende": "En étage et en sous-sol : 40 m au plus pour gagner un escalier protégé ou une circulation protégée (30 m depuis une partie en cul-de-sac), 30 m pour un escalier non protégé. Au rez-de-chaussée, débouché d'un escalier encloisonné à moins de 20 m d'une sortie.",
    "ecarts": [
        "Débouché au rez-de-chaussée d'un escalier non protégé : à moins de 50 m d'une sortie (30 m sans choix), CO 52 § 6.",
    ],
}

ROUGE = "#C1121F"
VERT = "#15803D"
BLEU = "#1D4ED8"


def cage(s, x, y, protege=True):
    s.sol(x, y, 4, 6, "#D6E6F7" if protege else "#FFFFFF", ep=1.2)
    for k in range(1, 9):
        s.ligne((x + 0.3, y + k * 0.62, 0), (x + 3.7, y + k * 0.62, 0), "#5B7DB1" if protege else "#9CA3AF", 1.2)


def dessiner():
    s = Scene(1600, 1160, echelle=15, origine=(560, 220))
    s.cartouche("Distances à parcourir en étage", "Répartition des escaliers en étage et en sous-sol — ERP", "CO 49")
    L, P, h = 60, 34, 0.8
    s.sol(-3, -3, L + 6, P + 6, "#E5E7EB", trait=None)
    s.sol(0, 0, L, P, SOL_INT, ep=1.4)
    s.sol(44, 0, 16, 16, "#FCE7C8", ep=1.2)                      # partie en cul-de-sac
    cage(s, 2, 26, True); cage(s, 30, 26, True); cage(s, 36, 2, False)
    v = [mur(0, 0, L, 0, h), mur(0, 0, 0, P, h), mur(L, 0, L, P, h), mur(0, P, L, P, h)]
    for x in (2, 30):
        v += [mur(x, 26, x, 32, h, ep=0.35, pal=MUR_BLEU), mur(x + 4, 26, x + 4, 32, h, ep=0.35, pal=MUR_BLEU), mur(x, 32, x + 4, 32, h, ep=0.35, pal=MUR_BLEU), mur(x, 26, x + 0.8, 26, h, ep=0.35, pal=MUR_BLEU), mur(x + 2.2, 26, x + 4, 26, h, ep=0.35, pal=MUR_BLEU)]
    v += [mur(44, 0, 44, 16, h), mur(44, 16, 50, 16, h), mur(52, 16, L, 16, h)]
    s.volumes(v)
    s.chemin([(8, 4, 0.1), (8, 22, 0.1), (3.5, 22, 0.1), (3.5, 25.6, 0.1)], BLEU, 4.5, "12 7")
    s.chemin([(56, 3, 0.1), (56, 18, 0.1), (51, 18, 0.1), (51, 22, 0.1), (33.5, 22, 0.1), (33.5, 25.6, 0.1)], "#B45309", 4.5, "12 7")
    s.chemin([(22, 4, 0.1), (36, 4, 0.1), (37.5, 4, 0.1)], "#4B5563", 4.5, "12 7")
    for pt in [(8, 4), (56, 3), (22, 4)]:
        u, v_ = s.p(*pt, 0); s.items.append(f'<circle cx="{u:.1f}" cy="{v_:.1f}" r="7" fill="{ROUGE}" stroke="{TRAIT}" stroke-width="1.6"/>')
    u, v_ = s.p(8, 13, 0); s.etiquette(u - 150, v_, "≤ 40 m\nvers un escalier protégé\n(portes à ferme-porte)", BLEU, 17)
    u, v_ = s.p(56, 10, 0); s.etiquette(u + 140, v_ + 20, "≤ 30 m\ndepuis une partie\nen cul-de-sac", "#B45309", 17)
    u, v_ = s.p(28, 4, 0); s.etiquette(u + 40, v_ - 70, "≤ 30 m vers un\nescalier non protégé", "#4B5563", 17)
    u, v_ = s.p(4, 29, 1.0); s.pastille(u - 10, v_ + 60, "escalier protégé", BLEU, taille=15)
    u, v_ = s.p(38, 5, 0); s.pastille(u + 60, v_ - 20, "escalier non protégé", "#4B5563", taille=15)
    s.legende(40, 860, [("#D6E6F7", "escalier protégé (encloisonné ou à l'air libre)"), ("#FCE7C8", "partie de l'établissement formant cul-de-sac")], taille=16)

    s.bandeau([
        ("En étage et en sous-sol, distance mesurée suivant l'axe des circulations de tout point d'un local : 40 m au plus pour gagner un escalier", 18, TRAIT),
        ("protégé ou une circulation horizontale protégée (portes à ferme-porte), 30 m depuis une partie formant cul-de-sac ; 30 m pour un escalier non protégé.", 18, TRAIT),
        ("Au rez-de-chaussée, l'escalier encloisonné débouche directement dehors ou à moins de 20 m d'une sortie, par un cheminement direct,", 18, TRAIT),
        ("de même largeur et libre en permanence. Escalier non protégé : débouché à moins de 50 m d'une sortie (30 m sans choix) — CO 52 § 6.", 18, TRAIT),
    ])
    return s
