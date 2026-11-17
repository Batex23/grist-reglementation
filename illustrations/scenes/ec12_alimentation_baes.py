"""EC 11, EC 12, EC 14 — Alimentation de l'éclairage de sécurité (blocs autonomes, source centralisée)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "EC12_alimentation-eclairage-securite",
    "titre": "Alimentation de l'éclairage de sécurité",
    "articles": ["ERP:EC 12", "ERP:EC 11", "ERP:EC 14"],
    "fiche": "EC 4",
    "legende": "Blocs autonomes alimentés par une dérivation prise en aval de la protection et en amont de la commande de l'éclairage normal du local, avec une mise au repos centralisée près de la commande générale. Source centralisée : batterie (NF EN 50171), au moins deux circuits distincts par local et par dégagement de plus de 15 m.",
    "ecarts": [
        "Normes actualisées : blocs NF EN IEC 60598-2-22 (2022) et NF C 71-800/801/805 ; source centralisée NF EN 50171 (2021) ; câbles C ca-s2,d2,a2 (l'ancienne fiche citait les câbles C2).",
    ],
}

ROUGE = "#C1121F"
VERT = "#15803D"


def boite2d(s, x, y, w, h, t, fill="#FFFFFF", col=TRAIT, taille=16):
    s.items.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{col}" stroke-width="2.4"/>')
    for i, l in enumerate(t.split("\n")):
        s.texte(x + w / 2, y + h / 2 + 6 + (i - (len(t.split(chr(10))) - 1) / 2) * (taille + 4), l, taille, col if col != TRAIT else TRAIT, gras=True, ancre="middle")


def fil(s, pts, c=TRAIT, ep=3, tirets=None):
    d = " ".join(f"{x},{y}" for x, y in pts)
    dash = f' stroke-dasharray="{tirets}"' if tirets else ""
    s.items.append(f'<polyline points="{d}" fill="none" stroke="{c}" stroke-width="{ep}" stroke-linejoin="round"{dash}/>')


def dessiner():
    s = Scene(1600, 1160)
    s.cartouche("Alimentation de l'éclairage de sécurité", "Blocs autonomes (BAES) et source centralisée — schémas de principe", "EC 11 · EC 12")
    # --- blocs autonomes
    s.texte(40, 140, "Blocs autonomes (EC 12)", 22, TRAIT, gras=True)
    boite2d(s, 60, 180, 220, 70, "Tableau éclairage\nnormal", "#F3F4F6")
    fil(s, [(170, 250), (170, 300)])
    boite2d(s, 110, 300, 120, 50, "protection", "#FFFFFF", taille=15)
    fil(s, [(170, 350), (170, 420)])
    s.items.append(f'<circle cx="170" cy="420" r="7" fill="{ROUGE}"/>')
    fil(s, [(170, 420), (170, 470)])
    boite2d(s, 110, 470, 120, 50, "commande\nlocal", "#FFFFFF", taille=14)
    fil(s, [(170, 520), (170, 600), (480, 600)])
    for x in (260, 380):
        s.items.append(f'<circle cx="{x}" cy="600" r="22" fill="#FEF3C7" stroke="{TRAIT}" stroke-width="2"/><path d="M{x - 14},{600 - 14} L{x + 14},{600 + 14} M{x + 14},{600 - 14} L{x - 14},{600 + 14}" stroke="{TRAIT}" stroke-width="2"/>')
    s.texte(320, 650, "éclairage normal du local", 15, "#4B5563", ancre="middle")
    fil(s, [(170, 420), (560, 420), (560, 470)], ROUGE, 3.5)
    for i, x in enumerate((520, 660)):
        s.items.append(f'<rect x="{x}" y="470" width="110" height="44" rx="6" fill="#FFFFFF" stroke="{TRAIT}" stroke-width="2.4"/><rect x="{x + 12}" y="480" width="86" height="24" fill="{VERT}"/>')
    fil(s, [(630, 492), (660, 492)], ROUGE, 3.5)
    s.texte(560, 540, "2 blocs au moins par local et par dégagement > 15 m", 15, TRAIT)
    s.etiquette(400, 380, "dérivation en aval de la protection,\nen amont de la commande", ROUGE, 16)
    boite2d(s, 880, 300, 190, 70, "télécommande\nde mise au repos", "#E0F2FE", "#1D4ED8", 15)
    fil(s, [(880, 335), (745, 335), (745, 470)], "#1D4ED8", 2.4, "8 6")
    s.texte(880, 400, "près de la commande générale", 15, "#1D4ED8")
    s.texte(880, 422, "de l'éclairage normal", 15, "#1D4ED8")
    s.texte(560, 570, "SATI : test automatique (NF C 71-820)", 15, VERT, gras=True)

    # --- source centralisée
    y0 = 720
    s.texte(40, y0, "Source centralisée (EC 11)", 22, TRAIT, gras=True)
    boite2d(s, 60, y0 + 40, 220, 80, "Batterie\nNF EN 50171", "#FEE2E2", ROUGE)
    fil(s, [(280, y0 + 80), (360, y0 + 80)], ROUGE, 3.5)
    boite2d(s, 360, y0 + 40, 220, 80, "Tableau de\nsécurité (EL 15)", "#FFFFFF", ROUGE)
    for k, (c, yy) in enumerate((("circuit 1", y0 + 60), ("circuit 2", y0 + 100))):
        fil(s, [(580, yy), (1450, yy)], ROUGE if k == 0 else "#B45309", 3.5)
        s.texte(600, yy - 8, c, 14, ROUGE if k == 0 else "#B45309", gras=True)
    for i, x in enumerate(range(700, 1450, 110)):
        yy = y0 + 60 if i % 2 == 0 else y0 + 100
        s.items.append(f'<rect x="{x}" y="{yy + 10}" width="70" height="30" rx="5" fill="#FFFFFF" stroke="{TRAIT}" stroke-width="2"/><rect x="{x + 8}" y="{yy + 16}" width="54" height="18" fill="{VERT}"/>')
        fil(s, [(x + 35, yy), (x + 35, yy + 10)], ROUGE if i % 2 == 0 else "#B45309", 2.4)
    s.texte(700, y0 + 180, "Circuits alternés : la perte d'un circuit laisse un éclairement suffisant ; aucun dispositif", 16, TRAIT)
    s.texte(700, y0 + 204, "de protection sur le parcours des canalisations ; autonomie 1 h.", 16, TRAIT)
    s.bandeau([
        ("Exploitation (EC 14) : éclairage de sécurité en veille pendant l'ouverture ; mis au repos (blocs) ou à l'arrêt (source centralisée)", 18, TRAIT),
        ("quand l'éclairage normal est volontairement coupé. Chaque mois : essai de passage en fonctionnement et de la télécommande ;", 18, TRAIT),
        ("chaque semestre : autonomie d'au moins 1 h (automatique avec SATI). Résultats consignés au registre de sécurité.", 18, TRAIT),
    ])
    return s
