"""CO 25 — Compartiments."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "CO25_compartiments",
    "titre": "Distribution par compartiments",
    "articles": ["ERP:CO 25"],
    "fiche": "C.12",
    "legende": "Au moins deux compartiments par niveau, de capacité comparable ; pas d'exigence de résistance au feu entre locaux à l'intérieur ; parois limites CF selon la structure ; deux communications au plus, par bloc-porte va-et-vient ou sas ; une issue de 2 UP vers l'extérieur ou un dégagement protégé au-delà de 100 personnes.",
    "ecarts": [
        "Autorisés seulement lorsque les dispositions particulières du type d'établissement le prévoient (surface ou effectif maximal fixé par type).",
    ],
}

ROUGE = "#C1121F"


def dessiner():
    s = Scene(1600, 1160, echelle=17, origine=(560, 230))
    s.cartouche("Distribution par compartiments", "Volumes sans exigence de cloisonnement intérieur — ERP", "CO 25")
    L, P, h = 44, 26, 1.6
    s.sol(-3, -3, L + 6, P + 6, VERT_GAZON, trait=None)
    s.sol(0, 0, 22, P, "#FBF3E4", ep=1.4)
    s.sol(22, 0, 22, P, "#EAF2FB", ep=1.4)
    s.sol(18, 10, 8, 6, "#F3F4F6", ep=1.2)                          # circulation principale
    v = [mur(0, 0, L, 0, h), mur(0, 0, 0, P, h), mur(L, 0, L, P, h), mur(0, P, 4, P, h), mur(6.4, P, 36, P, h), mur(38.4, P, L, P, h)]
    # paroi entre compartiments avec un sas (deux portes va-et-vient)
    v += [mur(22, 0, 22, 11, h, ep=0.45, pal=MUR_CF), mur(22, 15, 22, P, h, ep=0.45, pal=MUR_CF)]
    v += [mur(20, 11, 24, 11, h, pal=MUR_CF), mur(20, 15, 24, 15, h, pal=MUR_CF)]
    v += [mur(20, 11, 20, 12.2, h, pal=MUR_CF), mur(20, 13.8, 20, 15, h, pal=MUR_CF), mur(24, 11, 24, 12.2, h, pal=MUR_CF), mur(24, 13.8, 24, 15, h, pal=MUR_CF)]
    # quelques cloisons légères sans exigence
    v += [mur(6, 0, 6, 8, h, pal=GRIS), mur(0, 8, 6, 8, h, pal=GRIS), mur(36, 18, 36, P, h, pal=GRIS), mur(36, 18, 44, 18, h, pal=GRIS)]
    s.volumes(v)
    for xd in (20, 24):
        s.arc_sol((xd, 12.2), 0.8, 90, 40, 0, ROUGE, 1.4); s.arc_sol((xd, 12.2), 0.8, 90, 140, 0, ROUGE, 1.4)
    for (x, y, k, f) in [(10, 16, 1, 0), (14, 6, 2, 1), (4, 19, 3, 0), (30, 8, 4, 1), (34, 15, 5, 0), (40, 6, 6, 1)]:
        s.personne((x, y, 0), 28, k, bool(f))
    s.chemin([(12, 18, 0.1), (5.2, 18, 0.1), (5.2, P + 1.5, 0.1)], "#15803D", 4.5)
    s.chemin([(32, 18, 0.1), (37.2, 18, 0.1), (37.2, P + 1.5, 0.1)], "#15803D", 4.5)
    u, v_ = s.p(10, 10, 0); s.pastille(u, v_, "Compartiment 1", "#B45309", taille=19)
    u, v_ = s.p(32, 22, 0); s.pastille(u, v_, "Compartiment 2", "#1D4ED8", taille=19)
    s.repere((22, 22, 1.6), "paroi CF selon la structure\n(½ h, 1 h ou 1 h ½)", du=330, dv=-250, couleur=ROUGE, taille=18)
    s.repere((22, 13, 1.6), "sas : blocs-portes va-et-vient\nPF de degré moitié", du=420, dv=-110, couleur=ROUGE, taille=18)
    s.repere((5.2, P, 0.8), "issue de 2 UP (> 100 pers.) vers l'extérieur\nou un dégagement protégé (PF ½ h à ferme-porte)", du=120, dv=230, couleur="#15803D", taille=17)
    s.repere((6, 4, 1.6), "cloisons intérieures\nsans exigence", du=-220, dv=-60, couleur="#4B5563", taille=17)

    # tableau parois
    x0, y0 = 1150, 640
    rows = [("Structure", "Parois limites"), ("aucune exigence", "CF ½ h"), ("SF ½ h", "CF ½ h"), ("SF 1 h", "CF 1 h"), ("SF 1 h ½", "CF 1 h ½")]
    s.items.append(f'<rect x="{x0}" y="{y0}" width="380" height="{36 * len(rows) + 8}" rx="8" fill="#FFFFFF" stroke="#9CA3AF" stroke-width="1.5"/>')
    for i, (a, b) in enumerate(rows):
        s.texte(x0 + 16, y0 + 30 + 36 * i, a, 17, TRAIT, gras=(i == 0))
        s.texte(x0 + 230, y0 + 30 + 36 * i, b, 17, ROUGE if i else TRAIT, gras=True)
    s.bandeau([
        ("Chaque niveau comporte au moins deux compartiments de capacité du même ordre ; un compartiment peut couvrir deux niveaux si sa", 18, TRAIT),
        ("surface totale ne dépasse pas la surface moyenne d'un compartiment. Deux dispositifs de communication au plus, sur les circulations principales :", 18, TRAIT),
        ("bloc-porte va-et-vient PF du degré de la paroi, ou sas à blocs-portes va-et-vient PF de degré moitié (fermeture automatique possible).", 18, TRAIT),
        ("Circulations parfaitement matérialisées ; chaque compartiment est désenfumé.", 18, TRAIT),
    ])
    return s
