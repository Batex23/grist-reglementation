"""CO 10 — Franchissement des parois d'isolement et des aires libres."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "CO10_franchissement",
    "titre": "Franchissement d'une paroi d'isolement",
    "articles": ["ERP:CO 10"],
    "fiche": "C.6",
    "legende": "Communication entre l'ERP et un tiers : dispositif CF 2 h (CF ½ h dans les cas de CO 29, CO 35 et CO 41), portes à ferme-porte ou à fermeture automatique, non utilisable pour l'évacuation sauf exceptions, maintenance par l'exploitant de l'ERP.",
    "ecarts": [],
}

ROUGE = "#C1121F"


def dessiner():
    s = Scene(1600, 1160, echelle=26, origine=(760, 250))
    s.cartouche("Franchissement d'une paroi d'isolement", "Communication entre un ERP et un tiers contigu", "CO 10")
    s.sol(-3, -3, 36, 22, VERT_GAZON, trait=None)
    s.sol(0, 0, 14, 14, SOL_INT, ep=1.4)
    s.sol(14, 0, 16, 14, "#EEF0F3", ep=1.4)
    # porte ouverte (débattement côté tiers) dans la paroi d'isolement
    s.arc_sol((14, 6.0), 1.2, 90, 20, 0, ROUGE, 1.6)
    v = []
    # murs extérieurs
    v += [mur(0, 0, 14, 0), mur(14, 0, 30, 0, pal=GRIS), mur(0, 0, 0, 14), mur(30, 0, 30, 14, h=2, pal=GRIS)]
    v += [mur(0, 14, 5, 14, h=1.2), mur(6.5, 14, 14, 14, h=1.2), mur(14, 14, 30, 14, h=1.2, pal=GRIS)]
    # paroi d'isolement CF 2 h avec bloc-porte
    v += [mur(14, 0, 14, 6, h=3, ep=0.45, pal=MUR_CF), mur(14, 7.2, 14, 14, h=3, ep=0.45, pal=MUR_CF)]
    v += [dict(x=13.78, y=6, z=2.2, dx=0.45, dy=1.2, dz=0.8, pal=MUR_CF)]
    s.volumes(v)
    s.vantail((14.2, 6.0), 1.2, 20, 2.15, "#D9776F")
    # ferme-porte
    u, v_ = s.p(14.1, 6.2, 2.15); s.items.append(f'<rect x="{u - 9:.1f}" y="{v_ - 5:.1f}" width="18" height="7" rx="2" fill="#374151"/>')

    s.personne((5, 8, 0), 34, 5); s.personne((9, 4, 0), 34, 2, femme=True)
    s.personne((22, 9, 0), 34, 6)
    u, v_ = s.p(7, 7, 3.2); s.pastille(u, v_ - 30, "ERP", ROUGE, taille=22)
    u, v_ = s.p(22, 5, 3.2); s.pastille(u, v_ - 30, "Tiers", "#4B5563", taille=22)
    s.repere((14, 3, 2.4), "paroi d'isolement\nCF 2 h", du=-60, dv=-150, couleur=ROUGE, taille=18)
    s.repere((14, 6.5, 1.2), "bloc-porte CF 2 h\n(CF ½ h : CO 29, CO 35, CO 41)\nferme-porte ou fermeture\nautomatique", du=330, dv=-90, couleur=ROUGE, taille=18)

    s.legende(40, 760, [("#F7C6C2", "paroi et dispositif coupe-feu"), (SOL_INT, "établissement recevant du public"), ("#EEF0F3", "locaux occupés par un tiers")], taille=17)

    s.bandeau([
        ("Franchissement prévu par le règlement ou admis après avis de la commission : dispositif CF 2 h (CF ½ h dans les cas de CO 29 § 2,", 19, TRAIT),
        ("CO 35 § 5 et CO 41 § 2), portes munies d'un ferme-porte ou à fermeture automatique, pas d'évacuation du public sauf CO 35 § 5 et CO 41 § 2,", 19, TRAIT),
        ("maintenance sous la responsabilité de l'exploitant de l'ERP.", 19, TRAIT),
        ("Aire libre franchie par un passage (souterrain, rez-de-chaussée, passerelle) : désenfumable s'il est clos, parois et blocs-portes PF ½ h", 17, "#4B5563"),
        ("au droit des façades, sans potentiel calorifique, évacuation seulement vers l'extérieur ou un dégagement protégé.", 17, "#4B5563"),
    ])
    return s
