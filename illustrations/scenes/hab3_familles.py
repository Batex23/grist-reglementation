"""Habitation, arrêté du 31 janvier 1986, art. 3 et 5 — Classement en familles."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "HAB3_familles",
    "titre": "Familles d'habitation",
    "articles": ["HAB:3", "HAB:5"],
    "fiche": "",
    "legende": "1re famille : individuelles R+1 isolées ou jumelées, R en bande. 2e : individuelles plus hautes, collectifs jusqu'à R+3. 3e : plancher bas du logement le plus haut à 28 m au plus (A : R+7 max, 10 m palier–escalier, accès par voie échelles ; B sinon, escaliers à moins de 50 m d'une voie engins). 4e : jusqu'à 50 m. Structure SF ¼ h, ½ h, 1 h, 1 h ½.",
    "ecarts": [
        "Planche ajoutée : l'ancien recueil ne traitait que les ERP. Au-delà de 50 m : IGH (immeuble de grande hauteur).",
        "Collectif R+3 dont le plancher bas du logement le plus haut est à plus de 8 m : escaliers encloisonnés, sauf escaliers extérieurs (art. 3, 2°).",
    ],
}

ROUGE = "#C1121F"
H_NIV = 2.8


def maison(s, x, y, n, larg=6, prof=6, pal=BEIGE):
    s.boite(x, y, 0, larg, prof, n * H_NIV, pal, ep=1.8)
    s.fenetres_y(x, y + prof, 0, larg, n * H_NIV, 2, n, larg=0.9, haut=1.0)
    s.poly([(x, y, n * H_NIV), (x + larg, y, n * H_NIV), (x + larg, y + prof / 2, n * H_NIV + 2), (x, y + prof / 2, n * H_NIV + 2)], "#C2410C", ep=1.6)
    s.poly([(x, y + prof, n * H_NIV), (x + larg, y + prof, n * H_NIV), (x + larg, y + prof / 2, n * H_NIV + 2), (x, y + prof / 2, n * H_NIV + 2)], "#EA580C", ep=1.6)


def immeuble(s, x, y, n, larg=8, prof=8):
    s.boite(x, y, 0, larg, prof, n * H_NIV, GRIS, ep=1.8)
    s.fenetres_y(x, y + prof, 0, larg, n * H_NIV, 3, n, larg=1.0, haut=1.1)
    s.fenetres_x(x + larg, y, 0, prof, n * H_NIV, 3, n, larg=1.0, haut=1.1)


def dessiner():
    s = Scene(1600, 1160, echelle=8.4, origine=(60, 700))
    s.cartouche("Familles d'habitation", "Classement des bâtiments d'habitation — arrêté du 31 janvier 1986", "Art. 3 · art. 5")
    # les bâtiments sont alignés suivant (1, -1) : une ligne horizontale à l'écran
    pos = lambda d: (d, -d)
    s.poly([(0, 6, 0), (95, -89, 0), (105, -79, 0), (10, 16, 0)], VERT_GAZON, trait=None)
    x, y = pos(4); maison(s, x, y, 2)
    for k in range(3):
        x, y = pos(17 + 4.2 * k); maison(s, x, y, 1, larg=4, prof=6)
    x, y = pos(36); maison(s, x, y, 3)
    x, y = pos(47); immeuble(s, x, y, 4)
    x, y = pos(61); immeuble(s, x, y, 8, larg=9)
    x, y = pos(75); immeuble(s, x, y, 10, larg=9)
    x, y = pos(89); immeuble(s, x, y, 17, larg=9)
    for z, t in ((8, "8 m"), (28, "28 m"), (50, "50 m")):
        s.ligne((42, -36, z), (102, -96, z), "#6B7280", 1.6, "8 6")
        u, v = s.p(102, -96, z); s.texte(u + 10, v + 6, t, 17, "#374151", gras=True)
    fam = [(pos(9) + (11,), "1re famille", "R+1 isolée ou jumelée,\nR en bande · SF ¼ h", "#15803D"),
           (pos(40) + (17,), "2e famille", "individuelle > R+1,\ncollectif ≤ R+3 · SF ½ h", "#2563EB"),
           (pos(66) + (28,), "3e famille A / B", "logement le plus haut\n≤ 28 m · SF 1 h", "#B45309"),
           (pos(94) + (50,), "4e famille", "≤ 50 m · SF 1 h ½", ROUGE)]
    for (x, y, z), t, d, c in fam:
        u, v = s.p(x, y, z)
        s.pastille(u, v - 120, t, c, taille=17)
        s.etiquette(u, v - 72, d, c, 15, gras=False)
    s.texte(40, 890, "3e famille A : au plus R+7, porte palière la plus éloignée à 10 m au plus de l'escalier,", 18, TRAIT)
    s.texte(40, 916, "accès aux escaliers atteints par une voie échelles (art. 4). Sinon : 3e famille B.", 18, TRAIT)
    s.texte(40, 948, "3e famille B et 4e famille : accès aux escaliers à moins de 50 m d'une voie engins ;", 18, TRAIT)
    s.texte(40, 974, "colonnes sèches au-delà de R+7 (art. 98). Au-delà de 50 m : immeuble de grande hauteur.", 18, TRAIT)
    s.bandeau([
        ("Hauteurs mesurées au plancher bas du logement le plus haut, depuis le sol utilement accessible aux engins de secours.", 18, TRAIT),
        ("Maison individuelle : bâtiment sans logements superposés. Bande R+1 à structures indépendantes : 1re famille ; sinon 2e famille.", 18, TRAIT),
        ("Le maire peut soumettre la 3e famille B aux seules règles de la 3e A si les échelles aériennes du secteur atteignent le logement le plus haut.", 18, TRAIT),
    ])
    return s
