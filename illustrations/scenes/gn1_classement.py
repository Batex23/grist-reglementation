"""R. 143-19 CCH, GN 1, PE 2 — Classement des ERP en types et catégories."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "GN1_classement-types-categories",
    "titre": "Classement des ERP : types et catégories",
    "articles": ["ERP:GN 1", "ERP:R143-19", "ERP:PE 2"],
    "fiche": "Cl 1-1 à 2-2",
    "legende": "Catégorie selon l'effectif du public et du personnel non indépendant : 1re au-dessus de 1 500, 2e de 701 à 1 500, 3e de 301 à 700, 4e jusqu'à 300 ; 5e sous le seuil du type (PE 2). Type selon l'activité (J à Y, établissements spéciaux).",
    "ecarts": [
        "Seuils de la 5e catégorie mis à jour d'après le tableau actuel de PE 2 (ex. type J : 25 résidents âgés / 20 handicapés ou 100 au total ; R avec sommeil : 30 ; U avec hébergement : 20).",
        "Pour le classement en 5e catégorie, l'effectif du personnel n'est pas pris en compte (GN 1 § 2 b).",
    ],
}

ROUGE = "#C1121F"
SEUILS = [("J", "Structures d'accueil personnes âgées / handicapées", "-", "-", "25 / 20 résidents · 100"),
          ("L", "Salles de réunion, polyvalentes", "100", "-", "200"),
          ("L", "Salles de spectacles, cabarets", "20", "-", "50"),
          ("M", "Magasins de vente", "100", "100", "200"),
          ("N", "Restaurants, débits de boissons", "100", "200", "200"),
          ("O", "Hôtels, pensions de famille", "-", "-", "100"),
          ("P", "Salles de danse, salles de jeux", "20", "100", "120"),
          ("R", "Crèches, maternelles", "interdit", "1 (20*)", "100"),
          ("R", "Autres enseignement · avec sommeil : 30", "100", "100", "200"),
          ("S · T · W · X · Y", "Bibliothèques, expositions, bureaux, sport, musées", "100", "100", "200"),
          ("U", "Soins sans / avec hébergement", "-", "-", "100 / 20"),
          ("V", "Établissements de culte", "100", "200", "300"),
          ("OA · GA · PA", "Altitude · gares aériennes · plein air", "-", "-", "20 · 200 · 300")]


def dessiner():
    s = Scene(1600, 1160)
    s.cartouche("Classement des ERP", "Catégories (R. 143-19 CCH) et seuils de la 5e catégorie (PE 2)", "GN 1 · R. 143-19 · PE 2")
    # échelle des catégories
    cats = [("1re", "plus de 1 500", "#7F1D1D"), ("2e", "701 à 1 500", "#B91C1C"), ("3e", "301 à 700", "#DC2626"), ("4e", "jusqu'à 300", "#F87171"), ("5e", "sous le seuil du type", "#FCA5A5")]
    s.texte(40, 130, "Catégorie (effectif public + personnel non indépendant)", 20, TRAIT, gras=True)
    x = 40
    for i, (c, e, col) in enumerate(cats):
        w = 304
        s.items.append(f'<rect x="{x}" y="150" width="{w - 8}" height="96" rx="10" fill="{col}"/>')
        s.texte(x + 18, 196, c, 34, "#FFFFFF" if i < 4 else "#7F1D1D", gras=True)
        s.texte(x + 18, 230, e, 17, "#FFFFFF" if i < 4 else "#7F1D1D", gras=True)
        x += w
    s.items.append(f'<rect x="40" y="258" width="1176" height="30" rx="6" fill="#FEE2E2"/>')
    s.texte(56, 279, "1er groupe : 1re à 4e catégorie — règlement livre II (dispositions générales + particulières)", 15, "#7F1D1D", gras=True)
    s.items.append(f'<rect x="1224" y="258" width="336" height="30" rx="6" fill="#FFF1F2"/>')
    s.texte(1240, 279, "2e groupe : livre III (PE, PO, PU, PX)", 15, "#7F1D1D", gras=True)
    # tableau des seuils
    y0 = 330
    s.texte(40, y0, "Seuils d'assujettissement au 1er groupe (effectif du public) — en dessous : 5e catégorie", 20, TRAIT, gras=True)
    cw = [190, 650, 200, 200, 300]
    hdr = ("Type", "Activité", "Sous-sol", "Étages", "Ensemble des niveaux")
    y = y0 + 20
    rows = [hdr] + SEUILS
    for i, r in enumerate(rows):
        h = 42
        s.items.append(f'<rect x="40" y="{y}" width="{sum(cw)}" height="{h}" fill="{"#1F2A37" if i == 0 else ("#F7F8FA" if i % 2 else "#FFFFFF")}" stroke="#E5E7EB"/>')
        xx = 40
        for j, c in enumerate(r):
            col = "#FFFFFF" if i == 0 else (ROUGE if j == 0 else (TRAIT if j == 1 else "#111827"))
            s.texte(xx + 14, y + 28, c, 15 if i else 15, col, gras=(i == 0 or j in (0, 4)))
            xx += cw[j]
        y += h
    s.texte(40, y + 26, "* crèches en étage : 1 personne, ou 20 si l'établissement n'a qu'un seul niveau situé en étage. Gares souterraines et mixtes : 1er groupe quel que soit l'effectif.", 14, "#4B5563")
    s.bandeau([
        ("Types (GN 1) : J personnes âgées et handicapées · L réunions, spectacles · M magasins · N restaurants · O hôtels · P danse, jeux ·", 17, TRAIT),
        ("R enseignement · S bibliothèques · T expositions · U soins · V culte · W bureaux · X sport couvert · Y musées ; établissements spéciaux", 17, TRAIT),
        ("PA plein air · CTS chapiteaux · SG structures gonflables · PS parcs de stationnement · GA gares · OA hôtels d'altitude · EF flottants · REF refuges.", 17, TRAIT),
    ])
    return s
