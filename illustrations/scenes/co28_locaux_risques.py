"""CO 27 et CO 28 — Locaux à risques particuliers."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "CO28_locaux-risques",
    "titre": "Locaux à risques particuliers",
    "articles": ["ERP:CO 28", "ERP:CO 27"],
    "fiche": "C.13",
    "legende": "Risques importants : parois et plancher haut CF 2 h, porte CF 1 h à ferme-porte s'ouvrant vers la sortie, aucune communication directe avec le public. Risques moyens : parois et plancher haut CF 1 h, bloc-porte CF ½ h à ferme-porte.",
    "ecarts": [
        "La liste des locaux à risques moyens ou importants est fixée par les chapitres techniques et les dispositions particulières de chaque type (ex. chaufferie > 70 kW : CH ; local électrique : EL). Les exemples de l'ancienne fiche sont indicatifs.",
        "Équivalences : CF 2 h = EI 120 (REI 120 pour un plancher), CF 1 h = EI 60, porte CF 1 h = EI2 60-C, porte CF ½ h = EI2 30-C.",
    ],
}

ROUGE = "#C1121F"
ORANGE = "#B45309"
MUR_LRM = ("#FDE2B8", "#F7C27A", "#E0A04A")


def dessiner():
    s = Scene(1600, 1160, echelle=25, origine=(720, 330))
    s.cartouche("Locaux à risques particuliers", "Isolement des locaux à risques importants et moyens — ERP", "CO 27 · CO 28")
    h = 2.6
    s.sol(-2, -2, 34, 22, "#E5E7EB", trait=None)
    s.sol(0, 0, 30, 18, SOL_INT, ep=1.4)
    s.sol(0, 8, 30, 3, "#E9F3EA", ep=1.2)                              # dégagement accessible au public
    s.sol(0, 0, 8, 8, "#FCE3E1", ep=1.2)                               # LRI
    s.sol(8, 0, 3, 8, "#F3F4F6", ep=1.2)                               # dégagement non accessible au public
    s.sol(11, 0, 8, 8, "#FFF1DC", ep=1.2)                              # LRM
    v = [mur(0, 0, 30, 0, h), mur(0, 0, 0, 18, h)]
    v += [mur(8, 0, 8, 2.2, h, ep=0.4, pal=MUR_CF), mur(8, 3.4, 8, 8, h, ep=0.4, pal=MUR_CF), mur(0, 8, 8, 8, h, ep=0.4, pal=MUR_CF)]
    v += [mur(8, 8, 9, 8, h, pal=MUR), mur(10.3, 8, 11, 8, h, pal=MUR)]
    v += [mur(11, 0, 11, 8, h, ep=0.35, pal=MUR_LRM), mur(11, 8, 14, 8, h, ep=0.35, pal=MUR_LRM), mur(15.2, 8, 19, 8, h, ep=0.35, pal=MUR_LRM), mur(19, 0, 19, 8, h, ep=0.35, pal=MUR_LRM)]
    v += [mur(19, 8, 30, 8, h, pal=MUR_PF), mur(0, 11, 4, 11, h * 0.5, pal=MUR_PF), mur(5.2, 11, 30, 11, h * 0.5, pal=MUR_PF)]
    s.volumes(v)
    # plancher haut CF 2 h du LRI (en transparence)
    s.sol(0, 0, 8.2, 8.2, ROUGE, trait=ROUGE, ep=2, z=h + 0.05, opacite=0.28)
    s.sol(11, 0, 8.2, 8.2, "#F59E0B", trait=ORANGE, ep=2, z=h + 0.05, opacite=0.25)
    s.vantail((8, 2.2), 1.2, 40, 2.1, "#D9776F")
    s.vantail((14, 8), 1.2, 60, 2.1, "#F7C27A")
    s.vantail((9, 8), 1.2, 50, 2.0, "#E5E7EB")
    s.icone("feu_02", (3.5, 4, 0), 40)
    s.personne((20, 10, 0), 32, 5); s.personne((25, 14, 0), 32, 6, True)
    u, v_ = s.p(4, 4, h + 0.1); s.pastille(u, v_ - 6, "Risques importants", ROUGE, taille=17)
    u, v_ = s.p(15, 4, h + 0.1); s.pastille(u, v_ - 6, "Risques moyens", ORANGE, taille=17)
    s.repere((0, 4, h), "parois et plancher haut CF 2 h\nfaçades selon CO 19 à CO 22\nconduits selon CO 32 et CO 33", du=-250, dv=-60, couleur=ROUGE, taille=17)
    s.repere((8, 2.8, 2.0), "porte CF 1 h, ferme-porte,\nouverture vers la sortie", du=-30, dv=-200, couleur=ROUGE, taille=17)
    s.repere((9.6, 6, 0), "accès par un dégagement\nnon accessible au public", du=-320, dv=170, couleur="#374151", taille=17)
    s.repere((19, 4, h), "parois et plancher haut CF 1 h\nbloc-porte CF ½ h à ferme-porte\nconduits selon CO 31", du=230, dv=-130, couleur=ORANGE, taille=17)
    s.repere((24, 9.5, 0), "dégagement accessible au public", du=200, dv=120, couleur="#15803D", taille=17)

    s.bandeau([
        ("Locaux à risques importants : façades selon la section V, conduits selon CO 32 et CO 33, parois et planchers hauts CF 2 h, communications", 18, TRAIT),
        ("CF 1 h s'ouvrant vers la sortie avec ferme-porte ; aucune communication directe avec les locaux et dégagements accessibles au public.", 18, TRAIT),
        ("Locaux à risques moyens : isolés des locaux et dégagements accessibles au public par des parois et planchers hauts CF 1 h,", 18, TRAIT),
        ("blocs-portes CF ½ h à ferme-porte ; conduits selon CO 31. Locaux à risques courants : pas d'isolement particulier (CO 29).", 18, TRAIT),
    ])
    return s
