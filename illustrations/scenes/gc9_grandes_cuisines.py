"""GC 1, GC 4, GC 9 à GC 11 — Grandes cuisines isolées et ouvertes."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "GC9_grandes-cuisines",
    "titre": "Grandes cuisines",
    "articles": ["ERP:GC 9", "ERP:GC 1", "ERP:GC 4", "ERP:GC 10", "ERP:GC 11"],
    "fiche": "GC 1",
    "legende": "Plus de 20 kW de cuisson : grande cuisine. Isolée : local à risques moyens (CF 1 h), portes va-et-vient vers la salle PF ½ h / E 30. Ouverte : écran E 15 de 0,50 m au moins sous plafond, cuisine et salle classées à risques moyens, extraction mécanique tenant 400 °C pendant 1 h. Arrêt d'urgence de l'énergie dans le local.",
    "ecarts": [
        "L'ancienne fiche (1996) mentionnait la mise en dépression de la cuisine ouverte et un écran M 0 SF ¼ h : le texte actuel exige un écran stable au feu ¼ h ou E 15-S en M 1 ou A2-s1, d1, et une extraction mécanique à commande manuelle « évacuation de fumées ».",
        "Distance de 0,50 m aux parois (sauf revêtement M 0 / A2-s1, d1) ; appareils marqués CE : préconisations du fabricant (GC 5).",
    ],
}

ROUGE = "#C1121F"
ORANGE = "#B45309"


def plan_cuisine(s, ox, oy, ouverte):
    s.ox, s.oy = ox, oy
    h = 2.8
    s.sol(0, 0, 14, 10, SOL_INT, ep=1.4)
    s.sol(0, 0, 6, 10, "#E5E7EB", ep=1.2)                         # cuisine
    v = [dict(x=-0.25, y=0, z=0, dx=0.25, dy=10, dz=h, pal=MUR_PF), dict(x=0, y=-0.25, z=0, dx=14, dy=0.25, dz=h, pal=MUR_PF if not ouverte else MUR)]
    if ouverte:
        v.append(dict(x=5.9, y=0, z=h - 0.5, dx=0.2, dy=10, dz=0.5, pal=("#FDE68A", "#FCD34D", "#F59E0B")))
    else:
        v += [dict(x=5.85, y=0, z=0, dx=0.3, dy=4, dz=h, pal=MUR_PF), dict(x=5.85, y=5.6, z=0, dx=0.3, dy=4.4, dz=h, pal=MUR_PF)]
    s.volumes(v)
    # bloc de cuisson et hotte
    s.boite(0.6, 1.0, 0, 1.6, 7, 0.9, ("#D1D5DB", "#9CA3AF", "#6B7280"), ep=1.6)
    s.boite(0.3, 0.8, 2.1, 2.2, 7.4, 0.5, ("#E5E7EB", "#D1D5DB", "#9CA3AF"), ep=1.6)
    s.boite(1.0, 4.0, 2.6, 0.6, 0.6, h - 2.6 + 0.6, ("#E5E7EB", "#D1D5DB", "#9CA3AF"), ep=1.4)
    if not ouverte:
        s.arc_sol((6, 4), 1.6, 90, 30, 0, ORANGE, 1.4); s.arc_sol((6, 4), 1.6, 90, 150, 0, ORANGE, 1.4)
    for (x, y) in [(9, 3), (11.5, 3), (9, 7), (11.5, 7)]:
        s.boite(x - 0.6, y - 0.6, 0, 1.2, 1.2, 0.75, ("#E7D3B5", "#D4B88E", "#B89468"), ep=1.2)
    s.personne((3.2, 6, 0), 30, 2); s.personne((10.2, 5, 0), 30, 6, True)
    # arrêt d'urgence près de l'accès / du bloc cuisson
    s.poly([(0, 8.8, 1.2), (0, 9.4, 1.2), (0, 9.4, 1.7), (0, 8.8, 1.7)], "#FDE047", trait=TRAIT, ep=1.4)
    u, v_ = s.p(0, 9.1, 1.45); s.items.append(f'<circle cx="{u:.1f}" cy="{v_:.1f}" r="5" fill="{ROUGE}"/>')


def dessiner():
    s = Scene(1600, 1160, echelle=30, origine=(0, 0))
    s.cartouche("Grandes cuisines", "Appareils de cuisson de plus de 20 kW : cuisine isolée ou ouverte sur la salle", "GC 9 · GC 10 · GC 11")
    plan_cuisine(s, 440, 390, False)
    s.texte(60, 128, "Grande cuisine isolée", 22, TRAIT, gras=True)
    s.repere((0, 5, 2.8), "local à risques moyens :\nparois et plancher haut CF 1 h\n(CO 28 § 2)", du=-60, dv=-150, couleur=ORANGE, taille=16)
    s.repere((6, 4.8, 2.2), "portes va-et-vient vers la salle\nPF ½ h ou E 30", du=180, dv=190, couleur=ORANGE, taille=16)
    s.repere((1.4, 4.5, 2.6), "hotte M 0 / A2-s1, d0, filtres à graisses,\nconduits métalliques CF 60 min\nhors du volume de la cuisine", du=40, dv=330, couleur="#4B5563", taille=16)
    plan_cuisine(s, 1200, 390, True)
    s.texte(840, 128, "Grande cuisine ouverte", 22, TRAIT, gras=True)
    s.ox, s.oy = 1200, 390
    s.repere((6, 6, 2.55), "écran fixe ≥ 0,50 m sous plafond\nE 15 (SF ¼ h), M 1 / A2-s1, d1", du=230, dv=-110, couleur="#B45309", taille=16)
    s.repere((1.3, 4.3, 3.3), "extraction mécanique : 1 h à 400 °C,\ncommande manuelle « évacuation\nde fumées », câbles CR 1", du=-180, dv=-150, couleur=ROUGE, taille=16)
    s.repere((10, 8, 0), "cuisine + salle :\nvolume à risques moyens", du=120, dv=150, couleur=ORANGE, taille=16)
    s.ox, s.oy = 440, 390
    s.repere((0, 9.1, 1.6), "arrêt d'urgence de l'énergie\ndans le local, près de l'accès\nou du bloc cuisson (GC 4)", du=20, dv=170, couleur=ROUGE, taille=16)
    s.bandeau([
        ("Grande cuisine : locaux non isolés entre eux comportant plus de 20 kW de puissance utile d'appareils de cuisson et de remise en température.", 18, TRAIT),
        ("Arrêt d'urgence par énergie : il ne coupe ni l'éclairage ni la ventilation participant à l'évacuation des fumées ; électrovanne gaz", 18, TRAIT),
        ("à réarmement manuel admise, commande commune possible ; consignes de réutilisation des brûleurs affichées à proximité.", 18, TRAIT),
        ("Office de remise en température et îlots de cuisson : sections III et IV du chapitre GC.", 17, "#4B5563"),
    ])
    return s
