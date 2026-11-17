"""EC 7 à EC 10, EC 12 — Éclairage de sécurité : évacuation et ambiance."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "EC8_eclairage-securite",
    "titre": "Éclairage de sécurité",
    "articles": ["ERP:EC 8", "ERP:EC 7", "ERP:EC 9", "ERP:EC 10", "ERP:EC 12"],
    "fiche": "EC 1",
    "legende": "Évacuation : cheminements, sorties, balisage, obstacles éclairés, foyers à 15 m au plus dans les dégagements, 45 lumens, au moins deux blocs au-delà de 15 m. Ambiance : dès 100 personnes (50 en sous-sol), 5 lm/m², écartement/hauteur ≤ 4, au moins deux blocs par local.",
    "ecarts": [
        "Les « types A, B, C, D » d'éclairage de sécurité de l'ancienne fiche ont disparu avec l'arrêté du 19 novembre 2001 : l'éclairage de sécurité est réalisé par source centralisée à batterie (EC 11) ou par blocs autonomes (EC 12), avec une autonomie d'une heure.",
        "Blocs d'évacuation à système de test automatique (SATI, NF C 71-820) ; mise au repos centralisée près de la commande générale de l'éclairage (EC 12 § 5).",
    ],
}

VERT = "#15803D"
JAUNE = "#F59E0B"


def baes(s, x, y, z, plan="y"):
    if plan == "y":
        s.poly([(x - 0.4, y, z), (x + 0.4, y, z), (x + 0.4, y, z + 0.25), (x - 0.4, y, z + 0.25)], "#FFFFFF", trait=TRAIT, ep=1.6)
        s.poly([(x - 0.3, y, z + 0.04), (x + 0.3, y, z + 0.04), (x + 0.3, y, z + 0.21), (x - 0.3, y, z + 0.21)], VERT, trait=None)
    else:
        s.poly([(x, y - 0.4, z), (x, y + 0.4, z), (x, y + 0.4, z + 0.25), (x, y - 0.4, z + 0.25)], "#FFFFFF", trait=TRAIT, ep=1.6)
        s.poly([(x, y - 0.3, z + 0.04), (x, y + 0.3, z + 0.04), (x, y + 0.3, z + 0.21), (x, y - 0.3, z + 0.21)], VERT, trait=None)


def ambiance(s, x, y, z):
    s.boite(x - 0.35, y - 0.35, z, 0.7, 0.7, 0.15, ("#FFFFFF", "#E5E7EB", "#D1D5DB"), ep=1.4)
    u, v = s.p(x, y, z)
    s.items.append(f'<path d="M{u - 40},{v + 60} L{u},{v + 4} L{u + 40},{v + 60} Z" fill="#FDE68A" fill-opacity="0.45"/>')


def dessiner():
    s = Scene(1600, 1160, echelle=20, origine=(640, 230))
    s.cartouche("Éclairage de sécurité", "Éclairage d'évacuation et éclairage d'ambiance (anti-panique) — ERP", "EC 7 à EC 12")
    H = 3.0
    L, P = 40, 22
    s.sol(-1, -1, L + 2, P + 2, "#E5E7EB", trait=None)
    s.sol(0, 0, L, P, "#2F3B4C", ep=1.4)                     # local plongé dans le noir
    s.sol(0, 14, L, 3, "#3F4B5C", ep=1.2)                    # dégagement
    s.volumes([dict(x=-0.2, y=0, z=0, dx=0.2, dy=P, dz=H, pal=MUR), dict(x=0, y=-0.2, z=0, dx=L, dy=0.2, dz=H, pal=MUR),
               dict(x=0, y=13.9, z=0, dx=16, dy=0.2, dz=1.0, pal=MUR), dict(x=18, y=13.9, z=0, dx=22, dy=0.2, dz=1.0, pal=MUR),
               dict(x=0, y=17, z=0, dx=L, dy=0.2, dz=0.8, pal=MUR)])
    # éclairage d'ambiance dans la salle (> 100 personnes)
    for x in (6, 16, 26, 34):
        for y in (4, 10):
            ambiance(s, x, y, H)
    for (x, y, k, f) in [(10, 7, 1, 0), (20, 6, 2, 1), (30, 9, 3, 0), (24, 11, 4, 1)]:
        s.personne((x, y, 0), 26, k, bool(f))
    # éclairage d'évacuation dans le dégagement : foyers tous les 15 m au plus, balisage des sorties
    for x in (2, 15, 28, 39):
        baes(s, x, 0, 2.4) if False else None
    for x in (3, 17, 31):
        u, v = s.p(x, 15.5, H); s.items.append(f'<rect x="{u - 18:.1f}" y="{v - 8:.1f}" width="36" height="14" rx="3" fill="#FFFFFF" stroke="{TRAIT}" stroke-width="1.6"/><rect x="{u - 13:.1f}" y="{v - 5:.1f}" width="26" height="8" fill="{VERT}"/>')
        s.items.append(f'<path d="M{u - 30},{v + 50} L{u},{v + 6} L{u + 30},{v + 50} Z" fill="#BBF7D0" fill-opacity="0.45"/>')
    baes(s, 0, 15.5, 2.3, plan="x")
    s.chemin([(36, 15.5, 0.05), (1, 15.5, 0.05)], VERT, 4.5, "12 7")
    s.cote((3, 15.5, H), (17, 15.5, H), "≤ 15 m", decal=(0, 0, 1.2), dy_txt=-24)
    s.repere((17, 15.5, H), "éclairage d'évacuation : foyers ≥ 45 lm,\nau moins 2 blocs si le dégagement > 15 m", du=-330, dv=200, couleur=VERT, taille=17)
    s.repere((16, 10, H), "éclairage d'ambiance : 5 lm/m², au moins 2 blocs,\nécartement entre foyers ≤ 4 × leur hauteur", du=200, dv=-170, couleur="#B45309", taille=17)
    s.repere((0, 15.5, 2.4), "balisage de la sortie\n(blanc sur fond vert, CO 42)", du=-200, dv=-80, couleur=VERT, taille=17)
    s.cote((34, 10, 0), (34, 10, H), "h", decal=(0, 0, 0), rappel=False, dx_txt=20)

    x0, y0 = 1000, 100
    s.items.append(f'<rect x="{x0}" y="{y0}" width="600" height="250" rx="10" fill="#FFFFFF" stroke="#9CA3AF" stroke-width="1.5"/>')
    s.texte(x0 + 20, y0 + 34, "Quand l'installer ?", 19, TRAIT, gras=True)
    for i, t in enumerate(["Évacuation : locaux de 50 personnes et plus, locaux de plus", "de 300 m² (rdc, étage) ou 100 m² (sous-sol), et leurs dégagements", "Ambiance : local ou hall de 100 personnes et plus (50 en sous-sol)", "Autonomie : 1 heure · état de veille pendant l'exploitation", "Contrôle : passage en fonctionnement chaque mois,", "autonomie chaque semestre (SATI possible) — EC 14"]):
        s.texte(x0 + 20, y0 + 70 + 30 * i, t, 16, TRAIT)
    s.bandeau([
        ("L'éclairage de sécurité est à l'état de veille pendant l'exploitation et se met en service à la défaillance de l'éclairage normal/remplacement.", 18, TRAIT),
        ("Il est réalisé par une source centralisée à batterie alimentant des luminaires (EC 11) ou par des blocs autonomes (EC 12).", 18, TRAIT),
        ("Les dégagements ne doivent pas pouvoir être plongés dans l'obscurité totale par une commande accessible au public (EC 6).", 18, TRAIT),
    ])
    return s
