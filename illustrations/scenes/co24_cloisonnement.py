"""CO 24 § 1 — Cloisonnement traditionnel."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "CO24_cloisonnement-traditionnel",
    "titre": "Cloisonnement traditionnel",
    "articles": ["ERP:CO 24", "ERP:CO 23", "ERP:CO 26"],
    "fiche": "C.10",
    "legende": "Locaux séparés des dégagements par des parois dont le degré suit la stabilité de la structure ; blocs-portes PF ½ h (¼ h sans exigence de structure) ; circulations encloisonnées recoupées tous les 25 à 30 m par des portes PF ½ h à ferme-porte.",
    "ecarts": [
        "Le tableau des degrés de parois figure dans le texte de l'article (CO 24 § 1 a) ; il dépend du degré de stabilité exigé pour la structure.",
        "Parois construites de plancher à plancher ; combles et plénums recoupés en cellules de 300 m² au plus, 30 m de plus grande dimension (CO 26).",
    ],
}

ROUGE = "#C1121F"
ORANGE = "#B45309"


def dessiner():
    s = Scene(1600, 1160, echelle=18.5, origine=(250, 300))
    s.cartouche("Cloisonnement traditionnel", "Distribution intérieure par locaux et dégagements cloisonnés — ERP", "CO 24 § 1")
    L, P, h = 60, 14, 1.6
    s.sol(-3, -3, L + 6, P + 6, VERT_GAZON, trait=None)
    s.sol(0, 0, L, P, SOL_INT, ep=1.6)
    s.sol(4, 6, L - 8, 2, "#E9F3EA", ep=1.2)                 # circulation
    for xs in (0, L - 4):                                    # escaliers encloisonnés aux extrémités
        s.sol(xs, 5, 4, 4, "#D6E6F7", ep=1.2)
        for k in range(1, 7):
            s.ligne((xs + 0.2 + k * 0.55, 5.4, 0), (xs + 0.2 + k * 0.55, 8.6, 0), "#5B7DB1", 1.2)
    v = [mur(0, 0, L, 0, h), mur(0, 0, 0, P, h), mur(L, 0, L, P, h), mur(0, P, L, P, h)]
    # cages d'escalier
    for xs in (0, L - 4):
        v += [mur(xs, 5, xs + 4, 5, h, pal=MUR_BLEU), mur(xs, 9, xs + 4, 9, h, pal=MUR_BLEU)]
    v += [mur(4, 5, 4, 6, h, pal=MUR_BLEU), mur(4, 8, 4, 9, h, pal=MUR_BLEU), mur(L - 4, 5, L - 4, 6, h, pal=MUR_BLEU), mur(L - 4, 8, L - 4, 9, h, pal=MUR_BLEU)]
    # parois des locaux sur circulation (avec portes) et refends
    largeur = (L - 8) / 8
    for i in range(8):
        x0 = 4 + i * largeur
        for yc, cote in ((6, -1), (8, 1)):
            v.append(mur(x0, yc, x0 + 1.2, yc, h, pal=MUR_PF))
            v.append(mur(x0 + 2.2, yc, x0 + largeur, yc, h, pal=MUR_PF))
        if i:
            v += [mur(x0, 0, x0, 6, h), mur(x0, 8, x0, P, h)]
    v += [mur(4, 0, 4, 5, h), mur(4, 9, 4, P, h), mur(L - 4, 0, L - 4, 5, h), mur(L - 4, 9, L - 4, P, h)]
    # recoupement de la circulation au milieu (porte PF ½ h à ferme-porte, va-et-vient)
    xr = 4 + 4 * largeur
    s.volumes(v)
    s.boite(xr - 0.15, 6, 0, 0.3, 2, 2.1, MUR_PF, ep=1.6, opacite=0.85)
    s.ligne((xr, 6, 0), (xr, 8, 0), ORANGE, 3)
    for i in range(8):
        x0 = 4 + i * largeur
        s.arc_sol((x0 + 1.2, 6), 1.0, 0, -90, 0, ORANGE, 1.4)
        s.arc_sol((x0 + 1.2, 8), 1.0, 0, 90, 0, ORANGE, 1.4)

    s.chemin([(xr + 6, 7, 0.1), (L - 4.5, 7, 0.1)], "#15803D", 4.5)
    s.chemin([(xr - 6, 7, 0.1), (4.5, 7, 0.1)], "#15803D", 4.5)
    s.cote((4, 6, 0), (xr, 6, 0), "25 à 30 m", decal=(0, -9, 0), dy_txt=-22)
    s.repere((xr, 7, 2.1), "recoupement : bloc-porte PF ½ h\nà ferme-porte (va-et-vient si\nutilisé dans les deux sens)", du=40, dv=-180, couleur=ORANGE, taille=17)
    s.repere((4 + 6.5 * largeur, 8, 1.6), "parois locaux / dégagements :\ndegré selon la stabilité de la structure\nblocs-portes PF ½ h (¼ h si structure sans exigence)", du=70, dv=150, couleur=ORANGE, taille=17)
    s.repere((2, 7, 1.6), "escalier\nprotégé", du=-60, dv=-130, couleur="#1D4ED8", taille=17)

    s.legende(1150, 110, [(MUR_PF[1], "parois et portes résistant au feu"), ("#E9F3EA", "circulation horizontale encloisonnée"), ("#D6E6F7", "escalier protégé")], taille=16)
    s.bandeau([
        ("Parois des dégagements et des locaux : degré de résistance au feu fixé par le tableau de CO 24 § 1 a selon la stabilité exigée pour la structure.", 18, TRAIT),
        ("Pas d'exigence entre locaux non réservés au sommeil à l'intérieur d'un ensemble de locaux contigus de 300 m² au plus au même niveau.", 18, TRAIT),
        ("Blocs-portes et vitrages des parois : PF ½ h (PF ¼ h si aucune stabilité n'est exigée pour la structure).", 18, TRAIT),
        ("Circulations horizontales encloisonnées de grande longueur : recoupées tous les 25 à 30 m par des parois et blocs-portes PF ½ h à ferme-porte.", 18, TRAIT),
    ])
    return s
