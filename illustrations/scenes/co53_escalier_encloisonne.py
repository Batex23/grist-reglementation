"""CO 50, CO 52, CO 53 — Escalier encloisonné."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "CO53_escalier-encloisonne",
    "titre": "Escalier encloisonné",
    "articles": ["ERP:CO 53", "ERP:CO 52", "ERP:CO 50", "ERP:CO 54"],
    "fiche": "C.15",
    "legende": "Cage continue jusqu'au niveau d'évacuation, parois CF du degré de stabilité de la structure, un seul accès par niveau par bloc-porte PF ½ h à ferme-porte (hauteur ≤ 2,20 m), désenfumée ou à l'abri des fumées, sans communication avec la cage desservant les sous-sols ni local annexe.",
    "ecarts": [
        "Désenfumage des escaliers : instruction technique relative au désenfumage dans les ERP (IT 246), à laquelle renvoie CO 53.",
        "Portes palières d'ascenseur en cage encloisonnée : E 30 (CO 53 § 3).",
    ],
}

ROUGE = "#C1121F"
FUMEE = "#6B7280"


def volee(x0, x1, y, larg, z0, dz, n=9):
    """Volée droite de x0 vers x1 (sens quelconque), montant de dz."""
    out = []
    w = (x1 - x0) / n
    for k in range(n):
        xa = x0 + k * w
        out.append(dict(x=min(xa, xa + w), y=y, z=z0, dx=abs(w), dy=larg, dz=dz * (k + 1) / n, pal=BETON, ep=1.1))
    return out


def dessiner():
    s = Scene(1600, 1160, echelle=45, origine=(640, 610))
    s.cartouche("Escalier encloisonné", "Protection des escaliers par encloisonnement — ERP", "CO 50 · CO 52 · CO 53")
    X, Y, hn, N = 6.0, 3.2, 3.0, 3
    s.sol(-3, -3, 14, 10, "#E5E7EB", trait=None)
    v = [dict(x=-0.3, y=-0.3, z=0, dx=0.3, dy=Y + 0.3, dz=N * hn, pal=MUR_CF), dict(x=0, y=-0.3, z=0, dx=X, dy=0.3, dz=N * hn, pal=MUR_CF)]
    for k in range(N):
        z0 = k * hn
        v.append(dict(x=4.6, y=0, z=z0 - 0.2 if k else 0, dx=X - 4.6, dy=Y, dz=0.2 if k else 0.05, pal=BETON, ep=1.4))
        if k < N - 1 or True:
            v += volee(4.6, 1.0, 0, 1.45, z0, hn / 2)
            v.append(dict(x=0, y=0, z=z0 + hn / 2 - 0.2, dx=1.0, dy=Y, dz=0.2, pal=BETON, ep=1.4))
            v += volee(1.0, 4.6, Y - 1.45, 1.45, z0 + hn / 2, hn / 2)
    s.volumes([b for b in v if b["z"] < N * hn - 0.5])
    # parois avant en transparence (coupe)
    s.poly([(0, Y, 0), (X, Y, 0), (X, Y, N * hn), (0, Y, N * hn)], MUR_CF[1], trait=ROUGE, ep=2, opacite=0.22, tirets="8 6")
    s.poly([(X, 0, 0), (X, Y, 0), (X, Y, N * hn), (X, 0, N * hn)], MUR_CF[2], trait=ROUGE, ep=2, opacite=0.30)
    s.poly([(0, 0, N * hn), (X, 0, N * hn), (X, Y, N * hn), (0, Y, N * hn)], "#F3F4F6", trait=TRAIT, ep=2, opacite=0.55)
    for k in range(N):
        z0 = k * hn
        s.poly([(X, 0.9, z0), (X, 2.2, z0), (X, 2.2, z0 + 2.2), (X, 0.9, z0 + 2.2)], "#E8A39C" if k else "#3F8F5A", ep=2)
        u, v_ = s.p(X, 2.1, z0 + 1.1); s.items.append(f'<circle cx="{u:.1f}" cy="{v_:.1f}" r="3.5" fill="{TRAIT}"/>')
    # désenfumage : exutoire en partie haute, amenée d'air en partie basse
    s.boite(2.0, 1.0, N * hn, 1.6, 1.2, 0.5, GRIS, ep=1.6)
    s.icone("fumee_01", (2.8, 1.6, N * hn + 0.6), 120, ancre=(0.5, 0.95))
    s.poly([(X, 2.5, 0.2), (X, 3.0, 0.2), (X, 3.0, 0.8), (X, 2.5, 0.8)], "#FFFFFF", ep=1.6)
    for i in range(3):
        s.ligne((X, 2.55, 0.35 + i * 0.17), (X, 2.95, 0.35 + i * 0.17), TRAIT, 1)
    s.chemin([(X + 0.2, 1.55, 0.5), (X + 2.6, 1.55, 0.05)], "#15803D", 5)

    s.cote((X, 0.9, hn), (X, 0.9, hn + 2.2), "≤ 2,20 m", decal=(0, -0.9, 0), dx_txt=58)
    s.repere((X, 1.6, 2 * hn + 1.6), "un seul accès par niveau :\nbloc-porte PF ½ h à ferme-porte", du=260, dv=-60, couleur=ROUGE, taille=17)
    s.repere((X, 0.4, 2 * hn - 0.6), "parois CF du degré de\nstabilité de la structure", du=290, dv=40, couleur=ROUGE, taille=17)
    s.repere((2.8, 1.6, N * hn + 0.5), "désenfumage en partie haute\n(ou cage mise à l'abri des fumées)", du=-330, dv=10, couleur=FUMEE, taille=17)
    s.repere((X, 2.75, 0.5), "amenée d'air", du=230, dv=60, couleur=FUMEE, taille=17)
    s.repere((X + 1.6, 1.55, 0.2), "débouché sur l'extérieur\n(ou à moins de 20 m d'une sortie)", du=60, dv=150, couleur="#15803D", taille=17)

    s.legende(40, 600, [(MUR_CF[1], "volume d'encloisonnement")], taille=16)
    s.texte(40, 690, "Interdits dans la cage :", 18, TRAIT, gras=True)
    for i, t in enumerate(["• conduits présentant des risques d'incendie", "  ou d'enfumage (sauf électricité propre)", "• accès à un local annexe (sanitaire, dépôt…)", "• communication directe avec la cage", "  desservant les sous-sols (CO 50 § 2)"]):
        s.texte(40, 718 + 24 * i, t, 16, TRAIT)

    s.bandeau([
        ("Tous les escaliers et ascenseurs sont protégés (encloisonnés ou à l'air libre), sauf exceptions de CO 52 § 3 ; parois en matériaux", 18, TRAIT),
        ("incombustibles. Cage continue jusqu'au niveau d'évacuation ; escaliers d'étages et de sous-sols sans cheminement direct (CO 50).", 18, TRAIT),
        ("Parois CF du degré de stabilité de la structure (paroi sur le vide de façade : CO 20) ; un seul accès par niveau, blocs-portes PF ½ h", 18, TRAIT),
        ("à ferme-porte, hauteur 2,20 m au plus ; si la cage est traversée par une circulation, portes à fermeture automatique.", 18, TRAIT),
    ])
    return s
