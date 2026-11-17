"""CO 51, CO 55, CO 56 — Escaliers droits et tournants."""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "CO55_escaliers-droits-tournants",
    "titre": "Escaliers droits et tournants",
    "articles": ["ERP:CO 55", "ERP:CO 56", "ERP:CO 51"],
    "fiche": "C.15",
    "legende": "Volées de 25 marches au plus, paliers de la largeur de l'escalier (plus de 1 m de long si les volées ne se contrarient pas), mains courantes, recoupement au-delà de 4 UP ; escalier tournant à balancement continu, giron extérieur < 0,42 m.",
    "ecarts": [
        "Les valeurs de marches (hauteur 0,13 à 0,17 m, giron 0,28 à 0,36 m, 0,60 ≤ 2h + g ≤ 0,64 m) sont des règles de l'art auxquelles renvoie CO 55 ; elles ne sont pas fixées par le règlement.",
    ],
}

ROUGE = "#C1121F"
BLEU = "#1D4ED8"


def dessiner():
    s = Scene(1600, 1160, echelle=62, origine=(700, 320))
    s.cartouche("Escaliers droits et tournants", "Sécurité d'utilisation des escaliers — ERP", "CO 51 · CO 55 · CO 56")
    n, g, hm, larg = 10, 0.30, 0.165, 1.4
    Y0 = 9.0                                   # pied de la première volée ; on monte vers -y
    s.sol(-1, -0.5, larg + 2, Y0 + 1.5, "#E5E7EB", trait=None)
    v = []
    for k in range(n):
        v.append(dict(x=0, y=Y0 - (k + 1) * g, z=0, dx=larg, dy=g, dz=hm * (k + 1), pal=BETON, ep=1.1))
    zp = hm * n
    yp = Y0 - n * g
    v.append(dict(x=0, y=yp - 1.6, z=0, dx=larg, dy=1.6, dz=zp, pal=BETON, ep=1.4))
    for k in range(n):
        v.append(dict(x=0, y=yp - 1.6 - (k + 1) * g, z=zp, dx=larg, dy=g, dz=hm * (k + 1), pal=BETON, ep=1.1))
    s.volumes(v)
    ytop = yp - 1.6 - n * g
    for xx in (0.05, larg - 0.05):
        s.ligne((xx, Y0, 0.9), (xx, yp, zp + 0.9), BLEU, 4)
        s.ligne((xx, yp, zp + 0.9), (xx, yp - 1.6, zp + 0.9), BLEU, 4)
        s.ligne((xx, yp - 1.6, zp + 0.9), (xx, ytop, 2 * zp + 0.9), BLEU, 4)
    s.cote((larg, yp, zp), (larg, yp - 1.6, zp), "palier > 1 m", decal=(1.0, 0, 0), dx_txt=80)
    s.repere((larg - 0.05, Y0 - 0.5 * n * g, 0.5 * zp + 0.9), "main courante de chaque côté\n(dès 2 UP ; une seule dès 1 UP)", du=230, dv=60, couleur=BLEU, taille=17)
    s.repere((0.7, Y0 - 0.5 * g, hm), "25 marches au plus par volée", du=-140, dv=60, couleur=ROUGE, taille=17)
    s.repere((0.7, ytop + 0.4, 2 * zp), "au-delà de 4 UP : main courante\nintermédiaire (≤ 4 UP entre mains)", du=260, dv=-40, couleur="#374151", taille=16)

    # encart profil de marche (règles de l'art)
    x0, y0 = 40, 700
    s.items.append(f'<rect x="{x0}" y="{y0}" width="640" height="270" rx="10" fill="#FFFFFF" stroke="#9CA3AF" stroke-width="1.5"/>')
    s.texte(x0 + 20, y0 + 32, "Marches (règles de l'art, indicatif)", 18, TRAIT, gras=True)
    px, py, G, H = x0 + 60, y0 + 230, 110, 62
    d = f"M{px},{py}"
    for i in range(3):
        d += f" L{px + i * G},{py - (i + 1) * H} L{px + (i + 1) * G},{py - (i + 1) * H}"
    s.items.append(f'<path d="{d} L{px + 3 * G},{py} Z" fill="{BETON[1]}" stroke="{TRAIT}" stroke-width="2.4"/>')
    s.texte(px + G * 1.5, py - 2 * H - 8, "g", 20, ROUGE, gras=True, ancre="middle")
    s.texte(px + G + 12, py - 1.5 * H + 6, "h", 20, ROUGE, gras=True)
    s.texte(x0 + 430, y0 + 90, "h : 0,13 à 0,17 m", 16, TRAIT)
    s.texte(x0 + 430, y0 + 116, "g : 0,28 à 0,36 m", 16, TRAIT)
    s.texte(x0 + 430, y0 + 142, "0,60 ≤ 2h + g ≤ 0,64", 16, TRAIT)
    s.texte(x0 + 430, y0 + 178, "sans contremarche :", 15, "#4B5563")
    s.texte(x0 + 430, y0 + 198, "recouvrement 0,05 m", 15, "#4B5563")

    # encart escalier tournant (plan)
    cx, cy, R = 1240, 760, 190
    s.items.append(f'<rect x="{cx - 290}" y="{cy - 250}" width="600" height="460" rx="10" fill="#FFFFFF" stroke="#9CA3AF" stroke-width="1.5"/>')
    s.texte(cx - 270, cy - 218, "Escalier tournant (plan)", 18, TRAIT, gras=True)
    r0 = 40
    s.items.append(f'<path d="M{cx - R},{cy} A{R},{R} 0 0 1 {cx + R},{cy} L{cx + r0},{cy} A{r0},{r0} 0 0 0 {cx - r0},{cy} Z" fill="{BETON[0]}" stroke="{TRAIT}" stroke-width="2.2"/>')
    for i in range(1, 12):
        a = math.pi - i * math.pi / 12
        s.items.append(f'<line x1="{cx + r0 * math.cos(a):.1f}" y1="{cy - r0 * math.sin(a):.1f}" x2="{cx + R * math.cos(a):.1f}" y2="{cy - R * math.sin(a):.1f}" stroke="{TRAIT}" stroke-width="1.4"/>')
    rf = r0 + 60 * 150 / 150
    s.items.append(f'<path d="M{cx - rf},{cy} A{rf},{rf} 0 0 1 {cx + rf},{cy}" fill="none" stroke="{BLEU}" stroke-width="2.6" stroke-dasharray="9 6"/>')
    s.texte(cx, cy + 40, "ligne de foulée à 0,60 m du noyau", 15, BLEU, ancre="middle")
    s.texte(cx, cy + 66, "balancement continu, sans palier intermédiaire", 15, TRAIT, ancre="middle")
    s.texte(cx, cy + 92, "giron extérieur < 0,42 m · 1 UP : main courante côté extérieur", 15, ROUGE, ancre="middle")

    s.bandeau([
        ("Escaliers droits : volées de 25 marches au plus (sauf gradins), directions des volées contrariées si possible, paliers de la largeur de", 18, TRAIT),
        ("l'escalier et de plus de 1 m de long si les volées ne se contrarient pas ; rampes admises jusqu'à 12 % de pente.", 18, TRAIT),
        ("Marches non glissantes. Main courante dès 1 UP, de chaque côté dès 2 UP ; au-delà de 4 UP, mains courantes intermédiaires.", 18, TRAIT),
    ])
    return s
