"""Type T — T 2, T 21, T 23 : salles d'expositions et stands."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso import *

META = {
    "id": "T23_stands-expositions",
    "titre": "Type T : expositions et stands",
    "articles": ["ERP:T 23", "ERP:T 21", "ERP:T 2", "ERP:T 22", "ERP:T 24"],
    "fiche": "",
    "legende": "Effectif : 1 personne / m² (salons temporaires), 1 / 9 m² (expositions permanentes). Stands en M 3. Stands couverts ou à étage : moins de 300 m², distants de 4 m au moins, plafonds pleins limités à 10 % de la surface du niveau, un seul niveau de surélévation ; au-delà de 50 m², moyens d'extinction et agent de sécurité.",
    "ecarts": [
        "Vélums horizontaux autorisés le temps de la manifestation, en M 1 (M 2 si sprinklé) (T 22). Chargé de sécurité désigné par l'organisateur ; demande d'autorisation deux mois avant l'ouverture (T 5, T 6).",
    ],
}

ROUGE = "#C1121F"


def dessiner():
    s = Scene(1600, 1160, echelle=15, origine=(760, 300))
    s.cartouche("Type T : expositions et stands", "Hall d'exposition temporaire", "T 21 · T 23")
    L, P = 46, 30
    s.sol(-2, -2, L + 4, P + 4, "#E5E7EB", trait=None)
    s.sol(0, 0, L, P, "#F3F4F6", ep=1.4)
    s.volumes([mur(0, 0, 0, P, 6, ep=0.4), mur(0, 0, L, 0, 6, ep=0.4)])
    # allées
    s.sol(0, 12, L, 4, "#E9F3EA", trait=None)
    s.sol(20, 0, 4, P, "#E9F3EA", trait=None)
    # stands ouverts (M3)
    for (x, y) in [(2, 2), (8, 2), (14, 2), (2, 18), (8, 18), (14, 18), (26, 2), (32, 2), (38, 2)]:
        s.boite(x, y, 0, 5, 8, 0.1, ("#E0E7FF", "#C7D2FE", "#A5B4FC"), ep=1)
        s.boite(x, y, 0, 5, 0.15, 2.5, ("#E0E7FF", "#C7D2FE", "#A5B4FC"), ep=1)
        s.boite(x, y, 0, 0.15, 8, 2.5, ("#E0E7FF", "#C7D2FE", "#A5B4FC"), ep=1)
    # stands couverts / à étage
    s.boite(26, 18, 0, 8, 10, 3, ("#FDE68A", "#FCD34D", "#F59E0B"), ep=1.6)
    s.boite(26, 18, 3, 8, 10, 0.3, ("#FEF3C7", "#FDE68A", "#F59E0B"), ep=1.6)
    s.boite(38, 18, 0, 7, 10, 3, ("#FDE68A", "#FCD34D", "#F59E0B"), ep=1.6)
    s.cote((34, 23, 0), (38, 23, 0), "≥ 4 m", rappel=False, dy_txt=-26)
    for (x, y) in [(10, 14), (22, 8), (30, 14), (22, 24)]:
        s.personne((x, y, 0), 26, 1 + x % 4, x % 2 == 0)
    s.repere((30, 23, 3.3), "stand couvert ou à étage : < 300 m², un seul niveau\nde surélévation, plafonds pleins ≤ 10 % du niveau ;\n> 50 m² : extincteurs + agent de sécurité", du=200, dv=-230, couleur="#B45309", taille=16)
    s.repere((4.5, 2, 2.5), "stands ouverts : ossature et cloisons M 3,\nsans gêner désenfumage, détection, sprinklers", du=-330, dv=60, couleur="#4338CA", taille=16)
    s.repere((22, 14, 0.05), "allées : dégagements selon l'effectif\n(1 personne par m² en salon temporaire)", du=-300, dv=230, couleur="#15803D", taille=16)
    s.bandeau([
        ("Effectif : 1 personne par m² de la surface totale des salles accessibles au public (salons, foires), 1 pour 9 m² (expositions permanentes).", 18, TRAIT),
        ("Podiums, estrades, gradins de plus de 0,30 m : revêtements M 3 (M 4 si 20 m² au plus) ; matériaux exposés sans exigence, sauf en décoration", 18, TRAIT),
        ("de plus de 20 % des cloisons ou plafonds (T 21). Hall partiellement utilisé : séparations M 3 résistant à la poussée du public (T 24).", 18, TRAIT),
    ])
    return s
