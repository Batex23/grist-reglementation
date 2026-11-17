"""Type J — J 3, J 10, J 19, J 25 : zones et transfert horizontal."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "J10_zones-transfert-horizontal",
    "titre": "Type J : zones et transfert horizontal",
    "articles": ["ERP:J 10", "ERP:J 3", "ERP:J 19", "ERP:J 25", "ERP:J 17", "ERP:J 18"],
    "fiche": "",
    "legende": "Chaque niveau (sauf de plain-pied sur l'extérieur) est recoupé au moins une fois, de façade à façade, par une cloison CF : deux zones de capacité équivalente. Au début de l'incendie, les résidents sont transférés horizontalement vers la zone contiguë ; l'évacuation verticale n'est envisagée qu'en dernier recours.",
    "ecarts": [
        "Portes entre zones et portes de recoupement à fermeture automatique asservie à la détection (J 10, J 19, J 36) ; circulations communes de 2 UP (J 17) ; 40 m jusqu'à un escalier, 30 m en cul-de-sac (J 18).",
        "Circulations communes désenfumées mécaniquement quelle que soit leur longueur, sauf bâtiments R+1 et halls (J 25) ; commandes automatiques asservies à la détection.",
    ],
}

ROUGE = "#C1121F"
BLEU = "#1D4ED8"


def dessiner():
    s = Scene(1600, 1160, echelle=19, origine=(400, 290))
    s.cartouche("Type J : zones et transfert horizontal", "Structures d'accueil pour personnes âgées ou handicapées — niveau d'hébergement", "J 3 · J 10 · J 19")
    h = 1.2
    L, P = 50, 16
    s.sol(-2, -2, L + 4, P + 4, "#E5E7EB", trait=None)
    s.sol(0, 0, 25, P, "#FBF3E4", ep=1.4)
    s.sol(25, 0, 25, P, "#EAF2FB", ep=1.4)
    s.sol(0, 6.5, L, 3, "#E9F3EA", ep=1.2)
    for xs in (0, L - 4):
        s.sol(xs, 10, 4, 6, "#D6E6F7", ep=1.2)
    v = [mur(0, 0, L, 0, h), mur(0, 0, 0, P, h), mur(L, 0, L, P, h), mur(0, P, L, P, h)]
    for x in range(4, L, 5):
        if x == 24:
            continue
        v += [mur(x, 0, x, 6.5, h), mur(x, 9.5, x, P, h)] if x not in (4, 44) else [mur(x, 0, x, 6.5, h)]
    for x0 in range(0, L, 5):
        if x0 in (0, 45):
            continue
        v += [mur(x0, 6.5, x0 + 1, 6.5, h, pal=MUR_PF), mur(x0 + 2.2, 6.5, x0 + 5, 6.5, h, pal=MUR_PF)]
        v += [mur(x0, 9.5, x0 + 1, 9.5, h, pal=MUR_PF), mur(x0 + 2.2, 9.5, x0 + 5, 9.5, h, pal=MUR_PF)]
    v += [mur(0, 9.5, 4, 9.5, h, pal=MUR_BLEU), mur(46, 9.5, 50, 9.5, h, pal=MUR_BLEU), mur(4, 10, 4, 16, h, pal=MUR_BLEU), mur(46, 10, 46, 16, h, pal=MUR_BLEU)]
    v += [mur(25, 0, 25, 6.5, h + 0.2, ep=0.45, pal=MUR_CF), mur(25, 9.5, 25, P, h + 0.2, ep=0.45, pal=MUR_CF)]
    s.volumes(v)
    s.boite(24.8, 6.5, 0, 0.4, 3, 2.1, MUR_CF, ep=1.6, opacite=0.6)
    s.icone("feu_01", (12, 3, 0), 46)
    # transfert horizontal
    s.chemin([(8, 8, 0.1), (31, 8, 0.1)], BLEU, 6)
    s.icone("femme-assise_01", (14, 8, 0), 28)
    s.personne((18, 7.5, 0), 28, 6, True)
    s.ufr(*s.p(21, 8.4, 0.2), 30)
    u, v_ = s.p(12.5, 3, 0); s.pastille(u - 120, v_ + 10, "zone sinistrée", ROUGE, taille=17)
    u, v_ = s.p(37.5, 3, 0); s.pastille(u, v_ - 60, "zone contiguë protégée", BLEU, taille=17)
    s.repere((25, 13, 1.4), "cloison CF de façade à façade\n(zones de capacité équivalente)", du=300, dv=-120, couleur=ROUGE, taille=17)
    s.repere((25, 8, 2.1), "portes entre zones à fermeture\nautomatique asservie à la détection", du=60, dv=-250, couleur=ROUGE, taille=17)
    s.repere((24, 8, 0.1), "transfert horizontal des résidents\n(évacuation verticale en dernier recours)", du=-120, dv=200, couleur=BLEU, taille=17)
    s.repere((2, 13, 1.2), "escalier", du=40, dv=-110, couleur="#1D4ED8", taille=16)
    s.bandeau([
        ("Principe (J 3) : renforcement de l'isolement, détection automatique généralisée pour une alarme précoce, désenfumage des circulations,", 18, TRAIT),
        ("personnel formé ; transfert horizontal vers une zone contiguë protégée. Au plus 6 étages sur rez-de-chaussée (J 5).", 18, TRAIT),
        ("Compartiments seulement sans locaux à sommeil, 600 m² au plus (J 11). Alarme type 1, alarme générale sélective ; exercices semestriels (J 37, J 39).", 18, TRAIT),
    ])
    return s
