"""Type O — O 5, O 6, O 9 : hôtels."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "O9_hotels",
    "titre": "Type O : hôtels",
    "articles": ["ERP:O 9", "ERP:O 6", "ERP:O 5", "ERP:O 1", "ERP:O 3"],
    "fiche": "",
    "legende": "Circulations de 2 UP entre escaliers et sorties ; toutes les portes donnant sur les dégagements des chambres à ferme-porte. Escaliers protégés, sauf R+1 (ou escalier du hall ne desservant qu'un étage, après avis) avec 100 personnes au plus à l'étage. Chambres adaptées pouvant être traitées en espaces d'attente sécurisés.",
    "ecarts": [
        "Assujettis : hôtels de 100 personnes et plus ; autres hébergements à exploitation collective homogène au-delà de 15 personnes (O 1). Locaux de déchets > 50 m² : risques importants ; ≤ 50 m², réserves, lingeries, bagageries : risques moyens (O 5).",
    ],
}

ROUGE = "#C1121F"
BLEU = "#1D4ED8"


def dessiner():
    s = Scene(1600, 1160, echelle=22, origine=(400, 270))
    s.cartouche("Type O : hôtels", "Niveau d'hébergement — circulations, portes, escaliers", "O 5 · O 6 · O 9")
    h = 1.2
    L, P = 44, 14
    s.sol(-2, -2, L + 4, P + 4, "#E5E7EB", trait=None)
    s.sol(0, 0, L, P, "#FBF8F2", ep=1.4)
    s.sol(4, 5.5, L - 8, 3, "#E9F3EA", ep=1.2)
    for xs in (0, L - 4):
        s.sol(xs, 4, 4, 6, "#D6E6F7", ep=1.2)
    s.sol(4, 0, 4, 5.5, "#FCE3E1", ep=1.2)                 # local à risques (lingerie)
    s.sol(36, 8.5, 4, 5.5, "#DCEBFF", ep=1.2)               # chambre adaptée (EAS)
    v = [mur(0, 0, L, 0, h), mur(0, 0, 0, P, h), mur(L, 0, L, P, h), mur(0, P, L, P, h)]
    for x in range(8, L - 4, 4):
        v += [mur(x, 0, x, 5.5, h), mur(x, 8.5, x, P, h)]
    for x0 in range(4, L - 4, 4):
        for yc in (5.5, 8.5):
            v += [mur(x0, yc, x0 + 1.2, yc, h, pal=MUR_PF), mur(x0 + 2.4, yc, x0 + 4, yc, h, pal=MUR_PF)]
    for xs in (0, L - 4):
        v += [mur(xs, 4, xs + 4, 4, h, pal=MUR_BLEU), mur(xs, 10, xs + 4, 10, h, pal=MUR_BLEU)]
    v += [mur(4, 4, 4, 5.5, h, pal=MUR_BLEU), mur(4, 8.5, 4, 10, h, pal=MUR_BLEU), mur(40, 4, 40, 5.5, h, pal=MUR_BLEU), mur(40, 8.5, 40, 10, h, pal=MUR_BLEU)]
    v += [mur(4, 0, 4, 4, h), mur(40, 0, 40, 4, h), mur(4, 10, 4, P, h), mur(40, 10, 40, P, h)]
    s.volumes(v)
    for x0 in range(8, L - 4, 4):
        for (y0, a0, a1) in ((5.5, 0, -70), (8.5, 0, 70)):
            s.arc_sol((x0 + 1.2, y0), 1.0, a0, a1, 0, "#B45309", 1.2)
    for x0 in range(8, L - 8, 4):
        s.boite(x0 + 0.7, 1.0, 0, 2.4, 2.0, 0.5, ("#FFFFFF", "#E5E7EB", "#D1D5DB"), ep=1)
        s.boite(x0 + 0.7, 11.0, 0, 2.4, 2.0, 0.5, ("#FFFFFF", "#E5E7EB", "#D1D5DB"), ep=1)
    s.ufr(*s.p(38, 11, 0.6), 32)
    s.cote((20, 5.5, 0), (20, 8.5, 0), "2 UP", rappel=False, dx_txt=40, dy_txt=-12)
    s.repere((14, 8.5, 0.8), "portes donnant sur les dégagements\ndes chambres : ferme-porte", du=40, dv=260, couleur="#B45309", taille=17)
    s.repere((6, 2.5, 1.2), "lingerie, réserve, bagagerie :\nlocal à risques moyens", du=120, dv=-160, couleur=ROUGE, taille=17)
    s.repere((38, 11, 1.2), "chambre adaptée pouvant être traitée\nen espace d'attente sécurisé (O 9 § 2)", du=180, dv=150, couleur=BLEU, taille=17)
    s.repere((2, 7, 1.2), "escaliers protégés\n(sauf R+1, ≤ 100 pers. à l'étage)", du=-60, dv=190, couleur=BLEU, taille=17)
    s.bandeau([
        ("Effectif : nombre de personnes pouvant occuper les chambres (O 2). Distribution par secteurs autorisée : baies accessibles ouvrant", 18, TRAIT),
        ("sur une circulation ouverte au public (O 3). Gaz des cuisines de chambres et offices d'étage : distribution collective uniquement (O 13).", 18, TRAIT),
        ("Les articles AM 4 à AM 7 et AM 9 à AM 14 ne s'appliquent pas à l'intérieur des chambres ; appareils à éthanol interdits en chambre (O 10).", 18, TRAIT),
    ])
    return s
