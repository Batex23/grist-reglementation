"""5e catégorie — PE 11, PE 6, PE 9 : dégagements et isolement."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "PE11_5e-categorie-degagements",
    "titre": "5e catégorie : dégagements et isolement",
    "articles": ["ERP:PE 11", "ERP:PE 6", "ERP:PE 9"],
    "fiche": "",
    "legende": "Moins de 20 personnes : 1 dégagement de 0,90 m. 20 à 50 : 1 de 1,40 m vers l'extérieur (25 m au plus) ou 0,90 m + 0,60 m / accessoire. 51 à 100 : 2 × 0,90 m ou 1,40 m + 0,60 m / accessoire. 101 à 200 : 1,40 + 0,90 m. 201 à 300 : 2 × 1,40 m. Cul-de-sac de 10 m au plus. Isolement des tiers et des locaux à risques : murs et planchers CF 1 h, porte CF ½ h à ferme-porte.",
    "ecarts": [
        "En rénovation ou aménagement dans un immeuble existant, 0,90 m peut être ramené à 0,80 m (PE 11 § 3). Au-delà de 300 personnes (public + personnel sans dégagements propres) : CO 38.",
        "Escaliers protégés si le plancher bas accessible est à plus de 8 m, cage CF 1 h et portes PF ½ h (PE 11 § 6).",
    ],
}

ROUGE = "#C1121F"
VERT = "#15803D"


def dessiner():
    s = Scene(1600, 1160)
    s.cartouche("5e catégorie : dégagements et isolement", "Petits établissements (livre III, PE)", "PE 6 · PE 9 · PE 11")
    x0, y0 = 40, 120
    rows = [("Effectif", "Dégagements exigibles"), ("moins de 20", "1 × 0,90 m"),
            ("20 à 50", "1 × 1,40 m sur l'extérieur (≤ 25 m)  ou  0,90 m + 0,60 m (ou accessoire)"),
            ("51 à 100", "2 × 0,90 m  ou  1,40 m + 0,60 m (ou accessoire)"),
            ("101 à 200", "1,40 m + 0,90 m"), ("201 à 300", "2 × 1,40 m")]
    for i, (a, b) in enumerate(rows):
        y = y0 + i * 56
        s.items.append(f'<rect x="{x0}" y="{y}" width="1520" height="56" fill="{"#1F2A37" if i == 0 else ("#F7F8FA" if i % 2 else "#FFFFFF")}" stroke="#E5E7EB"/>')
        s.texte(x0 + 18, y + 36, a, 19 if i else 17, "#FFFFFF" if i == 0 else TRAIT, gras=True)
        s.texte(x0 + 260, y + 36, b, 19 if i else 17, "#FFFFFF" if i == 0 else ROUGE, gras=(i == 0))
    s.texte(x0, y0 + 6 * 56 + 30, "Locaux en étage de 20 à 50 personnes : escalier unique de 0,90 m, complété d'un dégagement accessoire si le plancher bas est à plus de 8 m.", 16, "#4B5563")
    s.texte(x0, y0 + 6 * 56 + 54, "Plus de 50 personnes : portes sur l'extérieur ouvrant dans le sens de l'évacuation. Portes coulissantes ou à tambour non comptées (sauf CO 48).", 16, "#4B5563")
    # schéma isométrique isolement
    s.ox, s.oy, s.s = 560, 610, 19
    h = 2.6
    s.sol(-2, -2, 40, 18, "#E5E7EB", trait=None)
    s.sol(0, 0, 18, 14, "#FBF8F2", ep=1.4)
    s.sol(18.5, 0, 16, 14, "#EEF0F3", ep=1.4)
    s.sol(13, 0, 5, 5, "#FCE3E1", ep=1.2)
    s.volumes([mur(0, 0, 0, 14, h), mur(0, 0, 18, 0, h), mur(18.5, 0, 34.5, 0, h, pal=GRIS),
               mur(18.25, 0, 18.25, 6, h, ep=0.45, pal=MUR_CF), mur(18.25, 7.4, 18.25, 14, h, ep=0.45, pal=MUR_CF),
               mur(13, 0, 13, 5, h, pal=MUR_CF), mur(13, 5, 14.5, 5, h, pal=MUR_CF), mur(15.9, 5, 18, 5, h, pal=MUR_CF)])
    s.vantail((18.25, 6.0), 1.4, 30, 2.1, "#E8A39C")
    s.vantail((14.5, 5), 1.4, 120, 2.1, "#E8A39C")
    s.chemin([(4, 10, 0.05), (4, 13.8, 0.05)], VERT, 4)
    s.personne((6, 7, 0), 26, 1); s.personne((9, 9, 0), 26, 2, True); s.personne((27, 7, 0), 26, 5)
    u, v = s.p(7, 11, 0); s.pastille(u, v - 20, "ERP 5e catégorie", ROUGE, taille=15)
    u, v = s.p(26, 7, h); s.pastille(u, v - 20, "tiers", "#4B5563", taille=15)
    s.repere((18.25, 11, 2.0), "murs et planchers CF 1 h avec les tiers ;\nporte d'intercommunication CF ½ h à ferme-porte", du=260, dv=-60, couleur=ROUGE, taille=15)
    s.repere((15, 2.5, h), "local à risques (réserve, archives, groupe\nélectrogène…) isolé comme un tiers (PE 9)", du=-330, dv=-60, couleur=ROUGE, taille=15)
    s.repere((4, 12, 0.05), "cul-de-sac ≤ 10 m", du=-170, dv=60, couleur=VERT, taille=15)
    s.bandeau([
        ("Deux établissements distants d'au moins 5 m, ou isolés selon PE 6 § 1, sont considérés comme distincts. Façade non aveugle d'un tiers", 17, TRAIT),
        ("dominant la couverture : couverture PF ½ h sur 2 m. Désenfumage des salles > 300 m² (rdc, étage) ou > 100 m² (sous-sol) : 1/200 (PE 14).", 17, TRAIT),
        ("Extincteur : 1 pour 300 m² et 1 par niveau (PE 26). Personnel présent dès 20 personnes ou locaux à sommeil, sauf cahier des charges (PE 27).", 17, TRAIT),
    ])
    return s
