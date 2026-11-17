"""DF 7 et DF 8 — Désenfumage des locaux accessibles au public (naturel)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "DF7_desenfumage-locaux",
    "titre": "Désenfumage des locaux",
    "articles": ["ERP:DF 7", "ERP:DF 8"],
    "fiche": "DF 4",
    "legende": "Locaux de plus de 300 m² (rez-de-chaussée, étage), de plus de 100 m² en sous-sol ou sans ouverture sur l'extérieur : désenfumés, naturellement ou mécaniquement. En naturel : cantons délimités par des écrans, exutoires en partie haute, amenées d'air en partie basse.",
    "ecarts": [
        "Les règles de dimensionnement (cantons, écrans, surface utile des exutoires, amenées d'air) sont dans l'instruction technique n° 246 (2004), qui n'est pas reprise dans la base Légifrance du widget : valeurs à vérifier sur le texte de l'IT.",
        "L'ancienne fiche (1996) donnait Su = 1/200 de la surface pour les locaux de moins de 1 000 m² et le coefficient α au-delà : principe conservé en 2004 ; le coefficient k = 0,3 / 0,5 a été remplacé par la notion de surface utile (SUE) des dispositifs certifiés NF EN 12101-2.",
        "Volume de 3 niveaux au plus en communication (si autorisé par le type) : désenfumé comme un local unique au-delà de 300 m² cumulés (DF 7 § 2). Compartiments : DF 8.",
    ],
}

AIR = "#2563EB"
FUM = "#4B5563"
ROUGE = "#C1121F"


def dessiner():
    s = Scene(1600, 1160)
    s.cartouche("Désenfumage des locaux", "Désenfumage naturel d'un grand local : cantons, exutoires, amenées d'air — coupe", "DF 7 · IT 246")
    k = 36                                  # pixels par mètre
    x0s, sol = 110, 600
    X = lambda x: x0s + x * k
    Z = lambda z: sol - z * k
    L, H = 36, 9
    def rect(x, y, w, h, fill, sw=2.2, extra=""):
        s.items.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" stroke="{TRAIT}" stroke-width="{sw}"{extra}/>')
    rect(0, sol, 1600, 40, VERT_GAZON, 0)
    rect(X(0), Z(H), L * k, H * k, "#FBF8F2")
    # couche de fumée dans le canton sinistré
    s.items.append(f'<rect x="{X(0):.1f}" y="{Z(H):.1f}" width="{18 * k:.1f}" height="{3 * k:.1f}" fill="#6B7280" fill-opacity="0.45"/>')
    rect(X(-0.4), Z(H) - 6, (L + 0.8) * k, 12, BETON[1])                  # toiture
    rect(X(-0.4), Z(H), 0.4 * k, H * k, BEIGE[1]); rect(X(L), Z(H), 0.4 * k, H * k, BEIGE[1])
    rect(X(17.9), Z(H), 0.25 * k, 3 * k, "#F59E0B")                          # écran de cantonnement
    for xe in (5, 13, 23, 31):                                               # exutoires
        ouvert = xe < 18
        rect(X(xe - 1), Z(H) - 18, 2 * k, 12, GRIS[1])
        if ouvert:
            s.items.append(f'<line x1="{X(xe - 1):.1f}" y1="{Z(H) - 18:.1f}" x2="{X(xe - 1) + 30:.1f}" y2="{Z(H) - 64:.1f}" stroke="{TRAIT}" stroke-width="4"/>')
            s.items.append(f'<image x="{X(xe) - 45:.1f}" y="{Z(H) - 160:.1f}" width="90" height="130" href="data:image/png;base64,{__import__("base64").b64encode(open(os.path.join(SPRITES, "fumee_01.png"), "rb").read()).decode()}"/>')
    # amenées d'air basses (façade gauche) et feu
    rect(X(-0.4), Z(2.4), 0.4 * k, 2.1 * k, "#DBEAFE")
    s.items.append(f'<line x1="{X(-2.5):.1f}" y1="{Z(1.3):.1f}" x2="{X(2.5):.1f}" y2="{Z(1.3):.1f}" stroke="{AIR}" stroke-width="6"/><path d="M{X(2.5):.1f},{Z(1.3) - 10:.1f} L{X(2.5) + 18:.1f},{Z(1.3):.1f} L{X(2.5):.1f},{Z(1.3) + 10:.1f} z" fill="{AIR}"/>')
    s.items.append(f'<image x="{X(9) - 50:.1f}" y="{Z(0) - 110:.1f}" width="100" height="117" href="data:image/png;base64,{__import__("base64").b64encode(open(os.path.join(SPRITES, "feu_01.png"), "rb").read()).decode()}"/>')
    for xp in (24, 28):
        s.items.append(f'<image x="{X(xp):.1f}" y="{Z(0) - 64:.1f}" width="32" height="64" href="data:image/png;base64,{__import__("base64").b64encode(open(os.path.join(SPRITES, "homme105.png"), "rb").read()).decode()}"/>')
    def cote_v(x, z1, z2, t, c=ROUGE, dx=12):
        mid = f"m{len(s.defs)}"; s.defs.append(f'<marker id="{mid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>')
        s.items.append(f'<line x1="{X(x)}" y1="{Z(z1)}" x2="{X(x)}" y2="{Z(z2)}" stroke="{c}" stroke-width="3" marker-start="url(#{mid})" marker-end="url(#{mid})"/>')
        s.etiquette(X(x) + dx, (Z(z1) + Z(z2)) / 2, t, c, 17, ancre="start")
    cote_v(37.5, 0, H, "hauteur de\nréférence H")
    cote_v(15.5, 0, H - 3, "hauteur libre\nde fumée ≥ 1,80 m")
    cote_v(1.5, H - 3, H, "épaisseur\nenfumée", c=FUM)
    s.texte(X(9), Z(H - 3) + 34, "canton 1 (sinistré)", 18, ROUGE, gras=True, ancre="middle")
    s.texte(X(27), Z(H - 3) + 34, "canton 2", 18, "#374151", gras=True, ancre="middle")
    s.etiquette(X(18) + 170, Z(H) + 60, "écran de cantonnement (DH 30)", "#B45309", 17)
    s.etiquette(X(13) + 230, Z(H) - 90, "exutoires du canton sinistré ouverts", FUM, 17)
    s.etiquette(X(3) + 60, Z(2.8) - 20, "amenée d'air en partie basse", AIR, 17)
    s.etiquette(X(13), Z(0) + 50, "canton : 1 600 m² et 60 m au plus · seul le canton sinistré est désenfumé", TRAIT, 17, gras=False)

    x0, y0 = 1060, 700
    s.items.append(f'<rect x="{x0}" y="{y0}" width="510" height="300" rx="10" fill="#FFFFFF" stroke="#9CA3AF" stroke-width="1.5"/>')
    s.texte(x0 + 20, y0 + 34, "Repères de l'IT 246 (naturel)", 18, TRAIT, gras=True)
    for i, t in enumerate([
        "• canton : 1 600 m² au plus, 60 m de long au plus",
        "• local ≤ 1 000 m² : SUE ≥ 1/200 de la surface",
        "• au-delà : SUE = α × surface du canton",
        "  (α selon hauteur de référence et hauteur libre)",
        "• toiture ≤ 10 % : tout point à moins de 4 H",
        "  et de 30 m d'un exutoire",
        "• hauteur libre de fumée : 1,80 m au moins",
        "• amenées d'air ≥ surface géométrique des évacuations",
    ]):
        s.texte(x0 + 20, y0 + 66 + 30 * i, t, 16, TRAIT)

    s.bandeau([
        ("Sont désenfumés : locaux de plus de 300 m² en rez-de-chaussée et en étage, de plus de 100 m² en sous-sol, et de plus de 100 m²", 18, TRAIT),
        ("sans ouverture sur l'extérieur — par tirage naturel ou mécanique. Seul le canton sinistré est désenfumé ; les amenées d'air peuvent", 18, TRAIT),
        ("se faire par les cantons voisins. Compartiments à cloisons toute hauteur : circulations et locaux ; plateau paysager : volume entier (DF 8).", 18, TRAIT),
    ])
    return s
