"""CO 12 — Résistance au feu des structures et planchers."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "CO12_stabilite-structures",
    "titre": "Stabilité au feu des structures",
    "articles": ["ERP:CO 12", "ERP:CO 11", "ERP:CO 14", "ERP:CO 15"],
    "fiche": "C.7",
    "legende": "Structure SF et planchers CF selon le nombre de niveaux, la hauteur (8 m, 28 m) et la catégorie : ½ h en simple rez-de-chaussée, ½ h ou 1 h jusqu'à 8 m, 1 h ou 1 h ½ de 8 à 28 m (1re catégorie : degré supérieur).",
    "ecarts": [
        "Équivalences européennes : SF ½ h = R 30, SF 1 h = R 60, SF 1 h ½ = R 90 ; planchers CF ½ h = REI 30, CF 1 h = REI 60, CF 1 h ½ = REI 90.",
        "Exceptions sans exigence : bâtiments en rez-de-chaussée sous conditions (CO 14), certains bâtiments de 3 niveaux au plus en 3e et 4e catégories (CO 15).",
    ],
}

ROUGE = "#C1121F"
BLEU = "#1D4ED8"


def bat(s, x0, niveaux, h_niv=3.5, l=11, p=9):
    H = niveaux * h_niv
    s.boite(x0, 0, 0, l, p, H, BEIGE, ep=2.2)
    s.fenetres_y(x0, p, 0, l, H, 3, niveaux, larg=1.4, haut=1.4, marge_bas=1.0)
    for k in range(1, niveaux):
        s.ligne((x0, p, k * h_niv), (x0 + l, p, k * h_niv), ROUGE, 3.2)
        s.ligne((x0 + l, p, k * h_niv), (x0 + l, 0, k * h_niv), ROUGE, 3.2)
    for xc in (x0 + 0.15, x0 + l / 2, x0 + l - 0.15):
        s.ligne((xc, p, 0), (xc, p, H), BLEU, 3)
    return H


def dessiner():
    s = Scene(1600, 1160, echelle=12.5, origine=(480, 560))
    s.cartouche("Stabilité au feu des structures", "Structure (SF) et planchers (CF) selon la hauteur et la catégorie — ERP", "CO 12")
    s.sol(-8, -6, 76, 22, VERT_GAZON, trait=None)
    bat(s, 0, 1, h_niv=5, p=8)
    bat(s, 22, 2, p=8)
    bat(s, 44, 8, p=8)
    # règle des hauteurs
    s.ligne((58, 0, 0), (58, 0, 30), "#374151", 2.4)
    for z in (0, 8, 28):
        s.ligne((57.4, 0, z), (58.6, 0, z), "#374151", 2.4)
        s.ligne((55, 0, z), (57.4, 0, z), "#9CA3AF", 1.4, "5 4")
        u, v = s.p(58.6, 0, z); s.texte(u + 10, v + 6, f"{z} m", 18, "#374151", gras=True)
    cases = [(5.5, 5, "Simple rez-de-chaussée", ["Toutes catégories : SF ½ h · CF ½ h"]),
             (27.5, 7, "Dernier niveau à moins de 8 m", ["2e à 4e cat. : SF ½ h · CF ½ h", "1re cat. : SF 1 h · CF 1 h"]),
             (49.5, 28, "De 8 m à 28 m", ["2e à 4e cat. : SF 1 h · CF 1 h", "1re cat. : SF 1 h ½ · CF 1 h ½"])]
    for x, z, t1, lignes in cases:
        u, v = s.p(x, 4, z)
        s.etiquette(u, v - 60 - 12 * len(lignes), t1 + "\n" + "\n".join(lignes), "#1F2A37", 16, gras=False)
    s.legende(40, 860, [("#1D4ED8", "structure : stabilité au feu (SF)"), (ROUGE, "planchers : coupe-feu (CF)")], taille=17)

    s.bandeau([
        ("Le degré dépend du plancher bas du niveau le plus haut et de la différence de hauteur entre niveaux extrêmes de l'établissement (8 m).", 18, TRAIT),
        ("Au-delà de 28 m : immeuble de grande hauteur. Les plafonds suspendus peuvent compter dans la résistance des planchers sous conditions.", 18, TRAIT),
        ("Toiture : SF ½ h, voire sans exigence, si l'ERP occupe le dernier niveau, toiture non accessible et sans effondrement en chaîne (CO 13).", 18, TRAIT),
        ("Mezzanine de moins de 50 % du niveau qu'elle surplombe : ne compte pas comme niveau (CO 11 § 4).", 17, "#4B5563"),
    ])
    return s
