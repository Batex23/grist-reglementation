"""CH 5 et CH 6 — Implantation des appareils de production de chaleur ou de froid par combustion."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "CH5_chaufferies",
    "titre": "Chaufferies et appareils à combustion",
    "articles": ["ERP:CH 5", "ERP:CH 6"],
    "fiche": "CH 1-1 à 1-3",
    "legende": "Plus de 70 kW : local à risques importants (CO 28 § 1) ; un seul accès direct par une circulation non accessible au public débouchant dehors, ou second accès par un sas à deux portes PF ½ h / E 30-C. De 30 à 70 kW : local non accessible au public, parois CF 1 h, porte CF ½ h à ferme-porte. Jusqu'à 30 kW : ventilation du local.",
    "ecarts": [
        "Les distances d'implantation des appareils à l'extérieur (8 m, 10 m, mur écran de 2 m…) relèvent désormais de l'article GZ 9 et des guides professionnels pour le gaz, ou de la notice du fabricant ; elles ne sont plus fixées par CH 5.",
        "Les seuils de l'ancienne fiche (20 kW / 70 kW) sont devenus 30 kW / 70 kW (CH 6).",
    ],
}

ROUGE = "#C1121F"
ORANGE = "#B45309"


def chaudiere(s, x, y):
    s.boite(x, y, 0, 1.4, 1.0, 1.6, ("#E5E7EB", "#D1D5DB", "#9CA3AF"), ep=1.6)
    s.boite(x + 0.5, y + 0.3, 1.6, 0.4, 0.4, 1.4, ("#D1D5DB", "#9CA3AF", "#6B7280"), ep=1.2)


def dessiner():
    s = Scene(1600, 1160, echelle=36, origine=(0, 0))
    s.cartouche("Chaufferies et appareils à combustion", "Implantation selon la puissance utile totale — ERP", "CH 5 · CH 6")
    # --- > 70 kW
    s.ox, s.oy = 420, 400
    s.texte(40, 130, "Puissance utile > 70 kW", 22, TRAIT, gras=True)
    h = 2.6
    s.sol(-1, -1, 14, 11, "#E5E7EB", trait=None)
    s.sol(0, 0, 6, 6, "#FCE3E1", ep=1.2)            # chaufferie
    s.sol(6, 0, 6, 3, "#F3F4F6", ep=1.2)            # sas
    s.sol(0, 6, 12, 3, "#E9F3EA", ep=1.2)           # circulation non accessible au public
    v = [dict(x=-0.3, y=0, z=0, dx=0.3, dy=9, dz=h, pal=MUR_CF), dict(x=0, y=-0.3, z=0, dx=12, dy=0.3, dz=h, pal=MUR_CF),
         dict(x=5.85, y=0, z=0, dx=0.3, dy=0.8, dz=h, pal=MUR_CF), dict(x=5.85, y=2.2, z=0, dx=0.3, dy=3.8, dz=h, pal=MUR_CF),
         dict(x=0, y=5.85, z=0, dx=2, dy=0.3, dz=h, pal=MUR_CF), dict(x=3.4, y=5.85, z=0, dx=2.6, dy=0.3, dz=h, pal=MUR_CF),
         dict(x=6, y=2.85, z=0, dx=1.5, dy=0.3, dz=h, pal=MUR_CF), dict(x=8.9, y=2.85, z=0, dx=3.1, dy=0.3, dz=h, pal=MUR_CF)]
    s.volumes(v)
    chaudiere(s, 1.2, 1.2); chaudiere(s, 3.4, 1.2)
    s.vantail((2, 6), 1.3, 60, 2.1, "#E8A39C")
    s.vantail((6, 0.8), 1.3, 60, 2.0, "#E8A39C")
    s.vantail((7.5, 3), 1.3, 60, 2.0, "#E8A39C")
    s.repere((0, 3, h), "local à risques importants :\nparois et plancher haut CF 2 h\n(CO 28 § 1, GZ 9 si gaz)", du=-120, dv=-150, couleur=ROUGE, taille=15)
    s.repere((2.7, 6, 1.5), "accès unique par une circulation\nnon accessible au public, débouchant\ndehors ou sur un hall au niveau d'évacuation", du=40, dv=210, couleur="#15803D", taille=15)
    s.repere((7.5, 1.6, 1.4), "second accès : sas, deux portes\nPF ½ h (E 30-C) à ferme-porte,\nouvrant vers la sortie", du=220, dv=-170, couleur=ORANGE, taille=15)
    u, v_ = s.p(10, 1.5, 0); s.pastille(u + 50, v_ + 20, "local accessible au public", "#4B5563", taille=13)
    # --- 30 à 70 kW
    s.ox, s.oy = 1230, 420
    s.texte(860, 130, "De 30 à 70 kW (hors gaz)", 22, TRAIT, gras=True)
    s.sol(-1, -1, 8, 8, "#E5E7EB", trait=None)
    s.sol(0, 0, 5, 5, "#FFF1DC", ep=1.2)
    s.volumes([dict(x=-0.3, y=0, z=0, dx=0.3, dy=5, dz=h, pal=MUR_PF), dict(x=0, y=-0.3, z=0, dx=5, dy=0.3, dz=h, pal=MUR_PF),
               dict(x=0, y=4.85, z=0, dx=2, dy=0.3, dz=h, pal=MUR_PF), dict(x=3.3, y=4.85, z=0, dx=1.7, dy=0.3, dz=h, pal=MUR_PF),
               dict(x=4.85, y=0, z=0, dx=0.3, dy=5, dz=h, pal=MUR_PF)])
    chaudiere(s, 1.5, 1.2)
    s.vantail((2, 5), 1.2, 60, 2.0, "#F7C27A")
    s.repere((0, 2.5, h), "non accessible au public,\npas de dépôt combustible,\nparois et plancher CF 1 h (A2-s3, d0)", du=-150, dv=-160, couleur=ORANGE, taille=15)
    s.repere((2.6, 5, 1.5), "porte CF ½ h (EI 30-C) à ferme-porte\nsi elle ouvre sur le public,\nsinon PF ½ h ; ouverture vers la sortie", du=40, dv=200, couleur=ORANGE, taille=15)
    s.legende(860, 850, [("#FCE3E1", "> 70 kW : local à risques importants"), ("#FFF1DC", "30-70 kW : local CF 1 h"), ("#FFFFFF", "≤ 30 kW : amenée d'air et évacuation des produits de combustion")], taille=15)
    s.bandeau([
        ("Gaz : quelle que soit la puissance au-delà de 30 kW, le local respecte l'article GZ 9 (sites de production d'énergie) et les guides visés au GZ 3.", 17, TRAIT),
        ("Autres combustibles au-delà de 70 kW : chaufferie conforme à l'arrêté visé au CH 2. Appareils en terrasse ou au sol à l'extérieur :", 17, TRAIT),
        ("règles d'implantation et d'isolement de GZ 9 et notice du fabricant. Appareils à circuit étanche : pas d'exigence de ventilation du local.", 17, TRAIT),
    ])
    return s
