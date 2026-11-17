"""GN 8, CO 34 § 6, CO 57 à CO 60 — Espaces d'attente sécurisés."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "CO59_espace-attente-securise",
    "titre": "Espace d'attente sécurisé",
    "articles": ["ERP:CO 59", "ERP:GN 8", "ERP:CO 57", "ERP:CO 58", "ERP:CO 60", "ERP:AS 4"],
    "fiche": "C.15",
    "legende": "Au moins deux espaces par niveau accessible en fauteuil roulant, près d'un escalier normal, atteints dans les distances de CO 43 et CO 49 ; 2 fauteuils au moins chacun ; parois comme les locaux à sommeil, portes CF à ferme-porte ; ouvrant en façade ou protection contre les fumées ; éclairage de sécurité ; balisage.",
    "ecarts": [
        "L'ancienne fiche présentait le « local d'attente » de l'ascenseur (AS 4) comme règle générale. Depuis l'arrêté du 24 septembre 2009, GN 8 impose des espaces d'attente sécurisés (CO 59) ; AS 4 n'est plus qu'une des solutions équivalentes (CO 57).",
        "Capacité : 2 fauteuils jusqu'à 50 personnes au niveau, + 1 fauteuil par tranche de 50 personnes, sans réduire la largeur du dégagement menant à l'issue.",
    ],
}

ROUGE = "#C1121F"
BLEU = "#1D4ED8"


def dessiner():
    s = Scene(1600, 1160, echelle=24, origine=(640, 250))
    s.cartouche("Espace d'attente sécurisé", "Évacuation différée des personnes en situation de handicap — ERP", "GN 8 · CO 59")
    h = 1.2
    L, P = 30, 16
    s.sol(-2, -2, L + 4, P + 4, "#E5E7EB", trait=None)
    s.sol(0, 0, L, P, SOL_INT, ep=1.4)
    s.sol(0, 6, L, 3, "#E9F3EA", ep=1.2)                         # circulation
    s.sol(20, 0, 4, 6, "#D6E6F7", ep=1.2)                         # escalier protégé
    for k in range(1, 9):
        s.ligne((20.3, k * 0.62, 0), (23.7, k * 0.62, 0), "#5B7DB1", 1.2)
    s.sol(24, 0, 6, 6, "#DCEBFF", ep=1.2)                         # EAS
    v = [mur(0, 0, L, 0, h), mur(0, 0, 0, P, h), mur(L, 0, L, 6, h), mur(L, 9, L, P, h), mur(0, P, L, P, h)]
    v += [mur(20, 0, 20, 6, h, pal=MUR_BLEU), mur(20, 6, 21, 6, h, pal=MUR_BLEU), mur(22.4, 6, 24, 6, h, pal=MUR_BLEU)]
    v += [mur(24, 0, 24, 6, h, ep=0.35, pal=MUR_CF), mur(24, 6, 26, 6, h, ep=0.35, pal=MUR_CF), mur(27.4, 6, L, 6, h, ep=0.35, pal=MUR_CF)]
    v += [mur(0, 6, 20, 6, h, pal=MUR_PF), mur(0, 9, 12, 9, h, pal=MUR_PF), mur(13.4, 9, L, 9, h, pal=MUR_PF), mur(10, 9, 10, P, h), mur(10, 0, 10, 6, h)]
    s.volumes(v)
    s.vantail((26, 6), 1.4, -60, 2.1, "#E8A39C")
    # ouvrant en façade de l'EAS
    s.poly([(L, 1.8, 0.9), (L, 4.2, 0.9), (L, 4.2, 2.2), (L, 1.8, 2.2)], BLEU_VITRE[2], ep=1.8)
    for (x, y) in [(26, 2.2), (28.3, 2.2)]:
        u, v_ = s.p(x, y, 0.9); s.ufr(u, v_, 40)
    u, v_ = s.p(27, 3, 2.4); s.pastille(u, v_ - 20, "EAS", BLEU, taille=20)
    s.chemin([(3, 12, 0.1), (3, 7.5, 0.1), (26.7, 7.5, 0.1), (26.7, 5.4, 0.1)], BLEU, 4.5, "12 7")
    s.personne((14, 12, 0), 30, 6); s.personne((6, 3, 0), 30, 2, True)

    s.repere((24, 3, h), "parois du degré prévu pour les locaux\nà sommeil (CO 24), porte CF à ferme-porte\n(même degré que la paroi, 1 h au plus)", du=-430, dv=-120, couleur=ROUGE, taille=17)
    s.repere((L, 3, 2.2), "ouvrant en façade manœuvrable depuis\nl'espace (ou à l'abri des fumées /\ndésenfumé) · visible des secours", du=170, dv=170, couleur=BLEU, taille=17)
    s.repere((22, 3, h), "à proximité d'un escalier normal", du=-60, dv=-200, couleur="#1D4ED8", taille=17)
    s.repere((12, 7.5, 0.1), "distances de CO 43 / CO 49", du=-260, dv=170, couleur=BLEU, taille=17)

    x0, y0 = 1050, 100
    s.items.append(f'<rect x="{x0}" y="{y0}" width="510" height="280" rx="10" fill="#FFFFFF" stroke="#9CA3AF" stroke-width="1.5"/>')
    s.texte(x0 + 20, y0 + 32, "Solutions équivalentes (CO 57)", 18, TRAIT, gras=True)
    for i, t in enumerate(["• zone protégée ou secteurs, avec moyen de signaler", "  sa présence (fenêtre, interphone, bouton d'appel)", "• paliers d'escaliers protégés agrandis, portes CF", "• espace à l'air libre protégé du rayonnement 1 h", "• ascenseurs d'évacuation et local d'attente (AS 4, AS 5)", "Exonérations (CO 60) : simple rez-de-chaussée, sorties", "de plain-pied à chaque niveau, mesures validées."]):
        s.texte(x0 + 20, y0 + 64 + 28 * i, t, 15.5, TRAIT if i < 5 else "#4B5563")

    s.bandeau([
        ("Au moins 2 espaces par niveau accessible aux fauteuils roulants (1 si un seul escalier exigé) ; 2 fauteuils par espace au minimum,", 18, TRAIT),
        ("2 fauteuils jusqu'à 50 personnes au niveau puis 1 par tranche de 50. Éclairage de sécurité (EC 10), consignes affichées,", 18, TRAIT),
        ("balisage spécifique repérable du public et des secours, report sur les plans schématiques. Interdit dans les locaux à risques particuliers.", 18, TRAIT),
    ])
    return s
