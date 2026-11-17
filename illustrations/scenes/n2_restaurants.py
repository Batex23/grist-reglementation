"""Type N — N 2, N 5, N 7 : restaurants."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "N2_restaurants",
    "titre": "Type N : restaurants et débits de boissons",
    "articles": ["ERP:N 2", "ERP:N 5", "ERP:N 7", "ERP:N 6", "ERP:N 3"],
    "fiche": "",
    "legende": "Effectif : places assises déclarées (1 personne pour 2 m² au plus) ou à défaut 1 pers./m² ; debout 2 pers./m² ; files d'attente 3 pers./m². Salle bordant un hall : parois incombustibles sans exigence de résistance au feu, retombée de 0,50 m formant écran de cantonnement. Circulations secondaires de 0,60 m mesurées sièges occupés.",
    "ecarts": [
        "Le calcul « déclaration contrôlée, 1 pers./2 m² au plus » remplace l'ancien forfait d'1 personne par m² en restauration assise, qui reste la règle à défaut de déclaration.",
        "Seuls les dégagements accessoires peuvent être communs avec des tiers (N 6). Bougies admises seulement dans les salles, sur supports stables et incombustibles (N 12).",
    ],
}

ROUGE = "#C1121F"


def dessiner():
    s = Scene(1600, 1160, echelle=26, origine=(600, 230))
    s.cartouche("Type N : restaurants et débits de boissons", "Effectif, salle sur hall et circulations", "N 2 · N 5 · N 7")
    h = 2.8
    L, P = 26, 16
    s.sol(-1, -1, L + 2, P + 2, "#E5E7EB", trait=None)
    s.sol(0, 0, 18, P, "#FBF3E4", ep=1.4)          # salle assise
    s.sol(18, 0, 8, 8, "#FEE2E2", ep=1.2)           # bar debout
    s.sol(18, 8, 8, 8, "#EDE9FE", ep=1.2)           # hall
    s.volumes([mur(0, 0, L, 0, h), mur(0, 0, 0, P, h)])
    # retombée de 0,50 m entre salle et hall
    s.boite(17.9, 8, h - 0.5, 0.2, 8, 0.5, ("#FDE68A", "#FCD34D", "#F59E0B"), ep=1.6)
    s.boite(17.9, 0, h - 0.5, 0.2, 8, 0.5, ("#FDE68A", "#FCD34D", "#F59E0B"), ep=1.6, opacite=0.4)
    for x in (2, 6, 10, 14):
        for y in (2, 6, 10, 13.5):
            s.boite(x, y, 0, 1.4, 1.4, 0.75, ("#E7D3B5", "#D4B88E", "#B89468"), ep=1.1)
            for (dx, dy) in ((-0.55, 0.45), (1.55, 0.45)):
                s.boite(x + dx, y + dy, 0, 0.4, 0.5, 0.45, ("#9CA3AF", "#6B7280", "#4B5563"), ep=0.8)
    s.boite(19, 1, 0, 6, 1, 1.1, ("#D6C3A5", "#C4A57C", "#9C7F57"), ep=1.4)   # comptoir
    for (x, y, k, f) in [(20, 4, 1, 0), (22, 5, 2, 1), (24, 3.5, 3, 0), (21, 11, 4, 1), (24, 13, 5, 0), (7.3, 7.5, 6, 1)]:
        s.personne((x, y, 0), 30, k, bool(f))
    s.cote((3.4, 3.4, 0), (5.45, 3.4, 0), "", rappel=False)
    s.repere((4.4, 3.6, 0), "circulation secondaire ≥ 0,60 m\n(sièges en position d'occupation)", du=-280, dv=-110, couleur=ROUGE, taille=16)
    s.repere((18, 12, h - 0.25), "retombée ≥ 0,50 m formant écran\nde cantonnement entre salle et hall", du=200, dv=-140, couleur="#B45309", taille=16)
    s.repere((18, 14, 1.0), "parois éventuelles incombustibles,\nsans exigence de résistance au feu", du=220, dv=70, couleur="#4B5563", taille=16)
    u, v = s.p(9, 16, 0); s.pastille(u - 40, v + 50, "assis : 1 pers. / 2 m² max (déclaration) · sinon 1 / m²", "#B45309", taille=15)
    u, v = s.p(22, 4, 0); s.pastille(u + 90, v + 40, "debout : 2 pers. / m²", ROUGE, taille=15)
    u, v = s.p(22, 12, 0); s.pastille(u + 60, v + 70, "file d'attente : 3 pers. / m²", "#6D28D9", taille=15)
    s.bandeau([
        ("Effectif calculé déduction faite des estrades des musiciens et des aménagements fixes autres que tables et sièges ; capacité par niveau.", 18, TRAIT),
        ("Salles bordant un hall sans exigence de résistance au feu si parois incombustibles et si le hall ne dessert pas directement les dégagements", 18, TRAIT),
        ("des étages (ou cuisine isolée selon GC 9). Distribution par secteurs autorisée (N 3). Vestiaires hors des chemins de circulation (N 8).", 18, TRAIT),
    ])
    return s
