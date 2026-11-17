"""MS 53, MS 61 à MS 66 — Catégories de SSI et équipements d'alarme."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "MS53_categories-ssi",
    "titre": "Catégories de SSI et équipements d'alarme",
    "articles": ["ERP:MS 53", "ERP:MS 62", "ERP:MS 61", "ERP:MS 66", "ERP:MS 64"],
    "fiche": "SSI 2-3 · 4-2",
    "legende": "Cinq catégories de SSI, de A (détection automatique + CMSI) à E (commandes manuelles des DAS) ; quatre types d'équipements d'alarme (1, 2a/2b, 3, 4). Seuls les types 1, 2a et 2b permettent une temporisation de l'alarme générale (5 min au plus, personnel qualifié présent).",
    "ecarts": [
        "Normes en vigueur : NF S 61-931 (SSI), NF S 61-936 (équipements d'alarme), NF S 61-970 (règles d'installation des SDI), NF S 61-932 (installation des SSI) ; la NF S 61-950 citée par l'ancienne fiche a été remplacée par la série NF EN 54.",
        "Alarme perceptible par les personnes en situation de handicap (MS 64 § 3) : diffuseurs lumineux en complément du signal sonore.",
    ],
}

ROUGE = "#C1121F"
BLEU = "#1D4ED8"
VERT = "#15803D"


def b(s, x, y, w, t, fill="#FFFFFF", col=TRAIT, h=46, taille=15):
    s.items.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="{fill}" stroke="{col}" stroke-width="2.2"/>')
    s.texte(x + w / 2, y + h / 2 + 6, t, taille, col, gras=True, ancre="middle")


def f(s, x1, y1, x2, y2, c=TRAIT):
    mid = f"a{len(s.defs)}"
    s.defs.append(f'<marker id="{mid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>')
    s.items.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="2.6" marker-end="url(#{mid})"/>')


def dessiner():
    s = Scene(1600, 1160)
    s.cartouche("Catégories de SSI et équipements d'alarme", "Chaînes de mise en sécurité (NF S 61-931) et types d'alarme (NF S 61-936)", "MS 53 · MS 62")
    lignes = [
        ("A", "SDI + DM", "CMSI", "UCMC · US · UGA 1", "détection automatique et déclencheurs manuels"),
        ("B", "DM", "CMSI", "UCMC · US · UGA 2", "déclencheurs manuels seuls"),
        ("C", "DM", "DCS", "+ équipement d'alarme", "dispositif de commande avec signalisation"),
        ("D", "DM", "DCMR", "+ équipement d'alarme", "commande manuelle regroupée"),
        ("E", "DM", "DCM", "+ équipement d'alarme", "commandes manuelles individuelles"),
    ]
    y = 120
    for cat, src, cmd, sous, note in lignes:
        s.items.append(f'<rect x="40" y="{y}" width="56" height="56" rx="10" fill="{ROUGE}"/>')
        s.texte(68, y + 39, cat, 30, "#FFFFFF", gras=True, ancre="middle")
        b(s, 120, y + 5, 140, src, "#FEF3C7", "#92400E")
        f(s, 260, y + 28, 320, y + 28)
        b(s, 320, y + 5, 200, cmd, "#E0E7FF", BLEU)
        s.texte(420, y + 68, sous, 13, BLEU, ancre="middle")
        f(s, 520, y + 28, 580, y + 28)
        b(s, 580, y + 5, 90, "DAC", "#FFFFFF", TRAIT)
        f(s, 670, y + 28, 720, y + 28)
        b(s, 720, y + 5, 230, "DAS (portes, clapets,\nvolets, exutoires…)" if False else "DAS", "#DCFCE7", VERT)
        s.texte(970, y + 34, note, 15, "#374151")
        y += 112
    s.texte(120, y + 6, "SDI : système de détection incendie · DM : déclencheur manuel · CMSI : centralisateur de mise en sécurité incendie · DAC : dispositif", 14, "#4B5563")
    s.texte(120, y + 26, "adaptateur de commande · DAS : dispositif actionné de sécurité (porte, clapet, volet, exutoire, diffuseur d'alarme…)", 14, "#4B5563")

    y0 = y + 80
    s.texte(40, y0, "Équipements d'alarme (MS 62)", 21, TRAIT, gras=True)
    types = [("Type 1", "associé à un SDI\n(UGA 1 + diffuseurs)", True),
             ("Type 2a", "DM + UGA 2\n+ diffuseurs ou BAAS Sa", True),
             ("Type 2b", "DM + BAAS Pr\n+ BAAS Sa", True),
             ("Type 3", "DM + BAAS Ma\n(autonomes)", False),
             ("Type 4", "tout dispositif sonore\nautonome (cloche, sifflet…)", False)]
    x = 40
    for t, d, tempo in types:
        s.items.append(f'<rect x="{x}" y="{y0 + 20}" width="290" height="130" rx="10" fill="#FFFFFF" stroke="#9CA3AF" stroke-width="1.5"/>')
        s.texte(x + 16, y0 + 52, t, 19, TRAIT, gras=True)
        for i, l in enumerate(d.split("\n")):
            s.texte(x + 16, y0 + 80 + 22 * i, l, 15, TRAIT)
        s.pastille(x + 220, y0 + 46, "tempo." if tempo else "immédiate", "#B45309" if tempo else "#4B5563", taille=13)
        x += 306
    s.bandeau([
        ("Alarme restreinte : signal au poste de sécurité ou au personnel désigné, à exploiter pour lever le doute. Alarme générale : ordre d'évacuer,", 17, TRAIT),
        ("donnée par bâtiment ou zone de diffusion englobant la zone de mise en sécurité. Temporisation (types 1, 2a, 2b) : 5 min au plus, admise si un", 17, TRAIT),
        ("personnel qualifié exploite immédiatement l'alarme restreinte ; commande manuelle d'alarme générale immédiate au tableau (MS 66).", 17, TRAIT),
        ("SSI A et B : vérifiés par un organisme agréé à la mise en service puis tous les trois ans (MS 73) ; contrat d'entretien.", 17, TRAIT),
    ])
    return s
