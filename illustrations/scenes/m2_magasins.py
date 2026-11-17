"""Type M — M 2, M 12, M 16, M 49 : magasins de vente."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "M2_magasins",
    "titre": "Type M : magasins de vente",
    "articles": ["ERP:M 2", "ERP:M 16", "ERP:M 49", "ERP:M 12", "ERP:M 13", "ERP:M 26"],
    "fiche": "",
    "legende": "Effectif : 1 personne pour 3 m² en sous-sol, rez-de-chaussée et 1er étage, 6 m² au 2e, 15 m² au-delà (9 m² en faible densité). Réserves d'approche non isolées : 300 m³ (500 sprinklé), 6 m de côté, 8 m entre elles, 1/10 de la surface de vente. Réserves : communication directe possible par portes CF 1 h à fermeture automatique.",
    "ecarts": [
        "Volume unitaire des réserves : 1 500 m³ (3 000 m³ si le public n'a pas accès au-dessus et l'établissement occupe tout le bâtiment), 5 000 / 10 000 m³ si sprinklées (M 49).",
        "Défense : au-delà de 3 000 m² de vente, extinction automatique à eau et RIA (M 26).",
    ],
}

ROUGE = "#C1121F"


def dessiner():
    s = Scene(1600, 1160, echelle=16.5, origine=(470, 240))
    s.cartouche("Type M : magasins de vente", "Surface de vente, réserves d'approche et réserves", "M 2 · M 16 · M 49")
    h = 2.6
    L, P = 50, 28
    s.sol(-2, -2, L + 4, P + 4, "#E5E7EB", trait=None)
    s.sol(0, 0, 36, P, "#FBF8F2", ep=1.4)
    s.sol(36, 0, 14, P, "#FCE3E1", ep=1.4)
    v = [mur(0, 0, L, 0, h), mur(0, 0, 0, P, h), mur(L, 0, L, P, h), mur(0, P, 4, P, 0.8), mur(8, P, 28, P, 0.8), mur(32, P, L, P, 0.8)]
    v += [mur(36, 0, 36, 12, h, ep=0.45, pal=MUR_CF), mur(36, 15, 36, P, h, ep=0.45, pal=MUR_CF)]
    s.volumes(v)
    s.boite(35.8, 12, 0, 0.4, 3, 2.4, MUR_CF, ep=1.4, opacite=0.55)
    # rayonnages (îlots) et circulations principales matérialisées
    for x in (4, 12, 20):
        for y in (4, 12, 20):
            s.boite(x, y, 0, 5, 1.2, 1.8, ("#E7D3B5", "#D4B88E", "#B89468"), ep=1.1)
    s.sol(0, 9, 36, 0.12, "#15803D", trait=None)
    # réserves d'approche
    for y in (1, 18):
        s.boite(29, y, 0, 6, 6, 2.4, ("#FEF3C7", "#FDE68A", "#F59E0B"), ep=1.4)
    # stock dans la réserve
    for x in (39, 44):
        s.boite(x, 2, 0, 3, 22, 3.0, ("#D6C3A5", "#C4A57C", "#9C7F57"), ep=1.2)
    for (x, y) in [(10, 9.5), (17, 16), (24, 7), (6, 24)]:
        s.personne((x, y, 0), 28, 1 + x % 4, x % 2 == 1)
    s.cote((29, 7, 0), (35, 7, 0), "≤ 6 m", decal=(0, 0, 0), rappel=False, dy_txt=-30, dx_txt=60)
    s.cote((32, 7, 0), (32, 18, 0), "≥ 8 m", decal=(0, 0, 0), rappel=False, dx_txt=-60, dy_txt=10)
    s.repere((32, 4, 2.4), "réserve d'approche non isolée :\n300 m³ (500 m³ sprinklée), « Sans issue,\ninterdit au public », 1/10 de la surface", du=120, dv=-210, couleur="#B45309", taille=16)
    s.repere((36, 13.5, 2.0), "porte CF 1 h à fermeture automatique\nasservie à la détection (M 49)", du=350, dv=210, couleur=ROUGE, taille=16)
    s.repere((43, 20, 3.0), "réserve : local à risques importants\n1 500 m³ (3 000 m³) par unité", du=300, dv=-130, couleur=ROUGE, taille=16)
    s.repere((14, 9, 0.05), "circulations principales matérialisées\nau sol, joignant deux sorties (M 13)", du=-200, dv=200, couleur="#15803D", taille=16)

    x0, y0 = 40, 770
    s.items.append(f'<rect x="{x0}" y="{y0}" width="560" height="190" rx="10" fill="#FFFFFF" stroke="#9CA3AF" stroke-width="1.5"/>')
    s.texte(x0 + 20, y0 + 32, "Effectif théorique du public (M 2)", 18, TRAIT, gras=True)
    for i, (a, b) in enumerate([("sous-sol, rez-de-chaussée, 1er étage", "1 pers. / 3 m²"), ("2e étage", "1 pers. / 6 m²"), ("étages supérieurs", "1 pers. / 15 m²"), ("magasin à faible densité (tout niveau)", "1 pers. / 9 m²")]):
        s.texte(x0 + 20, y0 + 66 + 30 * i, a, 16, TRAIT)
        s.texte(x0 + 540, y0 + 66 + 30 * i, b, 16, ROUGE, gras=True, ancre="end")
    s.bandeau([
        ("Surface de vente : surfaces accessibles au public, circulations comprises, hors réserves et locaux annexes. Assujettis : 100 personnes", 18, TRAIT),
        ("en sous-sol ou en étages, 200 au total (M 1). Exploitations à risques particuliers au sens de CO 6, sauf si sprinklées (M 4).", 18, TRAIT),
        ("Escaliers : non protégés seulement en R+1 ; protégés au-delà des trois premiers niveaux, moitié au moins du nombre et de la largeur (M 12).", 18, TRAIT),
    ])
    return s
