"""DF 6 — Désenfumage des circulations horizontales encloisonnées."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "DF6_desenfumage-circulations",
    "titre": "Désenfumage des circulations",
    "articles": ["ERP:DF 6"],
    "fiche": "DF 3",
    "legende": "Circulations encloisonnées désenfumées par balayage : amenées d'air en partie basse et évacuations en partie haute, alternées ; 10 m au plus entre une amenée et une évacuation en ligne droite (15 m en mécanique), 7 m sinon (10 m en mécanique).",
    "ecarts": [
        "Valeurs de l'instruction technique n° 246 (version 2004) ; l'ancienne fiche reprenait la version de 1982 (ex. 15 m / 10 m mécanique, inchangés ; 10 dm² par UP en naturel, inchangé).",
        "Obligatoire si la circulation dépasse 30 m, si elle est desservie par des escaliers en surpression, si elle dessert des locaux à sommeil, ou en sous-sol (DF 6 § 1). Halls de plus de 300 m² : désenfumés comme des locaux.",
    ],
}

AIR = "#2563EB"
FUM = "#4B5563"
ROUGE = "#C1121F"


def bouche(s, plan, a, z0, z1, l=1.5, couleur="#DBEAFE", trait=AIR):
    if plan[0] == "y":      # sur le mur y = plan[1], centrée en x = a
        y = plan[1]; s.poly([(a - l / 2, y, z0), (a + l / 2, y, z0), (a + l / 2, y, z1), (a - l / 2, y, z1)], couleur, trait=trait, ep=2.4)
    else:                   # sur le mur x = plan[1], centrée en y = a
        x = plan[1]; s.poly([(x, a - l / 2, z0), (x, a + l / 2, z0), (x, a + l / 2, z1), (x, a - l / 2, z1)], couleur, trait=trait, ep=2.4)


def dessiner():
    s = Scene(1600, 1160, echelle=27, origine=(420, 290))
    s.cartouche("Désenfumage des circulations", "Circulations horizontales encloisonnées — balayage naturel ou mécanique", "DF 6")
    H = 2.7
    s.sol(-1, -1, 33, 16, "#E5E7EB", trait=None)
    s.sol(0, 0, 30, 2, "#E9F3EA", ep=1.4)
    s.sol(28, 2, 2, 12, "#E9F3EA", ep=1.4)
    s.volumes([dict(x=-0.2, y=-0.2, z=0, dx=0.2, dy=2.2, dz=H, pal=MUR_PF), dict(x=0, y=-0.2, z=0, dx=30, dy=0.2, dz=H, pal=MUR_PF),
               dict(x=27.8, y=2, z=0, dx=0.2, dy=12, dz=H, pal=MUR_PF)])
    # évacuations (haut, gris) et amenées (bas, bleu)
    for x in (7, 25):
        bouche(s, ("y", 0), x, 1.9, 2.55, couleur="#E5E7EB", trait=FUM)
    bouche(s, ("y", 0), 16, 0.15, 0.95)
    bouche(s, ("x", 28), 4.0 + 2, 0.15, 0.95)
    # parois avant en transparence
    s.poly([(0, 2, 0), (28, 2, 0), (28, 2, H), (0, 2, H)], MUR_PF[1], trait="#B45309", ep=1.6, opacite=0.18, tirets="8 6")
    s.poly([(30, 0, 0), (30, 14, 0), (30, 14, H), (30, 0, H)], MUR_PF[2], trait="#B45309", ep=1.6, opacite=0.18, tirets="8 6")
    s.icone("fumee_02", (7, 0.9, 1.2), 70, ancre=(0.5, 0.9))
    s.icone("fumee_02", (25, 0.9, 1.2), 70, ancre=(0.5, 0.9))
    s.chemin([(16, 0.4, 0.5), (16, 1.2, 0.6), (9, 1.2, 1.6), (7.4, 0.6, 2.2)], AIR, 3.5, "8 6")
    s.chemin([(16, 0.4, 0.5), (16, 1.2, 0.6), (23, 1.2, 1.6), (24.6, 0.6, 2.2)], AIR, 3.5, "8 6")
    s.cote((7, 0, 0), (16, 0, 0), "≤ 10 m en ligne droite\n(15 m en mécanique)", decal=(0, -2.2, 0), dy_txt=-40, dx_txt=-60)
    s.chemin([(25, 1, 0.05), (29, 1, 0.05), (29, 6, 0.05)], ROUGE, 3.2, "6 5", fleche=False)
    u, v = s.p(29, 3, 0); s.etiquette(u + 150, v + 20, "≤ 7 m hors ligne droite\n(10 m en mécanique)", ROUGE, 18)
    s.repere((25, 0, 2.55), "évacuation en partie haute :\nbord inférieur ≥ 1,80 m,\ndans le tiers supérieur", du=120, dv=-150, couleur=FUM, taille=17)
    s.repere((16, 0, 0.6), "amenée d'air en partie basse :\nbord supérieur ≤ 1 m", du=60, dv=230, couleur=AIR, taille=17)

    x0, y0 = 40, 780
    s.items.append(f'<rect x="{x0}" y="{y0}" width="560" height="200" rx="10" fill="#FFFFFF" stroke="#9CA3AF" stroke-width="1.5"/>')
    s.texte(x0 + 20, y0 + 34, "Naturel", 19, TRAIT, gras=True)
    s.texte(x0 + 20, y0 + 64, "surface libre de chaque amenée et évacuation :", 16, TRAIT)
    s.texte(x0 + 20, y0 + 88, "10 dm² par unité de passage de la circulation", 16, TRAIT)
    s.texte(x0 + 20, y0 + 130, "Mécanique", 19, TRAIT, gras=True)
    s.texte(x0 + 20, y0 + 160, "extraction 0,5 m³/s par UP · soufflage ≈ 0,6 × extraction", 16, TRAIT)
    s.texte(x0 + 20, y0 + 184, "vitesse de l'air aux amenées ≤ 5 m/s", 16, TRAIT)
    s.bandeau([
        ("Désenfumage obligatoire des circulations encloisonnées : longueur totale > 30 m, desservies par des escaliers en surpression,", 18, TRAIT),
        ("desservant des locaux à sommeil, ou en sous-sol. Balayage naturel ou mécanique ; amenées et évacuations alternées.", 18, TRAIT),
        ("Exceptionnellement, mise en surpression des circulations si tous les locaux desservis sont désenfumables (seul le local sinistré l'est).", 18, TRAIT),
        ("Valeurs indiquées : instruction technique n° 246 (2004).", 16, "#4B5563"),
    ])
    return s
