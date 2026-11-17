"""CO 39 et CO 40 — Locaux en sous-sol : définition, majoration d'effectif, enfouissement."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "CO39_sous-sol",
    "titre": "Locaux en sous-sol",
    "articles": ["ERP:CO 39", "ERP:CO 40"],
    "fiche": "C.15",
    "legende": "Sous-sol : plafond à moins de 1 m au-dessus des seuils extérieurs, ou plancher à plus de 1 m en dessous. Au-delà de 2 m de profondeur et 100 personnes, effectif arrondi à la centaine et majoré de 10 % par mètre. Un seul niveau de sous-sol accessible, à 6 m au plus.",
    "ecarts": [
        "La majoration d'effectif sert au calcul des dégagements, pas au classement de l'établissement.",
    ],
}

ROUGE = "#C1121F"
TERRE = "#C9B79C"


def dessiner():
    s = Scene(1600, 1160)
    s.cartouche("Locaux en sous-sol", "Définition, calcul des dégagements et enfouissement maximal — coupe", "CO 39 · CO 40")
    k = 74
    sol = 430
    Z = lambda z: sol - z * k
    def rect(x, y, w, h, fill, sw=2.2, extra=""):
        s.items.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" stroke="{TRAIT}" stroke-width="{sw}"{extra}/>')
    rect(0, sol, 1600, 1160 - sol, TERRE, 0)
    rect(0, 100, 1600, sol - 100, "#EEF5FB", 0)
    s.items.append(f'<line x1="0" y1="{sol}" x2="1600" y2="{sol}" stroke="#4B7F33" stroke-width="8"/>')
    # bâtiment en coupe
    rect(200, Z(3.5), 900, 3.5 * k, "#FBF8F2")
    rect(200, Z(0), 900, 6.0 * k, "#F6F1E7")
    rect(180, Z(0) - 10, 940, 20, BETON[1])                      # plancher RDC (sous-face à 0 m)
    rect(180, Z(3.5) - 10, 940, 20, BETON[1])
    rect(180, Z(-6), 940, 20, BETON[1])
    rect(180, Z(3.5) - 10, 20, 9.5 * k + 20, BEIGE[1]); rect(1100, Z(3.5) - 10, 20, 9.5 * k + 20, BEIGE[1])
    # escalier sous-sol
    for i in range(14):
        hm = (i + 1) * (6 * k / 14)
        rect(1080 - (14 - i) * 18, Z(-6) - hm + 10, 18, hm - 10, BETON[0], 1.2)
    s.texte(1250, Z(0) - 14, "niveau moyen des seuils extérieurs", 16, "#374151")
    # cotes
    def cote(x, z1, z2, t, dx=14):
        mid = f"m{len(s.defs)}"; s.defs.append(f'<marker id="{mid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{ROUGE}"/></marker>')
        s.items.append(f'<line x1="{x}" y1="{Z(z1)}" x2="{x}" y2="{Z(z2)}" stroke="{ROUGE}" stroke-width="3" marker-start="url(#{mid})" marker-end="url(#{mid})"/>')
        s.etiquette(x + dx, (Z(z1) + Z(z2)) / 2, t, ROUGE, 18, ancre="start")
    for z, t in ((1, "+ 1 m"), (-1, "- 1 m"), (-2, "- 2 m"), (-6, "- 6 m")):
        s.items.append(f'<line x1="100" y1="{Z(z)}" x2="1180" y2="{Z(z)}" stroke="#6B7280" stroke-width="1.6" stroke-dasharray="10 7"/>')
        s.texte(92, Z(z) + 6, t, 18, "#374151", gras=True, ancre="end")
    s.texte(92, Z(0) + 6, "0", 18, "#374151", gras=True, ancre="end")
    cote(1200, 0, -2, "pas de majoration\njusqu'à 2 m")
    cote(1200, -2, -6, "effectif arrondi à la centaine\nsupérieure, majoré de 10 %\npar mètre au-delà de 2 m\n(si > 100 personnes)")
    s.texte(240, Z(-0.5), "Local en sous-sol si :", 19, TRAIT, gras=True)
    s.texte(240, Z(-0.5) + 28, "• sous-face du plancher haut à moins de 1 m au-dessus des seuils, ou", 17, TRAIT)
    s.texte(240, Z(-0.5) + 52, "• plancher bas à plus de 1 m en contrebas des seuils.", 17, TRAIT)
    s.texte(240, Z(-3.9), "Un seul niveau de sous-sol accessible au public,", 17, TRAIT, gras=True)
    s.texte(240, Z(-3.9) + 24, "point le plus bas à 6 m au plus sous les seuils (CO 40).", 17, TRAIT, gras=True)
    s.personne((0, 0, 0), 1, 1) if False else None
    for x in (520, 640, 760):
        s.items.append(f'<image x="{x}" y="{Z(-6) - 80}" width="40" height="80" href="data:image/png;base64,{__import__("base64").b64encode(open(os.path.join(SPRITES, "homme101.png"), "rb").read()).decode()}"/>')
    s.bandeau([
        ("Exemple : 260 personnes à 4,5 m de profondeur → 300 arrondi, majoré de 3 × 10 % (2,5 m au-delà de 2 m, comptés 3 m) = 390 personnes", 18, TRAIT),
        ("pour le calcul du nombre et de la largeur des dégagements (CO 38). Plancher non horizontal (salle en gradins) : la moitié au moins", 18, TRAIT),
        ("des personnes doit sortir par des issues dont le seuil est au-dessous du niveau moyen du plancher.", 18, TRAIT),
    ])
    return s
