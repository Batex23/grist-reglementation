"""CH 41 à CH 43 — VMC : clapets ou fonctionnement permanent du ventilateur."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "CH42_vmc",
    "titre": "Ventilation mécanique contrôlée",
    "articles": ["ERP:CH 42", "ERP:CH 41", "ERP:CH 43"],
    "fiche": "CH 5",
    "legende": "La VMC ne doit pas propager feu et fumées : soit des dispositifs d'obturation (piquages PF ½ h / E 30 ou clapets CF au droit des planchers, autocommandés à 70 °C), soit le fonctionnement permanent du ventilateur (400 °C pendant ½ h, alimentation directe CR 1). Conduit collectif CF 60 min au plus, trappes PF ½ h.",
    "ecarts": [
        "VMC gaz interdite en ERP (CH 41 § 1) — l'ancienne fiche la mentionnait avec un dispositif de sécurité collectif.",
        "Conduits horizontaux : clapets CF ½ h (EI 30) au droit des parois entre secteurs, compartiments, zones de mise en sécurité et espaces d'attente sécurisés.",
    ],
}

ROUGE = "#C1121F"
BLEU = "#2563EB"


def dessiner():
    s = Scene(1600, 1160, echelle=38, origine=(560, 640))
    s.cartouche("Ventilation mécanique contrôlée", "Non-propagation du feu et des fumées par les conduits — ERP", "CH 41 à CH 43")
    hn, N = 3.0, 3
    s.sol(-1, -1, 12, 7, "#E5E7EB", trait=None)
    v = []
    for k in range(N):
        z = k * hn
        v.append(dict(x=0, y=0, z=z - 0.15 if k else 0, dx=9, dy=5, dz=0.3 if k else 0.05, pal=BETON, ep=1.4))
    v.append(dict(x=-0.25, y=0, z=0, dx=0.25, dy=5, dz=N * hn, pal=MUR))
    v.append(dict(x=0, y=-0.25, z=0, dx=9, dy=0.25, dz=N * hn, pal=MUR))
    s.volumes(v)
    # gaine collective verticale
    s.boite(6.8, 0, 0, 1.2, 1.0, N * hn + 1.2, ("#FDE2E2", "#F7B4B0", "#E8857E"), ep=1.8, opacite=0.55)
    s.boite(7.2, 0.3, 0, 0.4, 0.4, N * hn + 1.2, ("#E5E7EB", "#D1D5DB", "#9CA3AF"), ep=1.4)
    # caisson ventilateur en toiture
    s.boite(6.6, 0, N * hn + 1.2, 1.6, 1.2, 0.8, ("#D1D5DB", "#9CA3AF", "#6B7280"), ep=1.6)
    for k in range(N):
        z = k * hn + 2.3
        s.boite(3.0, 0.3, z, 3.8, 0.35, 0.35, ("#E5E7EB", "#D1D5DB", "#9CA3AF"), ep=1.2)     # piquage
        s.boite(6.5, 0.25, z - 0.05, 0.3, 0.45, 0.45, ("#FCA5A5", "#EF4444", "#B91C1C"), ep=1.4)  # dispositif PF ½ h
        s.poly([(3.0, 0.3, z), (3.0, 0.65, z), (3.0, 0.65, z + 0.35), (3.0, 0.3, z + 0.35)], "#FFFFFF", ep=1.4)
    s.chemin([(7.4, 0.5, N * hn + 2.0), (7.4, 0.5, N * hn + 3.2)], "#6B7280", 5)
    s.repere((6.65, 0.45, 2 * hn + 2.5), "dispositif PF ½ h (E 30) sur chaque\npiquage, ou clapet CF au droit de chaque\nplancher — autocommandé à 70 °C", du=320, dv=-80, couleur=ROUGE, taille=16)
    s.repere((7.4, 1.0, hn + 1.2), "conduit collectif + gaine : CF de traversée\n= planchers (60 min au plus),\ntrappes PF ½ h, conduits A2-s1, d0 / M 0", du=330, dv=60, couleur=ROUGE, taille=16)
    s.repere((7.4, 0.6, N * hn + 1.6), "ou ventilateur permanent : 400 °C ½ h,\nalimentation directe sélective CR 1\n(si pas de traversée de parois d'isolement\nni de local à risques moyens)", du=-420, dv=30, couleur=BLEU, taille=16)
    s.repere((3.0, 0.5, hn + 2.4), "bouche d'extraction\n(local à pollution spécifique)", du=-300, dv=30, couleur="#4B5563", taille=16)
    s.bandeau([
        ("Extraction de l'air uniquement dans les locaux à pollution spécifique ; conduits desservant des locaux accessibles au public interdits", 18, TRAIT),
        ("dans les locaux à risques importants ; conduits collectifs horizontaux ne traversant pas les locaux à sommeil.", 18, TRAIT),
        ("VMC inversée : pas de clapet dans les conduits collectifs, seulement sur les piquages. Raccordement d'appareils à gaz (VMC gaz) interdit.", 18, TRAIT),
    ])
    return s
