"""CO 35 et CO 37 — Conception des dégagements, cul-de-sac."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "CO35_conception-degagements",
    "titre": "Conception des dégagements",
    "articles": ["ERP:CO 35", "ERP:CO 37", "ERP:CO 34"],
    "fiche": "C.15",
    "legende": "Une circulation principale par sortie ; circulations de 2 UP entre escaliers et sorties ; portes des locaux à 10 m au plus du débouché d'un cul-de-sac ; pas de marche isolée ; aucune saillie de plus de 0,10 m sous 1,10 m de haut.",
    "ecarts": [],
}

ROUGE = "#C1121F"
VERT = "#15803D"


def dessiner():
    s = Scene(1600, 1160, echelle=21, origine=(520, 250))
    s.cartouche("Conception des dégagements", "Circulations principales, cul-de-sac, saillies — ERP", "CO 35 · CO 37")
    h = 0.8
    L, P = 40, 24
    s.sol(-2, -2, L + 4, P + 4, VERT_GAZON, trait=None)
    s.sol(0, 0, L, P, SOL_INT, ep=1.4)
    s.sol(4, 8, L - 8, 2, "#BFE3C6", ep=1.2)                     # circulation principale (2 UP)
    s.sol(18, 10, 2, 12, "#F8CF8F", ep=1.2)                      # cul-de-sac
    for xs in (0, L - 4):
        s.sol(xs, 6, 4, 6, "#D6E6F7", ep=1.2)
        for k in range(1, 9):
            s.ligne((xs + 0.3, 6 + k * 0.62, 0), (xs + 3.7, 6 + k * 0.62, 0), "#5B7DB1", 1.2)
    v = [mur(0, 0, L, 0, h), mur(0, 0, 0, P, h), mur(L, 0, L, P, h), mur(0, P, L, P, h)]
    for xs in (0, L - 4):
        v += [mur(xs, 6, xs + 4, 6, h, pal=MUR_BLEU), mur(xs, 12, xs + 4, 12, h, pal=MUR_BLEU)]
    v += [mur(4, 6, 4, 8, h, pal=MUR_BLEU), mur(4, 10, 4, 12, h, pal=MUR_BLEU), mur(L - 4, 6, L - 4, 8, h, pal=MUR_BLEU), mur(L - 4, 10, L - 4, 12, h, pal=MUR_BLEU)]
    v += [mur(4, 8, 36, 8, h, pal=MUR_PF)]
    v += [mur(4, 10, 18, 10, h, pal=MUR_PF), mur(20, 10, 36, 10, h, pal=MUR_PF)]
    # branche en cul-de-sac (y 10 → 22) : portes des locaux à moins de 10 m du débouché
    v += [mur(18, 10, 18, 12, h, pal=MUR_PF), mur(18, 13.2, 18, 17, h, pal=MUR_PF), mur(18, 18.2, 18, 22, h, pal=MUR_PF)]
    v += [mur(20, 10, 20, 15, h, pal=MUR_PF), mur(20, 16.2, 20, 22, h, pal=MUR_PF), mur(18, 22, 20, 22, h, pal=MUR_PF)]
    v += [mur(4, 17, 18, 17, h), mur(20, 16, 36, 16, h), mur(10, 10, 10, 17, h), mur(28, 10, 28, 16, h), mur(10, 0, 10, 8, h), mur(28, 0, 28, 8, h)]
    s.volumes(v)
    for (cx, cy, a0, a1) in [(18, 12, 90, 160), (18, 17, 90, 160), (20, 15, 90, 20)]:
        s.arc_sol((cx, cy), 1.0, a0, a1, 0, ROUGE, 1.4)
    s.chemin([(19, 21, 0.1), (19, 9, 0.1), (L - 4.4, 9, 0.1)], VERT, 4.5)
    s.chemin([(19, 9, 0.1), (4.4, 9, 0.1)], VERT, 4.5)
    s.cote((20, 10, 0), (20, 18.2, 0), "≤ 10 m", decal=(1.6, 0, 0), dx_txt=56, dy_txt=10)
    s.cote((26, 8, 0), (26, 10, 0), "2 UP", decal=(0, 0, 0), rappel=False, dx_txt=46, dy_txt=-26)
    s.repere((19, 20, 0), "dégagement en cul-de-sac", du=-260, dv=150, couleur="#B45309", taille=17)
    s.repere((18, 18.2, 1.0), "porte de local la plus éloignée :\n10 m au plus du débouché", du=-330, dv=-40, couleur=ROUGE, taille=17)
    s.repere((30, 9, 0), "circulation de 2 UP reliant\nles escaliers entre eux", du=200, dv=-150, couleur=VERT, taille=17)

    # encart saillies (CO 37) et marches (CO 35 § 1)
    x0, y0 = 1080, 760
    s.items.append(f'<rect x="{x0}" y="{y0}" width="480" height="210" rx="10" fill="#FFFFFF" stroke="#9CA3AF" stroke-width="1.5"/>')
    s.texte(x0 + 20, y0 + 34, "Dans les circulations principales", 18, TRAIT, gras=True)
    s.texte(x0 + 20, y0 + 66, "• pas d'une ou deux marches isolées : pente ≤ 10 %", 16, TRAIT)
    s.texte(x0 + 20, y0 + 90, "  ou groupe de 3 marches égales au moins", 16, TRAIT)
    s.texte(x0 + 20, y0 + 120, "• saillies fixes admises jusqu'à 1,10 m de haut", 16, TRAIT)
    s.texte(x0 + 20, y0 + 144, "  si elles dépassent de 0,10 m au plus", 16, TRAIT)
    s.texte(x0 + 20, y0 + 174, "• aucun dépôt dans la largeur réglementaire", 16, TRAIT)

    s.bandeau([
        ("À chaque sortie sur l'extérieur ou sur un dégagement protégé correspond une circulation principale. Des circulations de 2 UP relient", 18, TRAIT),
        ("au rez-de-chaussée les escaliers aux sorties et les sorties entre elles, en étage et en sous-sol les escaliers entre eux (1 UP si les", 18, TRAIT),
        ("dégagements reliés n'en offrent qu'une). Portes des locaux accessibles au public à 10 m au plus du débouché d'un cul-de-sac.", 18, TRAIT),
    ])
    return s
