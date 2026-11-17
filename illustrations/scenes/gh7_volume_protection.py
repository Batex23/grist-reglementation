"""IGH — GH 7, GH 8, GH 9 : isolement du voisinage et volume de protection."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "GH7_volume-protection",
    "titre": "IGH : volume de protection",
    "articles": ["IGH:GH 7", "IGH:GH 8", "IGH:GH 9"],
    "fiche": "",
    "legende": "Un IGH est isolé des constructions voisines par une façade CF 2 h (REI 120) sur toute sa hauteur, ou par un volume de protection limité à 8 m de toute façade non CF 2 h. Dans ce volume : aucun élément combustible ; constructions basses (< 8 m) à structure indépendante SF 2 h, façades et couvertures PF 2 h, sorties à moins de 60 m d'une voie engins.",
    "ecarts": ["Planche ajoutée : l'ancien recueil ne traitait pas les IGH. Structure de l'IGH : SF 2 h ou R 120 (GH 9)."],
}

ROUGE = "#C1121F"


def dessiner():
    s = Scene(1600, 1160, echelle=7.4, origine=(760, 640))
    s.cartouche("IGH : volume de protection", "Isolement d'un immeuble de grande hauteur vis-à-vis du voisinage", "GH 7 · GH 8")
    s.sol(-20, -20, 70, 64, VERT_GAZON, trait=None)
    s.sol(-20, 34, 70, 8, ENROBE, ep=1.4)
    # emprise du volume de protection au sol (8 m autour)
    s.sol(-8, -8, 36, 34, "#FDE68A", trait="#B45309", ep=2, tirets="10 6", opacite=0.55)
    H = 60
    s.boite(0, 0, 0, 20, 18, H, GRIS)
    s.fenetres_y(0, 18, 0, 20, H, 6, 18, larg=1.6, haut=1.4)
    s.fenetres_x(20, 0, 0, 18, H, 5, 18, larg=1.6, haut=1.4)
    # contour du volume de protection en hauteur (arêtes verticales en tirets)
    for (x, y) in [(28, -8), (28, 26), (-8, 26)]:
        s.ligne((x, y, 0), (x, y, H), "#B45309", 1.6, "8 6")
    s.poly([(-8, 26, H), (28, 26, H), (28, -8, H)], "none", trait="#B45309", ep=1.6, tirets="8 6")
    # construction basse dans le volume
    s.boite(22, 8, 0, 10, 10, 6, BEIGE, ep=1.8)
    s.fenetres_x(32, 8, 0, 10, 6, 3, 2)
    s.icone("SP_fpt_02", (10, 38, 0), 140, ancre=(0.5, 0.8))
    s.cote((20, 18, 0), (28, 18, 0), "8 m", decal=(0, 0, 0), rappel=False, dy_txt=30, dx_txt=-30)
    s.cote((32, 18, 0), (32, 18, 6), "< 8 m", decal=(2, 0, 0), dx_txt=50)
    s.repere((28, 26, 40), "limite latérale du volume de protection :\n8 m au moins des façades non CF 2 h", du=230, dv=40, couleur="#B45309", taille=17)
    s.repere((32, 13, 6), "construction dans le volume : structure\nindépendante SF 2 h, murs, façades et\ncouverture PF 2 h, sorties à < 60 m\nd'une voie engins", du=260, dv=90, couleur=ROUGE, taille=17)
    s.repere((10, 18, 30), "IGH : structure SF 2 h (R 120)", du=-330, dv=-40, couleur=TRAIT, taille=17)
    s.repere((-4, 22, 0), "aucun élément combustible\ndans le volume (végétation exclue)", du=-300, dv=40, couleur="#B45309", taille=17)
    s.bandeau([
        ("Isolement par un mur ou une façade verticale coupe-feu 2 h (REI 120) sur toute la hauteur, ou par un volume de protection (GH 7).", 18, TRAIT),
        ("Le volume ne peut empiéter sur les fonds voisins, sauf servitude conventionnelle par acte authentique ou indépendance des volumes.", 18, TRAIT),
        ("Limite inférieure : le sol, ou des constructions voisines CF 2 h. Le cheminement de 60 m compte 5 fois chaque dénivellation (GH 8).", 18, TRAIT),
    ])
    return s
