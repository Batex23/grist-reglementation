"""Type X — X 2, X 4, X 5 : établissements sportifs couverts."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "X2_etablissements-sportifs",
    "titre": "Type X : établissements sportifs couverts",
    "articles": ["ERP:X 2", "ERP:X 4", "ERP:X 5", "ERP:X 1", "ERP:X 7", "ERP:X 15"],
    "fiche": "",
    "legende": "Effectif (sauf déclaration) : plus grande valeur entre 1 personne / 4 m² d'aire d'activité et 1 / 8 m² + spectateurs (tennis : 25 par court) ; patinoires 2 / 3 m² ou 1 / 10 m² + spectateurs ; piscines 1 / m² de plan d'eau ou 1 / 5 m² + spectateurs. Compartiments de 1 600 m² au plus ; mezzanine de spectateurs sur un seul niveau : pas un étage.",
    "ecarts": [
        "Couvertures à plus de 8 m d'un tiers ou de la limite de parcelle : M 3 admis (M 2 sur 3 m au-dessus du sol) ; plafonds des grands volumes M 3, résilles bois interdites (X 7, X 15). Pédiluves de 0,15 m au plus (X 8).",
    ],
}

ROUGE = "#C1121F"


def dessiner():
    s = Scene(1600, 1160, echelle=15, origine=(560, 250))
    s.cartouche("Type X : établissements sportifs couverts", "Salle omnisports avec gradins", "X 2 · X 4 · X 5")
    h = 9
    L, P = 44, 28
    s.sol(-2, -2, L + 4, P + 4, "#E5E7EB", trait=None)
    s.sol(0, 0, L, P, "#E9D8B4", ep=1.4)
    s.sol(4, 4, 36, 18, "#D7A86E", ep=1.6)                    # aire d'activité
    for (a, b) in (((4, 13), (40, 13)),):
        s.ligne((a[0], a[1], 0.01), (b[0], b[1], 0.01), "#FFFFFF", 2)
    s.poly([(22, 4, 0.01), (22, 22, 0.01)], "none", trait="#FFFFFF", ep=2)
    s.volumes([mur(0, 0, 0, P, h, ep=0.4), mur(0, 0, L, 0, h, ep=0.4)])
    # gradins côté avant
    for k in range(5):
        s.boite(4, 23 + k, 0, 36, 1, 0.45 * (k + 1), ("#E5E7EB", "#D1D5DB", "#9CA3AF"), ep=1)
    for x in range(6, 40, 3):
        s.personne((x, 24.5 + (x % 3), 0.45 * (2 + x % 3)), 20, 1 + x % 4, x % 2 == 0)
    for (x, y) in [(10, 8), (16, 15), (28, 10), (34, 17)]:
        s.personne((x, y, 0), 28, 5 + x % 3, x % 2 == 1)
    u, v = s.p(22, 13, 0); s.pastille(u, v, "aire d'activité sportive", "#92400E", taille=16)
    s.repere((30, 6, 0), "1 pers. / 4 m² d'aire d'activité\nou 1 pers. / 8 m² + spectateurs", du=240, dv=-170, couleur=ROUGE, taille=16)
    s.repere((22, 26, 1.8), "spectateurs : places assises\n(ou 0,50 m de banc, 3 / m² debout)", du=-40, dv=210, couleur="#374151", taille=16)
    x0, y0 = 40, 720
    s.items.append(f'<rect x="{x0}" y="{y0}" width="620" height="230" rx="10" fill="#FFFFFF" stroke="#9CA3AF" stroke-width="1.5"/>')
    s.texte(x0 + 20, y0 + 32, "Effectif selon l'activité (plus grande valeur)", 18, TRAIT, gras=True)
    for i, (a, b) in enumerate([("salles omnisports, EPS", "1/4 m²  ou  1/8 m² + spect."), ("tennis", "25 par court"), ("patinoires", "2/3 m²  ou  1/10 m² + spect."),
                                ("polyvalentes à dominante sportive", "1/m² + spectateurs"), ("piscines couvertes", "1/m² d'eau  ou  1/5 m² + spect.")]):
        s.texte(x0 + 20, y0 + 70 + 32 * i, a, 16, TRAIT)
        s.texte(x0 + 600, y0 + 70 + 32 * i, b, 16, ROUGE, gras=True, ancre="end")
    s.bandeau([
        ("Assujettis : 100 personnes en sous-sol ou en étages, 200 au total, pour les établissements clos et couverts à vocation sportive (X 1).", 18, TRAIT),
        ("Secteurs et compartiments autorisés, compartiment de 1 600 m² au plus (X 4) ; mezzanines de spectateurs sur un seul niveau non comptées comme étage (X 5).", 18, TRAIT),
        ("Salles polyvalentes à dominante sportive de 1 200 m² et plus, ou de moins de 6,50 m sous plafond : type L.", 18, TRAIT),
    ])
    return s
