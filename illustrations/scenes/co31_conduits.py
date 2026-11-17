"""CO 30 à CO 33 — Conduits et gaines traversant les parois."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "CO31_conduits-gaines",
    "titre": "Conduits et gaines",
    "articles": ["ERP:CO 31", "ERP:CO 30", "ERP:CO 32", "ERP:CO 33"],
    "fiche": "C.14",
    "legende": "Diamètre ≤ 75 mm et eau en charge : sans exigence. De 75 à 315 mm : pare-flammes de traversée 30 min (CF 15 min en horizontal). Au-delà de 315 mm : gaine incombustible CF de la paroi (60 min au plus) ou clapet ; gaine verticale recoupée tous les deux niveaux, trappes PF ½ h.",
    "ecarts": [
        "Ne visent pas les conduits de ventilation, de fumées et de gaz (chapitres CH et GZ) — CO 30 § 1.",
        "PVC B-s3, d0 marqué NF Me ≤ 125 mm : PF 30 min réputé satisfait avec un renforcement (manchon de longueur = paroi + 1 diamètre) ; métal à point de fusion > 850 °C : réputé satisfait.",
        "Les classements M de l'ancienne fiche sont conservés par le texte ; équivalences européennes : M 0 ≈ A2-s1, d0 ; M 1 ≈ B-s3, d0.",
    ],
}

ROUGE = "#C1121F"


def tuyau_x(s, y, z, r, x0, x1, couleur="#9CA3AF"):
    """Conduit horizontal le long de x (cylindre approché par une boîte fine + section)."""
    s.boite(x0, y - r, z - r, x1 - x0, 2 * r, 2 * r, ("#E5E7EB", couleur, "#6B7280"), ep=1.6)


def dessiner():
    s = Scene(1600, 1160, echelle=70, origine=(470, 300))
    s.cartouche("Conduits et gaines", "Traversée des parois résistant au feu — ERP", "CO 30 à CO 33")
    # paroi verticale résistant au feu (plan x = 4) : conduits dessinés derrière puis devant la paroi
    s.sol(-1, -1, 10, 9, "#F3F4F6", trait=None)
    tubes = [(1.2, 2.2, 0.04, "#93C5FD"), (3.0, 2.2, 0.10, "#A1A1AA"), (5.2, 2.0, 0.25, "#D4D4D8")]
    for y, z, r, c in tubes:
        tuyau_x(s, y, z, r, 1.5, 4.0, c)
    s.boite(4, 0, 0, 0.25, 7, 3.0, MUR_CF, ep=1.8)
    for y, z, r, c in tubes:
        tuyau_x(s, y, z, r, 4.25, 7.0, c)
    s.boite(4.25, 2.86, 2.06, 0.3, 0.28, 0.28, ("#FCD34D", "#F59E0B", "#D97706"), ep=1.4)   # traversée PF 30
    s.boite(4.25, 4.9, 1.7, 0.4, 0.6, 0.6, ("#FCA5A5", "#EF4444", "#B91C1C"), ep=1.6)       # clapet
    s.repere((6.5, 1.2, 2.24), "Ø ≤ 75 mm, eau en charge :\naucune exigence", du=230, dv=-190, couleur="#2563EB", taille=17)
    s.repere((4.4, 3.0, 2.3), "75 < Ø ≤ 315 mm : pare-flammes\nde traversée 30 min (CF 15 min\nsi conduit horizontal)", du=400, dv=-60, couleur="#B45309", taille=17)
    s.repere((4.45, 5.2, 2.3), "Ø > 315 mm : gaine CF de la paroi\n(60 min max) ou clapet", du=400, dv=60, couleur=ROUGE, taille=17)
    s.repere((4.12, 0.5, 1.0), "paroi résistant au feu", du=-170, dv=170, couleur=ROUGE, taille=17)

    # encart gaine verticale
    x0, y0 = 860, 640
    s.items.append(f'<rect x="{x0}" y="{y0}" width="690" height="360" rx="10" fill="#FFFFFF" stroke="#9CA3AF" stroke-width="1.5"/>')
    s.texte(x0 + 20, y0 + 34, "Gaine verticale (coupe)", 18, TRAIT, gras=True)
    gx = x0 + 230
    for i, yy in enumerate((y0 + 110, y0 + 210, y0 + 310)):
        s.items.append(f'<rect x="{x0 + 40}" y="{yy}" width="610" height="16" fill="{BETON[1]}" stroke="{TRAIT}" stroke-width="1.6"/>')
    s.items.append(f'<rect x="{gx}" y="{y0 + 60}" width="80" height="280" fill="#FEE2E2" stroke="{ROUGE}" stroke-width="3"/>')
    s.items.append(f'<rect x="{gx + 30}" y="{y0 + 60}" width="20" height="280" fill="#D4D4D8" stroke="{TRAIT}" stroke-width="1.4"/>')
    s.items.append(f'<rect x="{gx}" y="{y0 + 110}" width="80" height="16" fill="#6B7280" stroke="{TRAIT}" stroke-width="1.6"/>')
    s.items.append(f'<rect x="{gx}" y="{y0 + 310}" width="80" height="16" fill="#6B7280" stroke="{TRAIT}" stroke-width="1.6"/>')
    s.items.append(f'<rect x="{gx + 80}" y="{y0 + 240}" width="10" height="44" fill="#F59E0B" stroke="{TRAIT}" stroke-width="1.4"/>')
    s.texte(gx + 110, y0 + 150, "recoupement incombustible", 15, TRAIT)
    s.texte(gx + 110, y0 + 170, "tous les deux niveaux", 15, TRAIT)
    s.texte(gx + 110, y0 + 270, "trappe de visite PF ½ h", 15, "#B45309")
    s.texte(x0 + 40, y0 + 80, "gaine CF", 15, ROUGE, gras=True)
    s.bandeau([
        ("Conduits traversant un local à risques courants ou moyens (CO 31) : exigences aux traversées de planchers ; dans un même niveau,", 18, TRAIT),
        ("seulement pour les recoupements de circulation, secteurs, compartiments et locaux à sommeil. Paroi ERP / tiers : CF de traversée = paroi.", 18, TRAIT),
        ("Local à risques importants (CO 32) : au-delà de 125 mm, conduit le traversant sans le desservir CF de traversée = paroi franchie.", 18, TRAIT),
        ("Conduits séparés, entraxe ≥ somme des diamètres (sauf PF 30 ou en gaine). Vide-ordures et monte-charge : CO 33.", 18, TRAIT),
    ])
    return s
