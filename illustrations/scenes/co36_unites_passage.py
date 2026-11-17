"""CO 36 — Unité de passage, largeur de passage."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "CO36_unites-de-passage",
    "titre": "Unités de passage",
    "articles": ["ERP:CO 36", "ERP:CO 44"],
    "fiche": "C.15",
    "legende": "Unité de passage (UP) : 0,60 m. Un dégagement d'une UP mesure 0,90 m, de deux UP 1,40 m, puis n × 0,60 m. Au-delà de 200 personnes, dégagements normaux de 2 UP au moins. Tolérance de -5 % sur la largeur des portes (CO 44).",
    "ecarts": [
        "Escaliers mécaniques (≤ 30°) et trottoirs roulants (≤ 12°) : 50 % au plus peuvent compter ; 1 UP pour 0,80 m entre mains courantes (0,60 m entre limons), 2 UP pour 1,20 m (1 m entre limons).",
    ],
}

ROUGE = "#C1121F"


def dessiner():
    s = Scene(1600, 1160, echelle=54, origine=(380, 300))
    s.cartouche("Unités de passage", "Largeur des dégagements — ERP", "CO 36")
    s.sol(-1, -1, 19, 5, "#F3F4F6", ep=1.4)
    ouv = [(1.0, 0.90, "1 UP\n0,90 m", 1), (4.6, 1.40, "2 UP\n1,40 m", 2), (9.4, 1.80, "3 UP\n3 × 0,60 = 1,80 m", 3), (13.8, 2.40, "4 UP\n4 × 0,60 = 2,40 m", 4)]
    murs = []
    x = -1
    for x0, w, t, n in ouv:
        murs.append(dict(x=x, y=-0.3, z=0, dx=x0 - x, dy=0.3, dz=2.6, pal=MUR))
        murs.append(dict(x=x0, y=-0.3, z=2.2, dx=w, dy=0.3, dz=0.4, pal=MUR))
        x = x0 + w
    murs.append(dict(x=x, y=-0.3, z=0, dx=18 - x, dy=0.3, dz=2.6, pal=MUR))
    s.volumes(murs)
    for x0, w, t, n in ouv:
        for k in range(n):
            cx = x0 + w / (2 * n) + k * w / n
            s.personne((cx + 0.15, 0.6, 0), 34, 1 + (k % 4), femme=(k % 2 == 1))
        s.cote((x0, 0, 0), (x0 + w, 0, 0), "", decal=(0, 2.4, 0))
        u, v = s.p(x0 + w / 2, 2.4, 0)
        s.etiquette(u - 30, v + 52, t, ROUGE, 19)
    s.bandeau([
        ("Chaque dégagement a une largeur proportionnée au nombre de personnes appelées à l'emprunter, calculée en unités de passage de 0,60 m.", 19, TRAIT),
        ("Un dégagement d'une ou deux unités de passage mesure respectivement 0,90 m et 1,40 m.", 19, TRAIT),
        ("Établissements, locaux, niveaux, secteurs ou compartiments de plus de 200 personnes : dégagements normaux de 2 UP au moins", 19, TRAIT),
        ("(dégagements d'1 UP admis s'ils ne comptent qu'une fois, soit en nombre de dégagements, soit en unités de passage).", 17, "#4B5563"),
    ])
    return s
