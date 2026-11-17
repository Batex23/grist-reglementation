"""Type PS — PS 12, PS 13 : compartimentage, escaliers et distances."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "PS12_compartiments-escaliers",
    "titre": "Parcs de stationnement : compartiments et escaliers",
    "articles": ["ERP:PS 12", "ERP:PS 13", "ERP:PS 14"],
    "fiche": "",
    "legende": "Compartiments de moins de 3 000 m² (surface du niveau jusqu'à 3 600 m², 6 000 m² sprinklé), parois CF 1 h, portes PF 1 h à ferme-porte, baies véhicules E 60 à fermeture automatique. Escalier ou sortie à 40 m au plus entre deux issues opposées, 25 m sinon (30 / 50 m si largement ventilé). Accès aux escaliers par un sas de 3 m², à moins de 10 m de l'escalier.",
    "ecarts": [
        "Arrêté du 9 mai 2006 modifié (type PS). Distances mesurées dans l'axe des circulations des véhicules depuis l'axe de la place la plus éloignée.",
        "Tunnel de circulation de plus de 50 m : 40 m au plus pour en sortir, désenfumage (900 m³/h par 5 m, 600 si sprinklé) (PS 14).",
    ],
}

ROUGE = "#C1121F"
VERT = "#15803D"


def dessiner():
    s = Scene(1600, 1160, echelle=11.5, origine=(400, 290))
    s.cartouche("Parcs de stationnement : compartiments et escaliers", "Niveau d'un parc couvert non largement ventilé", "PS 12 · PS 13")
    h = 1.0
    L, P = 80, 40
    s.sol(-2, -2, L + 4, P + 4, "#E5E7EB", trait=None)
    s.sol(0, 0, 40, P, "#ECEEF1", ep=1.4)
    s.sol(40, 0, 40, P, "#E4E8EE", ep=1.4)
    s.sol(0, 16, L, 8, "#D1D5DB", ep=1.0)                      # allée de circulation
    for x in range(2, L - 2, 3):
        for y in (0.5, 25):
            s.sol(x, y, 2.5, 5, "none", trait="#FFFFFF", ep=1.4)
    for x in range(2, L - 2, 3):
        for y in (10.5, 35):
            s.sol(x, y, 2.5, 5, "none", trait="#FFFFFF", ep=1.4)
    v = [mur(0, 0, L, 0, h), mur(0, 0, 0, P, h), mur(L, 0, L, P, h), mur(0, P, L, P, h)]
    v += [mur(40, 0, 40, 16, h + 1, ep=0.5, pal=MUR_CF), mur(40, 24, 40, P, h + 1, ep=0.5, pal=MUR_CF)]
    # escaliers avec sas (deux côtés opposés)
    for (x0, y0) in ((0, 30), (76, 0)):
        s.sol(x0, y0, 4, 4, "#D6E6F7", ep=1.2)
    v += [mur(4, 30, 4, 34, h + 1, pal=MUR_BLEU), mur(0, 30, 4, 30, h + 1, pal=MUR_BLEU), mur(76, 4, 80, 4, h + 1, pal=MUR_BLEU), mur(76, 0, 76, 4, h + 1, pal=MUR_BLEU)]
    s.volumes(v)
    s.boite(39.75, 16, 0, 0.5, 8, 2.2, ("#FDE2B8", "#F7C27A", "#E0A04A"), ep=1.4, opacite=0.6)
    for (x, y) in [(10, 3), (30, 28), (55, 12), (66, 30)]:
        s.boite(x, y, 0, 2.2, 4.5, 1.4, ("#93C5FD", "#3B82F6", "#1D4ED8") if x % 2 else ("#FCA5A5", "#EF4444", "#B91C1C"), ep=1.2)
    s.chemin([(38, 3, 0.05), (38, 20, 0.05), (3, 20, 0.05), (3, 29.6, 0.05)], VERT, 4, "10 6")
    s.chemin([(42, 37, 0.05), (42, 20, 0.05), (78, 20, 0.05), (78, 4.4, 0.05)], VERT, 4, "10 6")
    u, v_ = s.p(20, 8, 0); s.pastille(u, v_, "compartiment < 3 000 m²", "#374151", taille=15)
    u, v_ = s.p(60, 32, 0); s.pastille(u, v_, "compartiment", "#374151", taille=15)
    s.repere((40, 20, 2.2), "baie de passage des véhicules : obturation E 60\nà fermeture automatique + commande manuelle", du=60, dv=-230, couleur="#B45309", taille=16)
    s.repere((40, 30, 2.0), "paroi de compartimentage CF 1 h (EI 60),\nportes piétons PF 1 h à ferme-porte (E 60-C)", du=300, dv=-160, couleur=ROUGE, taille=16)
    s.repere((20, 20, 0.05), "≤ 40 m entre deux escaliers opposés\n(25 m sinon ; 50 / 30 m largement ventilé)", du=-150, dv=230, couleur=VERT, taille=16)
    s.repere((3, 31, 2.0), "accès par un sas ≥ 3 m², portes PF ½ h\n(E 30-C) vers l'intérieur, à < 10 m de l'escalier", du=60, dv=-200, couleur="#1D4ED8", taille=16)
    s.bandeau([
        ("Hors parcs largement ventilés, chaque niveau est recoupé en compartiments de moins de 3 000 m² (surface du niveau jusqu'à 3 600 m²,", 18, TRAIT),
        ("6 000 m² si sprinklé). Escaliers encloisonnés CF 1 h (½ h si R+1) ou à l'air libre, en matériaux A1, largeur 0,90 m au moins, volées droites", 18, TRAIT),
        ("au-delà de 4 niveaux. Boxes : 2 places au plus, parois M 0 pleines ou grillagées, vision totale sur l'intérieur depuis l'allée (PS 12 § 4).", 18, TRAIT),
    ])
    return s
