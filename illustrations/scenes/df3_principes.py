"""DF 1, DF 3, DF 4 — Objet et principes du désenfumage."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "DF3_principes-desenfumage",
    "titre": "Principes du désenfumage",
    "articles": ["ERP:DF 3", "ERP:DF 1", "ERP:DF 4"],
    "fiche": "DF 1-1",
    "legende": "Le désenfumage extrait en début d'incendie une partie des fumées pour garder praticables les cheminements d'évacuation : par balayage (amenée d'air neuf + évacuation des fumées, naturelles ou mécaniques) ou par différence de pression.",
    "ecarts": [
        "Les solutions techniques sont décrites par l'instruction technique n° 246 (arrêté du 22 mars 2004 modifié), qui a remplacé la version de 1982 dont s'inspirait l'ancienne fiche.",
        "Désenfumage mécanique alimenté par une AES (NF S 61-940) ; désenfumage commandé avant l'extinction automatique à eau en présence d'un SSI A (DF 3 § 2). Ingénierie du désenfumage possible (DF 4 § 2).",
    ],
}

AIR = "#2563EB"
FUM = "#6B7280"


def piece(s, ox, oy, titre, amenee, evac, sous):
    s.ox, s.oy = ox, oy
    L, P, H = 10, 7, 4
    s.sol(0, 0, L, P, SOL_INT, ep=1.4)
    s.boite(-0.3, 0, 0, 0.3, P, H, MUR, ep=1.6)
    s.boite(0, -0.3, 0, L, 0.3, H, MUR, ep=1.6)
    # couche de fumée sous plafond
    s.boite(0, 0, H - 1.5, L, P, 1.5, ("#9CA3AF", "#9CA3AF", "#9CA3AF"), ep=0, opacite=0.35)
    s.icone("fumee_02", (6.5, 3.5, H - 1.6), 90, ancre=(0.5, 0.9))
    s.icone("feu_01", (6.5, 3.5, 0), 46)
    # amenée d'air en bas sur le mur x = 0, évacuation en haut sur le mur y = 0
    s.poly([(0, 2, 0.3), (0, 4, 0.3), (0, 4, 1.3), (0, 2, 1.3)], "#DBEAFE", trait=AIR, ep=2.4)
    s.chemin([(-2.2, 3, 0.8), (2.4, 3, 0.8)], AIR, 5)
    s.poly([(3.5, 0, H - 1.2), (5.5, 0, H - 1.2), (5.5, 0, H - 0.2), (3.5, 0, H - 0.2)], "#E5E7EB", trait=FUM, ep=2.4)
    s.chemin([(4.5, 1.6, H - 0.7), (4.5, -2.6, H - 0.7)], FUM, 5)
    if amenee == "méca":
        u, v = s.p(-1.2, 3, 0.8); s.items.append(f'<circle cx="{u:.1f}" cy="{v:.1f}" r="15" fill="#fff" stroke="{AIR}" stroke-width="3"/><path d="M{u - 8},{v} L{u + 8},{v} M{u},{v - 8} L{u},{v + 8}" stroke="{AIR}" stroke-width="3"/>')
    if evac == "méca":
        u, v = s.p(4.5, -1.6, H - 0.7); s.items.append(f'<circle cx="{u:.1f}" cy="{v:.1f}" r="15" fill="#fff" stroke="{FUM}" stroke-width="3"/><path d="M{u - 8},{v} L{u + 8},{v} M{u},{v - 8} L{u},{v + 8}" stroke="{FUM}" stroke-width="3"/>')
    s.texte(ox - 330, oy - 170, titre, 21, TRAIT, gras=True)
    s.texte(ox - 330, oy - 146, sous, 16, "#4B5563")


def dessiner():
    s = Scene(1600, 1160, echelle=27, origine=(0, 0))
    s.cartouche("Principes du désenfumage", "Balayage du volume à protéger : amenée d'air neuf en partie basse, évacuation des fumées en partie haute", "DF 1 · DF 3")
    piece(s, 430, 290, "Naturel", "nat", "nat", "amenée naturelle · évacuation naturelle")
    piece(s, 1190, 290, "Mixte", "nat", "méca", "amenée naturelle · extraction mécanique")
    piece(s, 430, 690, "Mécanique", "méca", "méca", "soufflage mécanique · extraction mécanique")
    # différence de pression
    s.ox, s.oy = 1190, 690
    L, P, H = 10, 7, 4
    s.sol(0, 0, L, P, SOL_INT, ep=1.4)
    s.boite(-0.3, 0, 0, 0.3, P, H, MUR, ep=1.6); s.boite(0, -0.3, 0, L, 0.3, H, MUR, ep=1.6)
    s.boite(5, 0, 0, 0.3, P, H, MUR_BLEU, ep=1.6)
    s.icone("fumee_02", (8, 3.5, 0.5), 90, ancre=(0.5, 0.9))
    for k in range(3):
        s.chemin([(1.5 + k, 1.5 + 2 * k, 1.5), (4.6, 1.5 + 2 * k, 1.5)], AIR, 4)
    u, v = s.p(2.5, 5, 0.2); s.pastille(u, v + 10, "+ pression", AIR, taille=16)
    u, v = s.p(8, 5, 0.2); s.pastille(u + 20, v + 30, "volume sinistré", FUM, taille=16)
    s.texte(1190 - 330, 690 - 170, "Différence de pression", 21, TRAIT, gras=True)
    s.texte(1190 - 330, 690 - 146, "volume protégé en surpression (ex. escalier)", 16, "#4B5563")
    s.legende(40, 900, [("#DBEAFE", "amenée d'air neuf (partie basse)"), ("#E5E7EB", "évacuation des fumées (partie haute)")], taille=16)
    s.texte(560, 925, "⊕  ventilateur (soufflage ou extraction mécanique)", 17, TRAIT)
    s.bandeau([
        ("Objet : extraire en début d'incendie une partie des fumées et gaz de combustion pour maintenir praticables les cheminements", 18, TRAIT),
        ("d'évacuation ; le désenfumage peut aussi limiter la propagation et faciliter l'intervention des secours (DF 1).", 18, TRAIT),
        ("Méthodes : balayage (apport d'air neuf + évacuation des fumées), différence de pression, ou combinaison des deux (DF 3).", 18, TRAIT),
        ("Désenfumage mécanique alimenté par une AES ; commandé avant l'extinction automatique à eau en présence d'un SSI de catégorie A.", 18, TRAIT),
    ])
    return s
