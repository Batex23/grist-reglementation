"""EL 5 et EL 11 — Locaux de service électrique, coupure générale."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "EL5_locaux-service-electrique",
    "titre": "Locaux de service électrique",
    "articles": ["ERP:EL 5", "ERP:EL 11"],
    "fiche": "EL 2",
    "legende": "Local réservé aux personnes qualifiées, identifié et facile à atteindre par les secours ; isolement selon le matériel (CF 2 h et franchissement CF 1 h sans communication avec le public, ou CF 1 h et porte CF ½ h, ou local ordinaire) ; extincteur adapté, éclairage de sécurité et BAPI.",
    "ecarts": [
        "Mise hors tension générale : inaccessible au public, facile à atteindre par les secours, sans couper l'alimentation normale des installations de sécurité (EL 11 § 1).",
    ],
}

ROUGE = "#C1121F"
ORANGE = "#B45309"


def dessiner():
    s = Scene(1600, 1160, echelle=44, origine=(700, 400))
    s.cartouche("Locaux de service électrique", "Isolement, accès des secours et équipements — ERP", "EL 5 · EL 11")
    h = 2.6
    L, P = 9, 6
    s.sol(-1, -1, L + 6, P + 4.5, "#E5E7EB", trait=None)
    s.sol(0, 0, L, P, SOL_INT, ep=1.4)
    s.sol(0, P, L + 4, 3, "#F3F4F6", ep=1.2)               # dégagement non accessible au public
    s.volumes([dict(x=-0.3, y=0, z=0, dx=0.3, dy=P, dz=h, pal=MUR_CF), dict(x=0, y=-0.3, z=0, dx=L, dy=0.3, dz=h, pal=MUR_CF),
               dict(x=L, y=0, z=0, dx=0.3, dy=P + 0.3, dz=h, pal=MUR_CF),
               dict(x=0, y=P, z=0, dx=3, dy=0.3, dz=h, pal=MUR_CF), dict(x=4.4, y=P, z=0, dx=4.6, dy=0.3, dz=h, pal=MUR_CF)])
    # tableaux électriques
    for x in (1.0, 3.2, 5.4):
        s.boite(x, 0.05, 0, 1.8, 0.6, 2.0, ("#E5E7EB", "#D1D5DB", "#9CA3AF"), ep=1.6)
        s.poly([(x + 0.2, 0.65, 0.3), (x + 1.6, 0.65, 0.3), (x + 1.6, 0.65, 1.8), (x + 0.2, 0.65, 1.8)], "#F3F4F6", ep=1.2)
    # plancher haut en transparence
    s.sol(0, 0, L, P, ROUGE, trait=ROUGE, ep=2, z=h + 0.05, opacite=0.18)
    s.vantail((3, P), 1.4, 120, 2.1, "#E8A39C")
    # extincteur CO2, BAES, BAPI
    s.boite(7.7, 0.1, 0, 0.35, 0.35, 0.9, ("#F87171", "#EF4444", "#B91C1C"), ep=1.4)
    s.poly([(L, 2.4, 2.1), (L, 3.2, 2.1), (L, 3.2, 2.35), (L, 2.4, 2.35)], "#16A34A", ep=1.4)
    s.boite(L - 0.45, 4.6, 1.2, 0.4, 0.5, 0.35, ("#FDE68A", "#FBBF24", "#D97706"), ep=1.4)
    # signalisation sur la porte
    u, v = s.p(3.7, P + 0.31, 2.0)
    s.items.append(f'<path d="M{u - 16},{v + 12} L{u + 16},{v + 12} L{u},{v - 16} Z" fill="#FACC15" stroke="{TRAIT}" stroke-width="2"/><path d="M{u + 2},{v - 8} L{u - 4},{v + 3} L{u + 2},{v + 3} L{u - 2},{v + 10}" stroke="{TRAIT}" stroke-width="2" fill="none"/>')
    s.repere((0, 3, h), "parois et plancher haut CF selon le matériel :\na) CF 2 h, franchissement CF 1 h, sans communication\n    directe avec le public · b) CF 1 h, porte CF ½ h\nc) local ordinaire (risques courants)", du=-300, dv=-120, couleur=ROUGE, taille=16)
    s.repere((3.6, P, 1.5), "identifié, facile à atteindre\npar les secours, accès réservé\naux personnes qualifiées", du=-280, dv=160, couleur=ORANGE, taille=16)
    s.repere((7.9, 0.3, 0.9), "extincteur adapté\nau risque électrique", du=300, dv=-80, couleur=ROUGE, taille=16)
    s.repere((L, 2.8, 2.3), "éclairage de sécurité", du=280, dv=0, couleur="#15803D", taille=16)
    s.repere((L - 0.25, 4.85, 1.4), "bloc autonome portable\nd'intervention (BAPI)", du=270, dv=80, couleur="#B45309", taille=16)
    u, v = s.p(6, 7.5, 0); s.pastille(u, v + 10, "dégagement non accessible au public", "#4B5563", taille=15)

    x0, y0 = 40, 800
    s.items.append(f'<rect x="{x0}" y="{y0}" width="760" height="190" rx="10" fill="#FFFFFF" stroke="#9CA3AF" stroke-width="1.5"/>')
    s.texte(x0 + 20, y0 + 34, "Coupure générale et appareillages (EL 11)", 18, TRAIT, gras=True)
    for i, t in enumerate(["• mise hors tension générale inaccessible au public, facile à atteindre par les secours,", "  sans couper l'alimentation normale des installations de sécurité", "• aucune coupure d'urgence accessible au public (sauf enseignes lumineuses)", "• commandes et protections à moins de 2,50 m : manœuvre à clé ou outil"]):
        s.texte(x0 + 20, y0 + 66 + 28 * i, t, 16, TRAIT)
    s.bandeau([
        ("Les locaux de service électrique renferment des matériels électriques et ne sont accessibles qu'aux personnes qualifiées chargées", 18, TRAIT),
        ("de l'entretien et de la surveillance. Leur isolement dépend de la nature des matériels (EL 5 § 3) ; groupes électrogènes (EL 7)", 18, TRAIT),
        ("et batteries (EL 8) ont leurs propres conditions.", 18, TRAIT),
    ])
    return s
