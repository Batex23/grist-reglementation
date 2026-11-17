"""CO 7 § 3 et § 4 — Couvertures au même niveau, façades en dièdre."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "CO7_isolement-meme-niveau-diedre",
    "titre": "Isolement latéral — couvertures au même niveau, dièdre",
    "articles": ["ERP:CO 7"],
    "fiche": "C.6",
    "legende": "Couvertures au même niveau : paroi d'isolement prolongée de 1 m hors toiture (PF 1 h) ou toiture PF ½ h sur 4 m. Façades formant un dièdre de moins de 135° : bande verticale PF ½ h de 2 m le long de l'arête.",
    "ecarts": [
        "La bande du dièdre peut être réduite à 1 m si le tiers comporte déjà un tel isolement ; elle n'est pas exigée pour un ERP dont le dernier niveau accessible est à moins de 8 m sans locaux à sommeil au-dessus du 1er étage.",
    ],
}

ROUGE = "#C1121F"


def dessiner():
    s = Scene(1600, 1160, echelle=16, origine=(640, 330))
    s.cartouche("Isolement latéral — même niveau, dièdre", "ERP contigu à un tiers : couvertures au même niveau et façades en angle", "CO 7 § 3-4")
    hb = s.motif("hb", "#1D4ED8", 2.4, 12, -45)
    hr = s.motif("hr", ROUGE, 2.4, 11, 45)
    H = 12

    s.sol(-8, -8, 54, 40, VERT_GAZON, trait=None)
    s.sol(-8, 26, 54, 6, ENROBE, ep=1.2)
    # ERP : en avancée (x 0→20, y 0→22) ; tiers : x 20→38, y 0→11 → dièdre rentrant de 90° en (20, 11)
    s.boite(0, 0, 0, 20, 22, H, BEIGE)
    s.fenetres_y(0, 22, 0, 20, H, 6, 4)
    s.fenetres_x(20, 11, 0, 11, H, 2, 4)
    s.boite(20, 0, 0, 18, 11, H, GRIS)
    s.fenetres_y(20, 11, 0, 18, H, 5, 4)
    s.fenetres_x(38, 0, 0, 11, H, 3, 4)
    # bande verticale PF ½ h de 2 m sur l'ERP, le long de l'arête du dièdre
    s.poly([(20, 11, 0), (20, 13, 0), (20, 13, H), (20, 11, H)], hr, trait=ROUGE, ep=2.6)
    # paroi d'isolement prolongée de 1 m hors toiture (x = 20, y 0 → 11)
    s.boite(19.8, 0, H, 0.4, 11, 1.0, ("#F7C6C2", "#EE9D96", "#D9776F"), ep=2)
    # variante : toiture PF ½ h sur 4 m côté tiers
    s.sol(20.2, 0, 4, 11, hb, trait="#1D4ED8", ep=2.2, z=H)

    s.cote((20, 13, 0.2), (20, 11, 0.2), "2 m", decal=(1.8, 0, 0), dx_txt=-60, dy_txt=26)
    s.cote((19.8, 0, H), (19.8, 0, H + 1), "1 m", decal=(0, -1.6, 0), dx_txt=-50, dy_txt=-14)
    s.cote((20.2, 0, H), (24.2, 0, H), "4 m", decal=(0, -1.6, 0), dy_txt=-30, dx_txt=40)
    s.repere((20, 12, 6), "dièdre < 135° : bande verticale\nPF ½ h de 2 m le long de l'arête", du=40, dv=230, couleur=ROUGE, taille=18)
    s.repere((19.9, 5, H + 1), "paroi d'isolement prolongée\nde 1 m hors toiture, PF 1 h", du=-330, dv=-110, couleur=ROUGE, taille=18)
    s.repere((23, 6, H), "ou toiture PF ½ h\nsur 4 m", du=300, dv=-110, couleur="#1D4ED8", taille=18)
    u, v = s.p(10, 11, H); s.pastille(u, v, "ERP", ROUGE, taille=20)
    u, v = s.p(30, 5.5, H); s.pastille(u, v + 8, "Tiers", "#4B5563", taille=20)
    s.icone("arbre_01", (42, 6, 0), 56)

    s.bandeau([
        ("Couvertures au même niveau : paroi d'isolement prolongée hors toiture sur au moins 1 m par une paroi PF 1 h,", 19, TRAIT),
        ("ou l'une des toitures en éléments PF ½ h sur 4 m mesurés horizontalement depuis la couverture voisine.", 19, TRAIT),
        ("Façades de l'ERP et du tiers formant un dièdre de moins de 135° : bande d'isolement verticale PF ½ h de 2 m le long de l'arête", 19, TRAIT),
        ("(1 m si le tiers en comporte déjà une). Non exigée si dernier niveau accessible < 8 m et pas de sommeil au-dessus du 1er étage.", 17, "#4B5563"),
    ])
    return s
