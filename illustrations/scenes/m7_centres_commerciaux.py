"""Type M — M 1, M 5, M 7, M 18 : centres commerciaux et mails."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "M7_centres-commerciaux",
    "titre": "Type M : centres commerciaux",
    "articles": ["ERP:M 7", "ERP:M 18", "ERP:M 5", "ERP:M 1", "ERP:M 6"],
    "fiche": "",
    "legende": "Centre commercial : magasins tributaires de mails clos pour accès et évacuation. Exploitations séparées entre elles par des parois incombustibles CF (½ h au moins), sans exigence vers le mail. Mail désenfumé comme un local de plus de 1 000 m² ; boutiques de moins de 300 m² non désenfumées. Sas de 6 m² et portes CF 1 h à 3 m l'une de l'autre vers un parc de stationnement.",
    "ecarts": [
        "Effectif : 1 personne pour 5 m² de mail ; boutiques de moins de 300 m² : 1 pour 6 m² quel que soit le niveau (M 2). Hall réunissant le rez-de-chaussée et 4 niveaux admis seulement dans le mail, avec extinction automatique (M 6 § 1 bis).",
    ],
}

ROUGE = "#C1121F"
BLEU = "#1D4ED8"


def dessiner():
    s = Scene(1600, 1160, echelle=14, origine=(430, 250))
    s.cartouche("Type M : centres commerciaux", "Mail, boutiques et intercommunication avec un parc de stationnement", "M 5 · M 7 · M 18")
    h = 3.0
    L, P = 52, 26
    s.sol(-2, -2, L + 4, P + 8, "#E5E7EB", trait=None)
    s.sol(0, 10, L, 6, "#EDE9FE", ep=1.4)                        # mail
    for i in range(6):
        s.sol(i * 8.66, 0, 8.66, 10, "#FBF3E4" if i % 2 else "#FEF9EE", ep=1.2)
        s.sol(i * 8.66, 16, 8.66, 10, "#FBF3E4" if i % 2 == 0 else "#FEF9EE", ep=1.2)
    v = [mur(0, 0, L, 0, h), mur(0, 0, 0, 10, h), mur(L, 0, L, 10, h), mur(0, 16, 0, P, 1.0), mur(L, 16, L, P, 1.0), mur(0, P, L, P, 1.0)]
    for i in range(1, 6):
        x = i * 8.66
        v += [mur(x, 0, x, 10, h, ep=0.35, pal=MUR_PF), mur(x, 16, x, P, 1.0, ep=0.35, pal=MUR_PF)]
    s.volumes(v)
    # vitrines côté mail (sans exigence)
    for i in range(6):
        s.poly([(i * 8.66 + 0.4, 10, 0), (i * 8.66 + 8.2, 10, 0), (i * 8.66 + 8.2, 10, 2.4), (i * 8.66 + 0.4, 10, 2.4)], BLEU_VITRE[1], ep=1.4, opacite=0.7)
    # écran de cantonnement du mail
    s.boite(0, 10, h - 0.8, L, 0.15, 0.8, ("#FDE68A", "#FCD34D", "#F59E0B"), ep=1.2, opacite=0.7)
    # exutoires du mail
    for x in (8, 22, 36, 48):
        s.boite(x - 1, 12, h + 0.05, 2, 2, 0.3, GRIS, ep=1.4)
    # sas en bout de mail vers le parc de stationnement
    s.sol(L, 11, 3, 4, "#F3F4F6", ep=1.4)
    s.sol(L + 3, 6, 9, 14, ENROBE_CLAIR, ep=1.2)
    s.boite(L - 0.15, 11, 0, 0.3, 4, 2.2, MUR_CF, ep=1.4)
    s.boite(L + 2.85, 11, 0, 0.3, 4, 2.2, MUR_CF, ep=1.4)
    s.boite(L, 10.8, 0, 3, 0.2, 2.6, MUR_CF, ep=1.2)
    for (x, y) in [(10, 13), (20, 12), (30, 14), (42, 13)]:
        s.personne((x, y, 0), 28, 1 + x % 4, x % 3 == 0)
    u, v_ = s.p(26, 13, 0); s.pastille(u, v_ + 10, "mail", "#6D28D9", taille=18)
    s.repere((17.3, 5, h), "parois entre exploitations incombustibles,\nCF du degré de la structure (½ h au moins)", du=-200, dv=-150, couleur=ROUGE, taille=16)
    s.repere((35, 10, 1.4), "pas d'exigence de résistance au feu\nentre boutique et mail", du=230, dv=-180, couleur="#4B5563", taille=16)
    s.repere((48, 13, h + 0.3), "mail désenfumé comme un local\n> 1 000 m² (classe 3, IT 246)", du=200, dv=-60, couleur="#4B5563", taille=16)
    s.repere((4, 21, 1.0), "boutique < 300 m² : pas de désenfumage,\npas d'écran imposé vers le mail", du=-40, dv=250, couleur="#B45309", taille=16)
    s.repere((L + 1.5, 15, 1.2), "sas ≥ 6 m², portes CF 1 h (EI 60) à fermeture\nautomatique distantes d'au moins 3 m", du=-60, dv=220, couleur=ROUGE, taille=16)
    u, v_ = s.p(L + 7, 13, 0); s.etiquette(u + 40, v_ + 40, "parc de stationnement", "#374151", 15, gras=False)
    s.bandeau([
        ("Centre commercial : groupement d'établissements au sens de R. 143-21 du CCH, sous la responsabilité d'un responsable unique de sécurité.", 18, TRAIT),
        ("Bars, kiosques, aires de repos dans le mail : accord écrit du responsable unique et maintien de la largeur des dégagements (M 8).", 18, TRAIT),
        ("Réserve et vente sans isolement si l'exploitation fait moins de 300 m² et est sprinklée (M 7 § 4). SSI : catégorie B en 1re catégorie (M 30).", 18, TRAIT),
    ])
    return s
