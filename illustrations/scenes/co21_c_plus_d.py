"""CO 21 — Règle du C + D (propagation verticale du feu par les façades)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "CO21_C-plus-D",
    "titre": "Règle du C + D",
    "articles": ["ERP:CO 21", "ERP:CO 19", "ERP:CO 20"],
    "fiche": "C.9",
    "legende": "Obstacle au passage du feu d'un étage à l'autre : C (distance verticale entre baies) + D (saillie horizontale) ≥ 1 m si la masse combustible mobilisable M ≤ 130 MJ/m², ≥ 1,30 m au-delà.",
    "ecarts": [
        "La définition de C, D et M et les solutions sans essai sont dans l'instruction technique relative aux façades (IT 249, version 2010).",
        "Règle exigée : sommeil au-dessus du 1er étage, dernier niveau > 8 m avec secteurs ou compartiments, droit des planchers hauts des locaux à risques importants et des planchers d'isolement avec un tiers ; non exigée si l'ERP occupe tout le bâtiment et est sprinklé ou équipé d'un SSI A.",
    ],
}

ROUGE = "#C1121F"


def dessiner():
    s = Scene(1600, 1160)
    s.cartouche("Règle du C + D", "Propagation verticale du feu par les façades comportant des baies — coupe sur façade", "CO 21 § 3")
    k = 118                               # pixels par mètre
    xe, ep = 700, 0.3 * k                 # nu extérieur de la façade
    sol = 980
    Z = lambda z: sol - z * k
    def rect(x, y, w, h, fill, sw=2.4):
        s.items.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" stroke="{TRAIT}" stroke-width="{sw}" stroke-linejoin="round"/>')
    s.items.append(f'<rect x="{xe}" y="100" width="{1600 - xe}" height="{sol - 100}" fill="#EEF5FB"/>')     # extérieur
    s.items.append(f'<rect x="0" y="100" width="{xe - ep}" height="{sol - 100}" fill="#FBF8F2"/>')           # intérieur
    rect(0, sol, 1600, 24, VERT_GAZON, 0)
    for n in range(2):
        z0 = 3 * n
        rect(xe - ep, Z(z0 + 1.0), ep, 1.0 * k - (12 if n else 0), BEIGE[1])                          # allège
        rect(xe - ep, Z(z0 + 3) + 12, ep, 0.4 * k - 12, BEIGE[1])                                    # linteau
        s.items.append(f'<rect x="{xe - ep * 0.55:.1f}" y="{Z(z0 + 2.6):.1f}" width="{ep * 0.18:.1f}" height="{1.6 * k:.1f}" fill="{BLEU_VITRE[1]}" stroke="{TRAIT}" stroke-width="1.6"/>')
        rect(180, Z(z0 + 3) - 12, xe - 180, 24, BETON[1])                                            # plancher haut
    rect(xe, Z(3) - 12, 0.8 * k, 22, BETON[0])                                                       # balcon
    s.items.append(f'<rect x="{xe + 0.8 * k - 6:.1f}" y="{Z(4.0):.1f}" width="6" height="{1.0 * k - 12:.1f}" fill="#9CA3AF" stroke="{TRAIT}" stroke-width="1.4"/>')
    # feu sortant de la baie basse, dévié par la saillie
    s.items.append(f'<image x="{xe - 10}" y="{Z(2.75):.1f}" width="170" height="{170 * 459 / 393:.1f}" href="data:image/png;base64,{__import__("base64").b64encode(open(os.path.join(SPRITES, "feu_01.png"), "rb").read()).decode()}"/>')
    # cotes
    def cote_v(x, z1, z2, t):
        y1, y2 = Z(z1), Z(z2)
        s.items.append(f'<line x1="{xe - ep}" y1="{y1}" x2="{x + 10}" y2="{y1}" stroke="{ROUGE}" stroke-width="1.4" stroke-dasharray="5 4"/><line x1="{xe - ep}" y1="{y2}" x2="{x + 10}" y2="{y2}" stroke="{ROUGE}" stroke-width="1.4" stroke-dasharray="5 4"/>')
        mid = f"mc{len(s.defs)}"; s.defs.append(f'<marker id="{mid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{ROUGE}"/></marker>')
        s.items.append(f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="{ROUGE}" stroke-width="3" marker-start="url(#{mid})" marker-end="url(#{mid})"/>')
        s.etiquette(x - 46, (y1 + y2) / 2, t, ROUGE, 30)
    cote_v(xe - ep - 140, 2.6, 4.0, "C")
    y = Z(3) - 70
    mid = f"md{len(s.defs)}"; s.defs.append(f'<marker id="{mid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{ROUGE}"/></marker>')
    s.items.append(f'<line x1="{xe}" y1="{y}" x2="{xe + 0.8 * k}" y2="{y}" stroke="{ROUGE}" stroke-width="3" marker-start="url(#{mid})" marker-end="url(#{mid})"/>')
    s.items.append(f'<line x1="{xe + 0.8 * k}" y1="{y - 10}" x2="{xe + 0.8 * k}" y2="{Z(3) - 12}" stroke="{ROUGE}" stroke-width="1.4" stroke-dasharray="5 4"/>')
    s.etiquette(xe + 0.4 * k, y - 34, "D", ROUGE, 30)
    s.texte(60, 150, "Intérieur", 24, "#6B7280", gras=True)
    s.texte(xe + 40, 150, "Extérieur", 24, "#6B7280", gras=True)
    s.texte(xe - ep - 24, Z(1.8), "baie", 18, "#374151", ancre="end")
    s.texte(xe - ep - 24, Z(4.8), "baie", 18, "#374151", ancre="end")
    s.texte(300, Z(3) - 24, "plancher", 18, "#374151")
    s.texte(xe + 0.8 * k + 16, Z(3) + 8, "saillie incombustible", 18, "#374151")
    s.texte(xe + 0.8 * k + 16, Z(3) + 30, "(balcon, auvent…)", 18, "#374151")

    x0, y0 = 1060, 680
    s.items.append(f'<rect x="{x0}" y="{y0}" width="500" height="250" rx="10" fill="#FFFFFF" stroke="#9CA3AF" stroke-width="1.5"/>')
    s.texte(x0 + 24, y0 + 44, "C + D ≥ 1,00 m", 34, ROUGE, gras=True)
    s.texte(x0 + 24, y0 + 74, "si M ≤ 130 MJ/m²", 19, TRAIT)
    s.texte(x0 + 24, y0 + 134, "C + D ≥ 1,30 m", 34, ROUGE, gras=True)
    s.texte(x0 + 24, y0 + 164, "si M > 130 MJ/m²", 19, TRAIT)
    s.texte(x0 + 24, y0 + 214, "M : masse combustible mobilisable", 16, "#4B5563")
    s.texte(x0 + 24, y0 + 236, "de la façade (IT façades)", 16, "#4B5563")

    s.bandeau([
        ("C : distance verticale entre le haut d'une baie et le bas de la baie de l'étage supérieur ; D : saillie horizontale des éléments", 19, TRAIT),
        ("incombustibles (balcons, auvents) entre ces baies. Orifices de ventilation de moins de 200 cm² non pris en compte.", 19, TRAIT),
        ("Façades : revêtements, menuiseries, occultations et garde-corps M 3 ou D-s3, d0 ; M 2 ou C-s3, d0 si le C + D n'est pas appliqué (CO 20).", 18, "#4B5563"),
    ])
    return s
