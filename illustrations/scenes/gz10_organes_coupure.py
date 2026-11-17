"""GZ 10, GZ 11, GZ 14 — Organes de coupure du gaz, ventilation des locaux."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "GZ10_organes-coupure-gaz",
    "titre": "Organes de coupure du gaz",
    "articles": ["ERP:GZ 10", "ERP:GZ 11", "ERP:GZ 14", "ERP:GZ 7"],
    "fiche": "GZ 2",
    "legende": "Organe de coupure de branchement en limite de propriété (posé par le distributeur), puis organes de coupure au niveau des bâtiments, des sites de production d'énergie, des locaux et des appareils : commande accessible, simple et identifiée. Air de combustion pris à l'extérieur, produits de combustion évacués dehors.",
    "ecarts": [
        "Le chapitre GZ a été entièrement réécrit (arrêté du 23 novembre 2015 et suivants) : les règles chiffrées des anciennes fiches (stockages de propane et butane, distances, sections de ventilation, détendeurs) relèvent désormais des guides professionnels reconnus visés à l'article GZ 3, et non plus du règlement.",
    ],
}

JAUNE = "#EAB308"
ROUGE = "#C1121F"


def vanne(s, pt, taille=16):
    u, v = s.p(*pt)
    s.items.append(f'<path d="M{u - taille},{v - taille * 0.6} L{u + taille},{v + taille * 0.6} L{u + taille},{v - taille * 0.6} L{u - taille},{v + taille * 0.6} Z" fill="{ROUGE}" stroke="{TRAIT}" stroke-width="2"/>')
    s.items.append(f'<line x1="{u}" y1="{v}" x2="{u}" y2="{v - taille * 1.3}" stroke="{TRAIT}" stroke-width="3"/><line x1="{u - 9}" y1="{v - taille * 1.3}" x2="{u + 9}" y2="{v - taille * 1.3}" stroke="{TRAIT}" stroke-width="4"/>')


def dessiner():
    s = Scene(1600, 1160, echelle=28, origine=(600, 230))
    s.cartouche("Organes de coupure du gaz", "De la limite de propriété jusqu'aux appareils — ERP", "GZ 10 · GZ 11")
    s.sol(-4, -4, 40, 30, VERT_GAZON, trait=None)
    s.sol(-4, 22, 40, 4, ENROBE, ep=1.2)
    s.ligne((-4, 21.5, 0), (36, 21.5, 0), "#9CA3AF", 2, "10 6")         # limite de propriété
    # canalisation enterrée du réseau puis branchement
    s.ligne((-4, 24, 0), (36, 24, 0), JAUNE, 6)
    s.ligne((6, 24, 0), (6, 14, 0), JAUNE, 6)
    s.boite(5.2, 20.6, 0, 1.6, 0.8, 1.2, ("#FEF9C3", "#FDE047", "#CA8A04"), ep=1.6)       # coffret en limite
    vanne(s, (6, 21.0, 1.4))
    # bâtiment en écorché (murs bas)
    L, P, h = 26, 14, 2.4
    s.sol(0, 0, L, P, SOL_INT, ep=1.4)
    s.volumes([dict(x=-0.25, y=0, z=0, dx=0.25, dy=P, dz=h, pal=MUR), dict(x=0, y=-0.25, z=0, dx=L, dy=0.25, dz=h, pal=MUR),
               dict(x=0, y=P - 0.25, z=0, dx=L, dy=0.25, dz=0.6, pal=MUR), dict(x=L - 0.25, y=0, z=0, dx=0.25, dy=P, dz=0.6, pal=MUR),
               dict(x=12, y=0, z=0, dx=0.25, dy=P, dz=h, pal=MUR_PF), dict(x=0, y=7, z=0, dx=12, dy=0.25, dz=h, pal=MUR)])
    # réseau intérieur
    s.ligne((6, 14, 0.8), (6, 10, 2.2), JAUNE, 5)
    s.ligne((6, 10, 2.2), (6, 3, 2.2), JAUNE, 5)
    s.ligne((6, 10, 2.2), (20, 10, 2.2), JAUNE, 5)
    vanne(s, (6, 13.2, 1.1))
    # chaufferie (site de production d'énergie)
    s.boite(1.5, 1.2, 0, 3, 2.2, 1.8, ("#E5E7EB", "#D1D5DB", "#9CA3AF"), ep=1.6)
    s.boite(2.6, 1.6, 1.8, 0.6, 0.6, 1.4, ("#D1D5DB", "#9CA3AF", "#6B7280"), ep=1.4)          # conduit de fumées
    s.ligne((6, 3, 2.2), (4.5, 2.3, 1.2), JAUNE, 4)
    vanne(s, (6, 4.6, 2.2))
    # cuisine : appareils avec robinet + arrêt d'urgence
    for x in (15, 18.5):
        s.boite(x, 10.6, 0, 2.6, 1.6, 0.9, ("#D1D5DB", "#9CA3AF", "#6B7280"), ep=1.4)
        s.ligne((x + 1.3, 10, 2.2), (x + 1.3, 10.6, 0.9), JAUNE, 4)
        vanne(s, (x + 1.3, 10.3, 1.6), 11)
    vanne(s, (13.2, 10, 2.2))
    # ventilation
    s.poly([(0, 2, 0.2), (0, 3.2, 0.2), (0, 3.2, 0.7), (0, 2, 0.7)], "#DBEAFE", trait="#2563EB", ep=2)
    s.chemin([(-2.4, 2.6, 0.45), (1.0, 2.6, 0.45)], "#2563EB", 4)
    s.icone("fumee_01", (2.9, 1.9, 3.2), 60, ancre=(0.5, 0.95))

    s.repere((6, 21.0, 1.6), "organe de coupure de branchement\nen limite de propriété (distributeur)", du=240, dv=110, couleur=ROUGE, taille=16)
    s.repere((6, 13.2, 1.3), "organe de coupure du bâtiment", du=60, dv=250, couleur=ROUGE, taille=16)
    s.repere((6, 4.6, 2.4), "organe du site de production\nd'énergie (chaufferie)", du=-330, dv=-60, couleur=ROUGE, taille=16)
    s.repere((13.2, 10, 2.4), "organe du local (cuisine) ou\narrêt d'urgence à électrovanne (GC 4)", du=200, dv=-170, couleur=ROUGE, taille=16)
    s.repere((19.8, 10.3, 1.7), "robinet de chaque appareil", du=250, dv=-40, couleur=ROUGE, taille=16)
    s.repere((0, 2.6, 0.7), "air de combustion pris\nà l'extérieur (GZ 11)", du=-200, dv=120, couleur="#2563EB", taille=16)
    s.etiquette(*s.p(28, 21.5, 0), "limite de propriété", "#4B5563", 15, gras=False)

    s.bandeau([
        ("En cas d'urgence, l'alimentation en gaz doit pouvoir être interrompue sans retard : organes de coupure en nombre et en qualité suffisants,", 18, TRAIT),
        ("commande manuelle accessible, à manœuvre simple et clairement identifiée. Accès et signalisation de l'organe de branchement maintenus", 18, TRAIT),
        ("par le maire (domaine public) ou l'exploitant (domaine privé). Vérification technique annuelle des installations (GZ 15).", 18, TRAIT),
    ])
    return s
