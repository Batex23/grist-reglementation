"""DF 5 — Désenfumage ou mise à l'abri des fumées des escaliers."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *
from scenes_communs import cage_escalier

META = {
    "id": "DF5_desenfumage-escaliers",
    "titre": "Désenfumage des escaliers",
    "articles": ["ERP:DF 5"],
    "fiche": "DF 3",
    "legende": "Escalier encloisonné désenfumé par balayage naturel (exutoire de 1 m² en partie haute, amenée d'air de 1 m² en partie basse, commande manuelle au niveau d'accès) ou mis en surpression ; jamais d'extraction mécanique des fumées.",
    "ecarts": [
        "Valeurs de l'instruction technique n° 246 (2004) : ouvrant de 1 m² géométrique en partie haute, amenée d'air de 1 m² en partie basse, commande manuelle à proximité de l'accès principal (réarmement possible depuis le niveau d'accès).",
        "Surpression : différence de pression de 20 à 80 Pa entre l'escalier et les volumes adjacents, toutes portes fermées.",
    ],
}

ROUGE = "#C1121F"
AIR = "#2563EB"
FUM = "#6B7280"


def dessiner():
    s = Scene(1600, 1160, echelle=45, origine=(560, 610))
    s.cartouche("Désenfumage des escaliers", "Escalier encloisonné : balayage naturel ou surpression", "DF 5")
    X, Y, hn, N = cage_escalier(s)
    # exutoire ouvert (1 m²) et fumées
    s.boite(2.3, 1.1, N * hn, 1.2, 1.0, 0.25, GRIS, ep=1.6)
    s.poly([(2.3, 1.1, N * hn + 0.25), (3.5, 1.1, N * hn + 0.25), (3.5, 1.1, N * hn + 1.1), (2.3, 1.1, N * hn + 0.95)], "#E5E7EB", trait=TRAIT, ep=1.6)
    s.icone("fumee_01", (2.9, 1.6, N * hn + 0.4), 120, ancre=(0.5, 0.95))
    # amenée d'air (1 m²) en façade, partie basse
    s.poly([(X, 2.25, 0.2), (X, 3.1, 0.2), (X, 3.1, 1.4), (X, 2.25, 1.4)], "#DBEAFE", trait=AIR, ep=2.4)
    s.chemin([(X + 2.4, 2.7, 0.8), (X + 0.2, 2.7, 0.8)], AIR, 5)
    # commande manuelle au niveau d'accès
    s.poly([(X, 0.25, 1.1), (X, 0.65, 1.1), (X, 0.65, 1.6), (X, 0.25, 1.6)], "#F59E0B", trait=TRAIT, ep=1.6)
    s.repere((2.9, 1.6, N * hn + 0.3), "exutoire en partie haute\n1 m² (surface géométrique)", du=-320, dv=-40, couleur=FUM, taille=17)
    s.repere((X, 2.7, 1.4), "amenée d'air en partie basse\n1 m² (ouvrant en façade)", du=260, dv=70, couleur=AIR, taille=17)
    s.repere((X, 0.45, 1.6), "commande manuelle au niveau d'accès\n(ouverture simultanée haut et bas)", du=250, dv=-90, couleur="#B45309", taille=17)

    # encart surpression
    x0, y0 = 1040, 120
    s.items.append(f'<rect x="{x0}" y="{y0}" width="520" height="300" rx="10" fill="#FFFFFF" stroke="#9CA3AF" stroke-width="1.5"/>')
    s.texte(x0 + 20, y0 + 34, "Ou mise à l'abri des fumées (surpression)", 18, TRAIT, gras=True)
    cx, cy = x0 + 70, y0 + 70
    s.items.append(f'<rect x="{cx}" y="{cy}" width="120" height="200" fill="#DBEAFE" stroke="{TRAIT}" stroke-width="2.4"/>')
    s.items.append(f'<rect x="{cx + 120}" y="{cy}" width="260" height="200" fill="#F3F4F6" stroke="{TRAIT}" stroke-width="2.4"/>')
    s.items.append(f'<circle cx="{cx + 60}" cy="{cy + 170}" r="18" fill="#fff" stroke="{AIR}" stroke-width="3"/><path d="M{cx + 50},{cy + 170} L{cx + 70},{cy + 170} M{cx + 60},{cy + 160} L{cx + 60},{cy + 180}" stroke="{AIR}" stroke-width="3"/>')
    for yy in (cy + 50, cy + 110):
        s.items.append(f'<line x1="{cx + 90}" y1="{yy}" x2="{cx + 160}" y2="{yy}" stroke="{AIR}" stroke-width="4"/>')
        s.items.append(f'<path d="M{cx + 160},{yy - 8} L{cx + 176},{yy} L{cx + 160},{yy + 8} z" fill="{AIR}"/>')
    s.texte(cx + 60, cy + 30, "escalier", 15, AIR, gras=True, ancre="middle")
    s.texte(cx + 250, cy + 30, "circulation / niveau", 15, "#4B5563", ancre="middle")
    s.texte(cx + 250, cy + 110, "Δp 20 à 80 Pa", 22, ROUGE, gras=True, ancre="middle")
    s.texte(cx + 250, cy + 140, "portes fermées", 15, "#4B5563", ancre="middle")

    s.bandeau([
        ("Escaliers encloisonnés : désenfumés par balayage naturel ou mis en surpression par rapport aux volumes adjacents ;", 18, TRAIT),
        ("en aucun cas les fumées ne sont extraites mécaniquement. Escalier non encloisonné : désenfumé par le volume avec lequel il communique,", 18, TRAIT),
        ("séparé des niveaux inférieurs par des écrans de cantonnement, si ces volumes sont eux-mêmes désenfumés.", 18, TRAIT),
        ("Sous-sols : pas d'exigence jusqu'à deux niveaux ; au-delà, désenfumage ou mise à l'abri obligatoire (sauf parcs de stationnement).", 18, TRAIT),
    ])
    return s
