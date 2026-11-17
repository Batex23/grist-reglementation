"""Type L — L 3, L 20, L 28 : salles, effectif et rangées de sièges."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "L28_rangees-sieges",
    "titre": "Type L : salles et rangées de sièges",
    "articles": ["ERP:L 28", "ERP:L 20", "ERP:L 3", "ERP:L 22", "ERP:L 29"],
    "fiche": "",
    "legende": "Rangées : 16 sièges au plus entre deux circulations (8 si une seule) avec un passage de 0,35 m, ou jusqu'à 50 sièges (gabarit de +2 cm par siège, 0,60 m au plus, sièges fixés, sorties majorées d'un tiers). Circulations de 0,60 m au moins entre les ensembles de sièges ; pente des circulations jusqu'à 15 %.",
    "ecarts": [
        "La règle des 16 sièges et du passage de 0,35 m vient de l'article AM 18 auquel renvoie L 28 § 1 a.",
        "Effectif : sièges ou places numérotées, 1 personne par 0,50 m de banc, 3 pers./m² debout, 5 par mètre de file d'attente ; réunion sans spectacle et polyvalente : 1 pers./m² ; cabaret : 4 pers. pour 3 m² (L 3). Sièges mobiles interdits en salle (L 29).",
    ],
}

ROUGE = "#C1121F"
SIEGE = ("#F87171", "#DC2626", "#991B1B")


def dessiner():
    s = Scene(1600, 1160, echelle=30, origine=(660, 230))
    s.cartouche("Type L : salles et rangées de sièges", "Salles d'audition, de conférences, de spectacles", "L 20 · L 28")
    L, P = 26, 18
    s.sol(-1, -1, L + 2, P + 2, "#E5E7EB", trait=None)
    s.sol(0, 0, L, P, "#FBF8F2", ep=1.4)
    s.sol(0, 0, L, 3, "#E5E7EB", ep=1.2)                       # scène
    s.boite(0, 0, 0, L, 3, 0.8, ("#D6C3A5", "#C4A57C", "#9C7F57"), ep=1.6)
    s.volumes([mur(0, 0, 0, P, 1.0), mur(0, P, 6, P, 1.0), mur(9, P, 17, P, 1.0), mur(20, P, L, P, 1.0), mur(L, 0, L, P, 1.0)])
    pas = 0.9
    blocs = [(1.0, 8, "8 max\n(une seule circulation)"), (9.0, 16, "16 entre deux circulations"), (24.4 - 8 * 0.5, 0, "")]
    def rangee(x0, n, y):
        for k in range(n):
            s.boite(x0 + k * 0.5, y, 0, 0.45, 0.5, 0.45, SIEGE, ep=0.8)
            s.boite(x0 + k * 0.5, y + 0.45, 0, 0.45, 0.12, 0.9, SIEGE, ep=0.8)
    for r in range(10):
        y = 4.5 + r * pas
        rangee(1.0, 8, y)        # rangée desservie par une seule circulation (côté mur)
        rangee(6.0, 16, y)
        rangee(16.6 + 0, 8, y) if False else rangee(16.6, 16, y) if False else None
    for r in range(10):
        y = 4.5 + r * pas
        for k in range(8):
            s.boite(16.6 + k * 0.5, y, 0, 0.45, 0.5, 0.45, SIEGE, ep=0.8)
            s.boite(16.6 + k * 0.5, y + 0.45, 0, 0.45, 0.12, 0.9, SIEGE, ep=0.8)
    s.cote((6.0, 13.6, 0), (14.0, 13.6, 0), "16 sièges", decal=(0, 1.6, 0), dy_txt=22)
    s.cote((1.0, 13.6, 0), (5.0, 13.6, 0), "8 max", decal=(0, 1.6, 0), dy_txt=22)
    s.cote((5.0, 9, 0), (6.0, 9, 0), "≥ 0,60 m", decal=(0, 0, 0), rappel=False, dy_txt=-40, dx_txt=-30)
    s.repere((10, 8.6, 0.45), "passage libre ≥ 0,35 m entre rangées\n(gabarit 0,35 × 1,20 m)", du=330, dv=-220, couleur=ROUGE, taille=17)
    s.repere((1, 9, 0.5), "rangée desservie par une seule\ncirculation : 8 sièges au plus", du=-200, dv=-200, couleur=ROUGE, taille=17)
    s.repere((7.5, 17, 0), "sorties selon l'effectif\n(CO 38, majorées d'⅓ si > 16 sièges)", du=80, dv=170, couleur="#15803D", taille=17)

    x0, y0 = 1050, 720
    s.items.append(f'<rect x="{x0}" y="{y0}" width="510" height="240" rx="10" fill="#FFFFFF" stroke="#9CA3AF" stroke-width="1.5"/>')
    s.texte(x0 + 20, y0 + 32, "Jusqu'à 50 sièges par rangée (L 28 § 1 b)", 18, TRAIT, gras=True)
    for i, t in enumerate(["gabarit + 2 cm par siège ajouté (0,60 m max),", "sièges fixés au sol, rangée de largeur constante ;", "sorties et unités de passage majorées d'⅓,", "sorties de 3 UP au moins ;", "> 700 places : circulation de 2 UP parallèle ;", "> 1 500 places : blocs de 700 ceinturés de 2 UP."]):
        s.texte(x0 + 20, y0 + 64 + 28 * i, t, 16, TRAIT)
    s.bandeau([
        ("Sièges fixes disposés en ensembles desservis par des dégagements de 0,60 m au moins (L 20) ; sièges en bordure alignés sur les", 18, TRAIT),
        ("dégagements ; strapontins à repli automatique laissant 0,60 m libre (L 28 § 3-4). Pente des circulations jusqu'à 15 %, au-delà paliers (L 22).", 18, TRAIT),
        ("Établissement regroupant plusieurs salles : chaque salle de plus de 200 personnes a un dégagement de 2 UP sur l'extérieur (L 23).", 18, TRAIT),
    ])
    return s
