"""CO 4 — Nombre de façades accessibles et dessertes par voies ou espaces libres."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "CO4_facades-accessibles",
    "titre": "Nombre de façades accessibles",
    "articles": ["ERP:CO 4"],
    "fiche": "C.5",
    "legende": "Nombre de façades accessibles et largeur des voies qui les desservent selon la catégorie et l'effectif de l'établissement.",
    "ecarts": [],
}

FAC = ("#FFE9A8", "#FFD15C", "#F2B705")
ROUGE = "#C1121F"


def panneau(s, ox, oy, titre, voies, note=""):
    """voies : liste de (côté, largeur en m, texte) ; côté parmi +y, +x, -y, -x."""
    s.ox, s.oy = ox, oy
    L, P, H = 16, 10, 6
    s.sol(-9, -9, L + 18, P + 18, VERT_GAZON, trait=None)
    cotes = {c for c, _, _ in voies}
    for c, w, t in voies:
        k = 0.42 * w
        if c == "+y": s.sol(-9, P + 3, L + 18, k, ENROBE_CLAIR, ep=1.2)
        if c == "-y": s.sol(-9, -3 - k, L + 18, k, ENROBE_CLAIR, ep=1.2)
        if c == "+x": s.sol(L + 3, -9, k, P + 12 + (k if "+y" in cotes else 6), ENROBE_CLAIR, ep=1.2)
        if c == "-x": s.sol(-3 - k, -9, k, P + 18, ENROBE_CLAIR, ep=1.2)
    s.boite(0, 0, 0, L, P, H, (BEIGE[0], FAC[1] if "+y" in cotes else BEIGE[1], FAC[2] if "+x" in cotes else BEIGE[2]))
    if "-y" in cotes: s.ligne((0, 0, H), (L, 0, H), "#F2B705", 6)
    if "-x" in cotes: s.ligne((0, 0, H), (0, P, H), "#F2B705", 6)
    for c, w, t in voies:
        k = 0.42 * w
        pos = {"+y": (-3, P + 3 + k / 2, 0), "-y": (2, -3 - k / 2, 0), "+x": (L + 3 + k / 2, -5, 0), "-x": (-3 - k / 2, P / 2 - 4, 0)}[c]
        u, v = s.p(*pos)
        s.pastille(u, v, t, ROUGE, taille=15)
    s.ox, s.oy = ox, oy
    s.texte(ox - 230, oy - 150, titre, 19, TRAIT, gras=True)
    if note:
        s.texte(ox - 230, oy - 126, note, 15, "#4B5563")


def dessiner():
    s = Scene(1600, 1160, echelle=8.5, origine=(0, 0))
    s.cartouche("Nombre de façades accessibles", "Façades accessibles et voies de desserte selon la catégorie — ERP", "CO 4")
    panneau(s, 300, 300, "4e catégorie", [("+y", 6, "voie 6 m · chaussée 4 m")], "ou impasse de 8 m, chaussée 7 m")
    panneau(s, 820, 300, "2e et 3e catégories", [("+y", 8, "voie 8 m")])
    panneau(s, 1320, 300, "1re cat. · 1 500 à 2 500 pers.", [("+y", 8, "voie 8 m"), ("+x", 8, "voie 8 m")])
    panneau(s, 300, 680, "1re cat. · 2 500 à 3 500 pers.", [("+y", 12, "voie 12 m"), ("+x", 8, "voie 8 m")], "3e façade (voie 8 m) si la condition 2 n'est pas remplie")
    panneau(s, 820, 680, "1re cat. · plus de 3 500 pers.", [("+y", 12, "voie 12 m"), ("-y", 12, "voie 12 m")], "deux façades opposées")
    panneau(s, 1320, 680, "ou trois façades réparties", [("+y", 12, "voie 12 m"), ("-y", 12, "voie 12 m"), ("+x", 8, "voie 8 m")], "quatre façades si la condition 2 n'est pas remplie")
    s.legende(1180, 905, [(FAC[1], "façade accessible"), (ENROBE_CLAIR, "voie engins desservant la façade")], taille=16)
    s.bandeau([
        ("1re catégorie au-delà de 3 500 personnes : façades accessibles sur plus de la moitié du périmètre (condition 1) et locaux en étage", 18, TRAIT),
        ("situés sur ces façades ou reliés par de larges dégagements (condition 2). 4e catégorie en rez-de-chaussée : sorties possibles sur un passage", 18, TRAIT),
        ("de 1,80 m relié à ses deux extrémités à des voies engins — moins de 50 m (couvert non désenfumé) ou 100 m (désenfumé ou à l'air libre).", 18, TRAIT),
    ])
    return s
