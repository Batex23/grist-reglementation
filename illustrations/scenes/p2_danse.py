"""Type P — P 2, P 4, P 9, P 17 : salles de danse et de jeux."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "P2_salles-de-danse",
    "titre": "Type P : salles de danse et de jeux",
    "articles": ["ERP:P 2", "ERP:P 4", "ERP:P 9", "ERP:P 17", "ERP:P 5"],
    "fiche": "",
    "legende": "Effectif : 4 personnes pour 3 m² de salle, déduction faite des estrades des musiciens et aménagements fixes autres que tables et sièges (billard : 4 par billard). Cloisonnement traditionnel seul autorisé. Vêtements suspendus le long d'une circulation : largeur majorée de 0,60 m. Bougies interdites.",
    "ecarts": [
        "Locaux à risques importants : stockage de disques et bandes non utilisés pendant la soirée ; risques moyens : réserves, articles de cotillons, offices, lingeries (P 5). Installations électriques BE 2 (P 16) ; chauffage électrique fixe à 100 °C de surface au plus (P 15).",
    ],
}

ROUGE = "#C1121F"


def dessiner():
    s = Scene(1600, 1160, echelle=30, origine=(720, 220))
    s.cartouche("Type P : salles de danse et de jeux", "Effectif et aménagements d'une salle de danse", "P 2 · P 9 · P 17")
    h = 3.2
    L, P = 24, 16
    s.sol(-1, -1, L + 2, P + 2, "#E5E7EB", trait=None)
    s.sol(0, 0, L, P, "#312E81", ep=1.4)
    s.sol(4, 3, 12, 9, "#4338CA", ep=1.2)                       # piste
    s.volumes([mur(0, 0, 0, P, h, ep=0.3), mur(0, 0, L, 0, h, ep=0.3)])
    s.boite(17, 1, 0, 6, 2, 0.6, ("#A78BFA", "#7C3AED", "#5B21B6"), ep=1.4)        # estrade DJ (déduite)
    s.boite(18, 6, 0, 5, 1.2, 1.1, ("#D6C3A5", "#C4A57C", "#9C7F57"), ep=1.4)       # bar (déduit)
    for x in range(6, 16, 2):
        for y in range(4, 12, 2):
            s.personne((x + (y % 3) * 0.3, y, 0), 22, 1 + (x + y) % 4, (x + y) % 3 == 0)
    # vestiaire le long d'une circulation
    s.sol(0, 13, 10, 3, "#6D28D9", trait=None)
    s.boite(0.2, 15.2, 0, 9.6, 0.6, 1.8, ("#FDE68A", "#F59E0B", "#B45309"), ep=1.2)
    s.cote((5, 13, 0), (5, 15.2, 0), "+ 0,60 m", rappel=False, dx_txt=60)
    s.repere((20, 2, 0.6), "estrade des musiciens et aménagements fixes\n(hors tables et sièges) : déduits de la surface", du=60, dv=-170, couleur="#7C3AED", taille=16)
    s.repere((10, 7.5, 0), "4 personnes pour 3 m²", du=-300, dv=-170, couleur=ROUGE, taille=18)
    s.repere((5, 15.5, 1.5), "vêtements suspendus le long d'une circulation :\nlargeur majorée de 0,60 m", du=-120, dv=200, couleur="#B45309", taille=16)
    s.bandeau([
        ("Effectif maximal : 4 personnes pour 3 m² de la surface de la salle (P 2) ; salles de billard : 4 personnes par billard + places réservées.", 18, TRAIT),
        ("Seul le cloisonnement traditionnel est autorisé ; l'atténuation de CO 15 ne s'applique pas aux salles de danse (P 4).", 18, TRAIT),
        ("Vestiaires hors des chemins de circulation et des escaliers (P 9). Bougies interdites (P 17). Éclairage de sécurité par source centralisée en 1re et 2e cat. (P 18).", 18, TRAIT),
    ])
    return s
