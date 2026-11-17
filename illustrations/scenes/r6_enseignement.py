"""Type R — R 1, R 6, R 15 : enseignement, compartiments et escaliers."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "R6_enseignement",
    "titre": "Type R : établissements d'enseignement",
    "articles": ["ERP:R 6", "ERP:R 15", "ERP:R 1", "ERP:R 33"],
    "fiche": "",
    "legende": "Compartiments autorisés (sauf niveau avec local à risques importants ou bâtiment avec sommeil) : 600 m² au plus, issues à 30 m au plus, sans local à risques moyens. Escalier protégé à 40 m au plus (30 m en cul-de-sac) ; escaliers non protégés seulement en R+1 avec 150 personnes au plus à l'étage. Portes des cages à fermeture automatique avec une alarme de type 1 ou 2.",
    "ecarts": [
        "Crèches, maternelles, jardins d'enfants : interdits en sous-sol ; assujettis en étage quel que soit l'effectif (20 si l'établissement n'a qu'un niveau situé en étage), 100 en rez-de-chaussée (R 1).",
        "Exercices d'évacuation pendant l'année, le premier dans le mois qui suit la rentrée, de nuit s'il y a des locaux à sommeil (R 33).",
    ],
}

ROUGE = "#C1121F"
BLEU = "#1D4ED8"


def dessiner():
    s = Scene(1600, 1160, echelle=19, origine=(420, 250))
    s.cartouche("Type R : établissements d'enseignement", "Niveau d'étage — compartiment et escaliers", "R 6 · R 15")
    h = 1.2
    L, P = 46, 22
    s.sol(-2, -2, L + 4, P + 4, "#E5E7EB", trait=None)
    s.sol(0, 0, 24, P, "#FBF3E4", ep=1.4)                  # compartiment (≤ 600 m²)
    s.sol(24, 0, 22, P, "#FBF8F2", ep=1.4)
    s.sol(24, 9, 22, 3, "#E9F3EA", ep=1.2)
    for (xs, ys) in ((0, 18), (42, 0)):
        s.sol(xs, ys, 4, 4, "#D6E6F7", ep=1.2)
    v = [mur(0, 0, L, 0, h), mur(0, 0, 0, P, h), mur(L, 0, L, P, h), mur(0, P, L, P, h)]
    v += [mur(24, 0, 24, 9, h, ep=0.4, pal=MUR_CF), mur(24, 12, 24, P, h, ep=0.4, pal=MUR_CF)]
    for x in (31, 38):
        v += [mur(x, 0, x, 9, h), mur(x, 12, x, P, h)]
    for x0 in (24, 31, 38):
        for yc in (9, 12):
            v += [mur(x0, yc, x0 + 1.2, yc, h, pal=MUR_PF), mur(x0 + 2.6, yc, x0 + 7, yc, h, pal=MUR_PF)]
    v += [mur(0, 18, 4, 18, h, pal=MUR_BLEU), mur(4, 18, 4, 22, h, pal=MUR_BLEU), mur(42, 4, 46, 4, h, pal=MUR_BLEU), mur(42, 0, 42, 4, h, pal=MUR_BLEU)]
    v += [mur(8, 0, 8, 6, h * 0.6, pal=GRIS), mur(14, 14, 20, 14, h * 0.6, pal=GRIS)]
    s.volumes(v)
    s.boite(23.8, 9, 0, 0.4, 3, 2.1, MUR_CF, ep=1.4, opacite=0.6)
    for (x, y) in [(12, 9), (5, 4), (18, 17), (28, 4), (35, 16)]:
        s.personne((x, y, 0), 26, 1 + (x % 4), x % 2 == 0)
    s.chemin([(20, 4, 0.1), (20, 10.5, 0.1), (23.6, 10.5, 0.1)], BLEU, 4, "10 6")
    s.chemin([(35, 18, 0.1), (35, 10.5, 0.1), (44, 10.5, 0.1), (44, 4.4, 0.1)], "#15803D", 4, "10 6")
    u, v_ = s.p(12, 11, 0); s.pastille(u, v_, "compartiment ≤ 600 m²", "#B45309", taille=16)
    s.repere((22, 7, 0.1), "issues du compartiment\nà 30 m au plus", du=-60, dv=230, couleur=BLEU, taille=17)
    s.repere((40, 10.5, 0.1), "≤ 40 m jusqu'à un escalier\nprotégé (30 m en cul-de-sac)", du=150, dv=160, couleur="#15803D", taille=17)
    s.repere((44, 2, 1.2), "portes des cages à fermeture\nautomatique (alarme type 1 ou 2)", du=200, dv=-120, couleur=BLEU, taille=17)
    s.repere((24, 16, 1.2), "parois du compartiment\nCF selon la structure (CO 25)", du=-160, dv=-210, couleur=ROUGE, taille=17)
    s.bandeau([
        ("Compartiments interdits dans un niveau comprenant un local à risques importants et dans un bâtiment avec locaux à sommeil ;", 18, TRAIT),
        ("un seul compartiment admis par niveau si le niveau fait 600 m² au plus (R 6). Escaliers non protégés : R+1 avec 150 personnes au plus", 18, TRAIT),
        ("à l'étage, ou un seul escalier supplémentaire desservant au plus R+2, sans locaux à sommeil (R 15). Effectif : déclaration par niveau (R 2).", 18, TRAIT),
    ])
    return s
