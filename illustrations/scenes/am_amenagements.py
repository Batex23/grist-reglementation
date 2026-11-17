"""AM 3 à AM 8 — Réaction au feu des revêtements et aménagements."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "AM3_reaction-au-feu",
    "titre": "Réaction au feu des aménagements",
    "articles": ["ERP:AM 3", "ERP:AM 4", "ERP:AM 5", "ERP:AM 7", "ERP:AM 8"],
    "fiche": "AM 1",
    "legende": "Escaliers protégés : plafonds B-s1, d0, parois B-s2, d0, marches CFL-s1. Circulations protégées : plafonds B-s2, d0, parois C-s3, d0, sols DFL-s2. Locaux et dégagements non protégés : plafonds B-s3, d0 (25 % en C ou D), parois C-s3, d0, sols DFL-s2. Isolants A2-s2, d0 ou protégés par un écran.",
    "ecarts": [
        "L'ancienne fiche donnait les classes M (M1, M2, M3, M4) : les euroclasses de l'arrêté du 21 novembre 2002 sont indiquées ici ; le texte admet encore les deux.",
        "Lambris bois D-s2, d0 sur tasseaux avec remplissage A2-s2, d0 : sur toutes les parois si le plafond est B-s3, d0, sinon 50 % au plus (AM 4 § 2).",
    ],
}

ROUGE = "#C1121F"


def dessiner():
    s = Scene(1600, 1160, echelle=40, origine=(520, 300))
    s.cartouche("Réaction au feu des aménagements", "Revêtements des parois, plafonds et sols — euroclasses (classement M entre parenthèses)", "AM 3 à AM 8")
    h = 3.0
    s.sol(-1, -1, 18, 11, "#E5E7EB", trait=None)
    s.sol(0, 0, 4, 9, "#DBEAFE", ep=1.4)            # escalier protégé
    s.sol(4, 0, 12, 3, "#DCFCE7", ep=1.4)           # circulation protégée
    s.sol(4, 3, 12, 6, "#FEF3C7", ep=1.4)           # local
    s.volumes([dict(x=-0.25, y=0, z=0, dx=0.25, dy=9, dz=h, pal=MUR_BLEU), dict(x=0, y=-0.25, z=0, dx=4, dy=0.25, dz=h, pal=MUR_BLEU),
               dict(x=4, y=-0.25, z=0, dx=12, dy=0.25, dz=h, pal=("#DCFCE7", "#BBF7D0", "#86EFAC")),
               dict(x=3.9, y=0, z=0, dx=0.2, dy=1, dz=h, pal=MUR_BLEU), dict(x=3.9, y=2.2, z=0, dx=0.2, dy=6.8, dz=h, pal=MUR_BLEU),
               dict(x=4, y=2.9, z=0, dx=6, dy=0.2, dz=h * 0.5, pal=("#DCFCE7", "#BBF7D0", "#86EFAC")), dict(x=11.2, y=2.9, z=0, dx=4.8, dy=0.2, dz=h * 0.5, pal=("#DCFCE7", "#BBF7D0", "#86EFAC"))])
    for k in range(8):
        s.boite(0.4, 8.5 - k * 0.55, 0, 3.2, 0.55, 0.18 * (k + 1), BETON, ep=1.1)
    # plafond suspendu du local en transparence
    s.sol(4, 3, 12, 6, "#FDE68A", trait="#B45309", ep=1.6, z=h, opacite=0.35)
    for x in range(5, 16, 2):
        s.boite(x, 3.5, 0, 1.2, 0.8, 0.75, ("#E7D3B5", "#D4B88E", "#B89468"), ep=1.1)
    s.personne((12, 6, 0), 30, 3); s.personne((8, 1.5, 0), 30, 4, True)

    def bloc(u, v, titre, col, lignes):
        s.items.append(f'<rect x="{u}" y="{v}" width="330" height="{40 + 26 * len(lignes)}" rx="9" fill="#FFFFFF" stroke="{col}" stroke-width="2.4"/>')
        s.texte(u + 16, v + 28, titre, 17, col, gras=True)
        for i, (a, b_) in enumerate(lignes):
            s.texte(u + 16, v + 56 + 26 * i, a, 15, "#374151")
            s.texte(u + 314, v + 56 + 26 * i, b_, 15, TRAIT, gras=True, ancre="end")
    bloc(40, 110, "Escalier protégé (AM 3)", "#1D4ED8", [("plafonds, rampants", "B-s1, d0 (M 1)"), ("parois verticales", "B-s2, d0 (M 1)"), ("marches, paliers", "CFL-s1 (M 3)")])
    bloc(40, 760, "Circulation protégée (AM 3)", "#15803D", [("plafonds", "B-s2, d0 (M 1)"), ("parois verticales", "C-s3, d0 (M 2)"), ("sols", "DFL-s2 (M 4)")])
    bloc(1230, 110, "Locaux et dégagements", "#B45309", [("plafonds (AM 5)", "B-s3, d0 (M 1)"), ("dont 25 % admis", "C / D-s3, d0"), ("parois (AM 4)", "C-s3, d0 (M 2)"), ("sols (AM 7)", "DFL-s2 (M 4)")])
    bloc(1230, 760, "Isolants (AM 8)", ROUGE, [("parois, plafonds, toiture", "A2-s2, d0 (M 0)"), ("sols", "A2FL-s1"), ("sinon écran thermique", "¼ h ou ½ h")])
    s.bandeau([
        ("Objectif : éviter le développement rapide d'un incendie qui compromettrait l'évacuation. Suspentes de plafonds suspendus A1 (ou sans", 18, TRAIT),
        ("effondrement en chaîne avant ¼ h) ; plafonds suspendus ou tendus maintenus sous l'effet du désenfumage mécanique (AM 5).", 18, TRAIT),
        ("Gros mobilier, décors, tentures, sièges : articles AM 9 à AM 18 ; dispositions particulières propres à chaque type d'établissement.", 18, TRAIT),
    ])
    return s
