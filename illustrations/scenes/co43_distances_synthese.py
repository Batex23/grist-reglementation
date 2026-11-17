"""Aide-mémoire des distances maximales à parcourir (CO 43, CO 49, CO 52, M 11, PS 13)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "CO43_distances-aide-memoire",
    "titre": "Distances maximales à parcourir : aide-mémoire",
    "articles": ["ERP:CO 43", "ERP:CO 49", "ERP:CO 52", "ERP:M 11", "ERP:PS 13"],
    "fiche": "",
    "legende": "Étages et sous-sols : 40 m vers un escalier protégé (30 m depuis un cul-de-sac), 30 m vers un escalier non protégé. Rez-de-chaussée : 50 m vers une sortie s'il y a le choix, 30 m sinon ; débouché d'escalier protégé à 20 m d'une sortie, d'escalier non protégé à 50 / 30 m. Centres commerciaux et parcs de stationnement : règles propres.",
    "ecarts": [
        "Distances mesurées dans l'axe des circulations. Pour les parcs de stationnement, depuis l'axe de la place la plus éloignée jusqu'à la porte de l'escalier, du sas ou de la sortie (PS 13).",
    ],
}

ROUGE = "#C1121F"
VERT = "#15803D"
BLEU = "#1D4ED8"
K = 14  # px par mètre


def regle(s, x, y, lignes):
    """lignes : [(m, texte, couleur, plein)] du plus long au plus court."""
    for i, (m, t, c, plein) in enumerate(lignes):
        yy = y + i * 24
        w = m * K
        s.items.append(f'<rect x="{x}" y="{yy}" width="{w:.0f}" height="16" rx="3" fill="{c if plein else "#FFFFFF"}" stroke="{c}" stroke-width="2"/>')
        s.texte(x + w + 10, yy + 14, f"{m} m", 17, c, gras=True)
        s.texte(x + w + 64, yy + 14, t, 15, "#374151")


def dessiner():
    s = Scene(1600, 1160)
    s.cartouche("Distances maximales à parcourir", "Aide-mémoire, distances mesurées dans l'axe des circulations", "CO 43 · CO 49 · CO 52 · M 11 · PS 13")
    x0 = 40
    xr = 430
    # échelle
    y = 108
    for m in range(0, 51, 10):
        xx = xr + m * K
        s.items.append(f'<line x1="{xx:.0f}" y1="{y + 18}" x2="{xx:.0f}" y2="880" stroke="#E5E7EB" stroke-width="1.2"/>')
        s.texte(xx, y + 12, f"{m} m", 14, "#6B7280", ancre="middle")
    blocs = [
        ("Étages et sous-sols", "#1F2A37", [
            ("Vers un escalier protégé ou une circulation\nhorizontale protégée (portes à ferme-porte)", "CO 49 § 2", [(40, "cas général", VERT, True), (30, "depuis une partie en cul-de-sac", VERT, False)]),
            ("Vers un escalier non protégé", "CO 49 § 2", [(30, "", ROUGE, True)]),
        ]),
        ("Rez-de-chaussée", "#1F2A37", [
            ("De tout point d'un local vers une sortie sur\nl'extérieur ou un dégagement protégé", "CO 43 § 2", [(50, "si choix entre plusieurs sorties", VERT, True), (30, "sinon", VERT, False)]),
            ("Débouché d'un escalier encloisonné\njusqu'à une sortie sur l'extérieur", "CO 49 § 3", [(20, "cheminement direct, même largeur", BLEU, True)]),
            ("Débouché d'un escalier non protégé\njusqu'à une sortie ou un dégagement protégé", "CO 52 § 6", [(50, "si choix entre plusieurs sorties", ROUGE, True), (30, "sinon", ROUGE, False)]),
        ]),
        ("Centres commerciaux (M)", "#7C2D12", [
            ("Rez-de-chaussée : vers le mail, une sortie\nou un dégagement protégé", "M 11 § 1", [(50, "s'il y a le choix", VERT, True), (30, "sinon", VERT, False)]),
            ("Étage ou sous-sol : idem ; escalier non\nprotégé (s'il est autorisé) : 30 m", "M 11 § 1", [(40, "s'il y a le choix", VERT, True), (30, "sinon, ou escalier non protégé", VERT, False)]),
        ]),
        ("Parcs de stationnement (PS)", "#1E3A8A", [
            ("Parc clos : vers un escalier ou une sortie hors\ndes zones de stationnement", "PS 13 § 1", [(40, "entre 2 sorties opposées", BLEU, True), (25, "autres cas (cul-de-sac ≤ 25 m : 40 m au total)", BLEU, False)]),
            ("Parc largement ventilé (PSLV)", "PS 13 § 1", [(50, "entre 2 sorties opposées", BLEU, True), (30, "autres cas (cul-de-sac ≤ 30 m : 50 m au total)", BLEU, False)]),
        ]),
    ]
    y = 140
    for titre, coul, rows in blocs:
        s.items.append(f'<rect x="{x0}" y="{y}" width="1520" height="34" rx="6" fill="{coul}"/>')
        s.texte(x0 + 14, y + 23, titre, 18, "#FFFFFF", gras=True)
        y += 44
        for lab, ref, lignes in rows:
            h = max(2, len(lignes)) * 24 + 12
            for j, l in enumerate(lab.split("\n")):
                s.texte(x0 + 6, y + 16 + j * 20, l, 15, TRAIT, gras=(j == 0))
            s.pastille(x0 + 1468, y + 14, ref, "#FFFFFF", TRAIT, taille=14)
            regle(s, xr, y + 2, lignes)
            s.items.append(f'<line x1="{x0}" y1="{y + h - 4}" x2="{x0 + 1520}" y2="{y + h - 4}" stroke="#E5E7EB" stroke-width="1"/>')
            y += h
        y += 6
    s.bandeau([
        ("Barre pleine : cas général ; barre vide : cas restrictif. Les dispositions particulières peuvent réduire ces distances", 18, TRAIT),
        ("(par exemple J 18, O 8, U 19 : distances propres aux établissements avec locaux à sommeil).", 18, TRAIT),
    ])
    return s
