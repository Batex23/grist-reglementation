"""Grille de l'espace « Réglementation applicable ».

Squelette des rubriques (dispositions générales) pour le 1er groupe (livre II)
et pour la 5e catégorie (livre III), règles de rangement des dispositions
particulières, seuils de la 5e catégorie (tableau de l'article PE 2).

Les plages « CO 11-CO 15 » sont développées par build.py sur les articles
réellement présents dans la base ; une référence absente fait échouer le test.
"""

# (chapitre, id, titre, références des dispositions générales)
RUBRIQUES_G1 = [
    ("Classement et généralités", "classement", "Définition, type et catégorie", ["R143-2", "R143-18", "R143-19", "GN 1"]),
    ("Classement et généralités", "groupement", "Groupements d'établissements, locaux de types différents", ["GN 2", "GN 3", "GN 5", "GN 6"]),
    ("Classement et généralités", "adaptation", "Adaptation, existant, aménagement dans un bâtiment existant", ["GN 4", "GN 9", "GN 10", "GN 7"]),
    ("Classement et généralités", "controle", "Contrôle, exploitation, consignes, travaux", ["GE 1-GE 10", "GN 11-GN 14"]),
    ("Implantation", "desserte", "Desserte, voies engins et échelles", ["CO 1", "CO 2"]),
    ("Implantation", "facades_acc", "Façades et baies accessibles", ["CO 3", "CO 4", "CO 5"]),
    ("Implantation", "isolement", "Isolement par rapport aux tiers", ["CO 6-CO 9"]),
    ("Implantation", "franchissement", "Franchissement des parois d'isolement, parcs de stationnement", ["CO 10"]),
    ("Construction", "structures", "Résistance au feu des structures", ["CO 11-CO 15"]),
    ("Construction", "couverture", "Couvertures", ["CO 16-CO 18"]),
    ("Construction", "facades", "Façades (C + D, réaction au feu)", ["CO 19-CO 22"]),
    ("Construction", "distribution", "Distribution intérieure : cloisonnement, secteurs, compartiments", ["CO 23-CO 26"]),
    ("Construction", "locaux", "Locaux à risques, réserves, logements du personnel", ["CO 27-CO 29"]),
    ("Construction", "conduits", "Conduits et gaines", ["CO 30-CO 33"]),
    ("Construction", "amenagements", "Aménagements intérieurs, décoration, mobilier", ["AM 1-AM 20"]),
    ("Construction", "tribunes", "Tribunes", ["CO 61"]),
    ("Dégagements", "conception", "Terminologie et conception des dégagements", ["CO 34", "CO 35"]),
    ("Dégagements", "calcul", "Unités de passage et calcul des dégagements", ["CO 36", "CO 37", "CO 38"]),
    ("Dégagements", "enfouissement", "Locaux en sous-sol, enfouissement", ["CO 39", "CO 40"]),
    ("Dégagements", "accessoires", "Dégagements accessoires et supplémentaires", ["CO 41"]),
    ("Dégagements", "balisage", "Balisage", ["CO 42"]),
    ("Dégagements", "sorties", "Sorties, distances, portes", ["CO 43-CO 48"]),
    ("Dégagements", "escaliers", "Escaliers : distances, protection, conception", ["CO 49-CO 56"]),
    ("Dégagements", "psh", "Évacuation des personnes handicapées, évacuation différée", ["GN 8", "CO 57-CO 60", "AS 4", "AS 5"]),
    ("Désenfumage", "df", "Désenfumage", ["DF 1-DF 10"]),
    ("Chauffage, ventilation, gaz", "ch", "Production de chaleur, combustibles", ["CH 1-CH 27"]),
    ("Chauffage, ventilation, gaz", "ventilation", "Traitement d'air, ventilation, VMC", ["CH 28-CH 43"]),
    ("Chauffage, ventilation, gaz", "appareils", "Appareils indépendants, entretien", ["CH 44-CH 58"]),
    ("Chauffage, ventilation, gaz", "gz", "Installations de gaz", ["GZ 1-GZ 15"]),
    ("Chauffage, ventilation, gaz", "gc", "Appareils de cuisson, grandes cuisines", ["GC 1-GC 22"]),
    ("Électricité, éclairage, ascenseurs", "el", "Installations électriques", ["EL 1-EL 23"]),
    ("Électricité, éclairage, ascenseurs", "ec", "Éclairage normal et de sécurité", ["EC 1-EC 15"]),
    ("Électricité, éclairage, ascenseurs", "as", "Ascenseurs, escaliers mécaniques", ["AS 1-AS 3", "AS 6-AS 11"]),
    ("Moyens de secours", "ms_ext", "Moyens d'extinction, DECI", ["MS 1-MS 40"]),
    ("Moyens de secours", "ms_sp", "Faciliter l'action des sapeurs-pompiers", ["MS 41-MS 44"]),
    ("Moyens de secours", "ssiap", "Service de sécurité incendie", ["MS 45-MS 52"]),
    ("Moyens de secours", "ssi", "SSI : détection, mise en sécurité, alarme", ["MS 53-MS 69"]),
    ("Moyens de secours", "alerte", "Alerte, entretien et vérifications des moyens de secours", ["MS 70-MS 75"]),
]

# 5e catégorie (livre III) : seules s'appliquent ces dispositions, plus celles
# du livre II expressément citées (PE 1 § 1).
RUBRIQUES_G2 = [
    ("Classement et généralités", "classement", "Définition, type et catégorie", ["R143-2", "R143-14", "R143-18", "R143-19", "GN 1", "PE 1", "PE 2", "PE 3"]),
    ("Classement et généralités", "groupement", "Groupements d'établissements, locaux de types différents", ["GN 2", "GN 3", "GN 5", "GN 6"]),
    ("Classement et généralités", "adaptation", "Adaptation, existant", ["GN 4", "GN 9", "GN 10"]),
    ("Classement et généralités", "controle", "Vérifications techniques", ["PE 4"]),
    ("Implantation", "desserte", "Accès des secours", ["PE 7"]),
    ("Implantation", "isolement", "Isolement, parcs de stationnement", ["PE 6"]),
    ("Construction", "structures", "Structures, patios et puits de lumière", ["PE 5"]),
    ("Construction", "locaux", "Locaux à risques particuliers, hydrocarbures", ["PE 9", "PE 10"]),
    ("Construction", "conduits", "Conduits et gaines", ["PE 12"]),
    ("Construction", "amenagements", "Aménagements intérieurs", ["PE 13"]),
    ("Dégagements", "enfouissement", "Enfouissement", ["PE 8"]),
    ("Dégagements", "calcul", "Dégagements", ["PE 11"]),
    ("Dégagements", "psh", "Personnes handicapées", ["GN 8"]),
    ("Désenfumage", "df", "Désenfumage", ["PE 14"]),
    ("Chauffage, ventilation, gaz", "gc", "Installations de cuisson", ["PE 15-PE 19"]),
    ("Chauffage, ventilation, gaz", "ch", "Chauffage, ventilation", ["PE 20-PE 23"]),
    ("Électricité, éclairage, ascenseurs", "el", "Installations électriques, éclairage", ["PE 24"]),
    ("Électricité, éclairage, ascenseurs", "as", "Ascenseurs, escaliers mécaniques", ["PE 25"]),
    ("Moyens de secours", "ms_ext", "Extincteurs, moyens de secours", ["PE 26"]),
    ("Moyens de secours", "ssi", "Alarme, alerte, consignes", ["PE 27"]),
]

# Règles complémentaires pour les établissements avec locaux à sommeil (PE 28 à PE 37)
SOMMEIL = {"structures": ["PE 28"], "amenagements": ["PE 29"], "calcul": ["PE 30"], "ch": ["PE 31"],
           "ssi": ["PE 32", "PE 33", "PE 34", "PE 35"], "el": ["PE 36"], "controle": ["PE 37"]}

# Chapitres du livre III propres à certains types (PE 1 § 2, PE 2 § 1)
CHAP5 = {"O": "PO", "U": "PU", "J": "PU", "X": "PX"}

TYPES = [
    # code, libellé, livre (II = 1er groupe possible, IV = établissements spéciaux)
    ("J", "Structures d'accueil pour personnes âgées et personnes handicapées", "II"),
    ("L", "Salles d'auditions, de conférences, de réunions, de spectacles ou à usage multiple", "II"),
    ("M", "Magasins de vente, centres commerciaux", "II"),
    ("N", "Restaurants et débits de boissons", "II"),
    ("O", "Hôtels et autres établissements d'hébergement", "II"),
    ("P", "Salles de danse et salles de jeux", "II"),
    ("R", "Établissements d'enseignement, colonies de vacances", "II"),
    ("S", "Bibliothèques, centres de documentation", "II"),
    ("T", "Salles d'expositions", "II"),
    ("U", "Établissements de soins", "II"),
    ("V", "Établissements de culte", "II"),
    ("W", "Administrations, banques, bureaux", "II"),
    ("X", "Établissements sportifs couverts", "II"),
    ("Y", "Musées", "II"),
    ("PA", "Établissements de plein air", "IV"),
    ("CTS", "Chapiteaux, tentes et structures itinérantes", "IV"),
    ("SG", "Structures gonflables", "IV"),
    ("OA", "Hôtels-restaurants d'altitude", "IV"),
    ("REF", "Refuges de montagne", "IV"),
    ("PS", "Parcs de stationnement couverts", "IV"),
    ("GA", "Gares accessibles au public", "IV"),
]

# Types où la question des locaux à sommeil se pose en 5e catégorie
SOMMEIL_TYPES = {"J": True, "O": True, "U": False, "R": False}

# Tableau de l'article PE 2 § 1 : seuils du 1er groupe (sous-sol, étages, ensemble des niveaux)
SEUILS = {
    "J": [["Personnes âgées : effectif des résidents", "-", "-", "25"], ["Personnes âgées : effectif total", "-", "-", "100"],
          ["Personnes handicapées : effectif des résidents", "-", "-", "20"], ["Personnes handicapées : effectif total", "-", "-", "100"]],
    "L": [["Auditions, conférences, réunions, pari, associations, quartier, multimédia, salles polyvalentes non X", "100", "-", "200"],
          ["Spectacles, projections (cirques non forains compris), cabarets", "20", "-", "50"]],
    "M": [["Magasins de vente", "100", "100", "200"]],
    "N": [["Restaurants ou débits de boissons", "100", "200", "200"]],
    "O": [["Hôtels ou pensions de famille", "-", "-", "100"]],
    "P": [["Salles de danse ou salles de jeux", "20", "100", "120"]],
    "R": [["Écoles maternelles, crèches, haltes-garderies, jardins d'enfants", "interdit", "1 (20 si un seul niveau en étage)", "100"],
          ["Autres établissements", "100", "100", "200"], ["Établissements avec locaux réservés au sommeil", "-", "-", "30"]],
    "S": [["Bibliothèques ou centres de documentation", "100", "100", "200"]],
    "T": [["Salles d'expositions", "100", "100", "200"]],
    "U": [["Établissements de soins sans hébergement", "-", "-", "100"], ["Établissements de soins avec hébergement", "-", "-", "20"]],
    "V": [["Établissements de culte", "100", "200", "300"]],
    "W": [["Administrations, banques, bureaux", "100", "100", "200"]],
    "X": [["Établissements sportifs couverts", "100", "100", "200"]],
    "Y": [["Musées", "100", "100", "200"]],
    "OA": [["Hôtels-restaurants d'altitude", "-", "-", "20"]],
    "GA": [["Gares aériennes (souterraines et mixtes : 1er groupe quel que soit l'effectif)", "-", "-", "200"]],
    "PA": [["Établissements de plein air", "-", "-", "300"]],
}

# Rangement automatique d'un article de dispositions particulières selon son titre
# (puis le titre de sa section). Premier motif qui correspond.
MOTS = [
    ("ssiap", r"service de s[ée]curit[ée]|personnel de s[ée]curit[ée]|agents? de s[ée]curit[ée]|^surveillance|surveillance de l'[ée]tablissement|poste (?:central )?de s[ée]curit[ée]|formation|organisation (?:globale )?de la s[ée]curit[ée]|organisation de la s[ée]curit[ée]"),
    ("ms_sp", r"faciliter l'action|reconnaissance des installations|sapeurs-pompiers|sauvetage|tours? d'incendie|tr[ée]mies? d'attaque"),
    ("ssi", r"syst[èe]me de s[ée]curit[ée]|\bssi\b|d[ée]tection|alarme|mise en s[ée]curit[ée]|exercices|sonorisation"),
    ("alerte", r"alerte|v[ée]rification|entretien|maintenance"),
    ("ms_ext", r"moyens? de secours|extinction|extincteur|robinet|colonne|sprinkl|d[ée]fense ext[ée]rieure|points? d'eau|mise en [œo]e?uvre"),
    ("df", r"d[ée]senfumage|fum[ée]es"),
    ("ec", r"[ée]clairage|bougies|flammes? nues?"),
    ("el", r"[ée]lectri"),
    ("gz", r"\bgaz\b|hydrocarbures"),
    ("gc", r"cuisson|cuisine|cantines?"),
    ("ventilation", r"ventilation|traitement d'air|a[ée]raulique|conditionnement d'air"),
    ("ch", r"chauffage|combustible|chaufferie|production de chaleur|chemin[ée]es?"),
    ("as", r"ascenseur|trottoirs? roulant|^escaliers? m[ée]caniques"),
    ("escaliers", r"escalier"),
    ("psh", r"handicap|espace d'attente|mise [àa] l'abri|transfert|[ée]vacuation diff[ée]r[ée]e|principes fondamentaux"),
    ("enfouissement", r"sous-sol|enfoui"),
    ("accessoires", r"d[ée]gagements? accessoire"),
    ("balisage", r"balisage|signal[ée]tique|signalisation|visibilit[ée]"),
    ("sorties", r"\bportes?\b|sorties?|issues?|ferme-porte"),
    ("calcul", r"d[ée]gagement|circulation|unit[ée]s? de passage|largeur|distance maximale|vestiaires?"),
    ("controle", r"fumer|consignes|registre|affichage|commission|dossier de s[ée]curit[ée]|visites?\b|attestation|inspection|ouverture au public|obligations|organisateurs|conditions particuli[èe]res d'exploitation|pr[ée]cautions d'exploitation|^exploitation$|modifications|vignettes"),
    ("tribunes", r"tribune|gradin"),
    ("conduits", r"conduits?|gaines?|canalisations?"),
    ("locaux", r"locaux? (?:[àa] risques|pr[ée]sentant|techniques|de service|non accessibles)|r[ée]serves?|stockage|d[ée]p[ôo]t|risques particuliers|produits? dangereux|mati[èe]res"),
    ("amenagements", r"am[ée]nagement|d[ée]cor|mobilier|rideau|tenture|stand|si[èe]ges|r[ée]action au feu|comportement au feu|mat[ée]riaux|v[ée]lum|rev[êe]tement|plafond"),
    ("distribution", r"distribution|compartiment|secteur|cloisonnement|recoupement|zones?\b|isolement des locaux|isolement interne|volumes? libres?|niveaux partiels|atrium|patio"),
    ("isolement", r"isolement|tiers|voisin|contigu|superpos"),
    ("franchissement", r"stationnement|franchissement"),
    ("facades", r"fa[çc]ade"),
    ("couverture", r"couverture|toiture"),
    ("desserte", r"\bacc[èe]s\b|\bvoies?\b|desserte|implantation"),
    ("structures", r"structure|r[ée]sistance au feu|stabilit[ée]|construction|plancher|ossature|mezzanine"),
    ("classement", r"effectif|assujetti|classement|capacit[ée] d'accueil|d[ée]finition|champ d'application|textes applicables|dispositions applicables|r[ée]glementation applicable|g[ée]n[ée]ralit[ée]s"),
]

# Rubrique propre aux types (hors squelette) pour les articles restants
AUTRES = "autres"

# ---------------------------------------------------------------------------
# Modes de calcul de l'effectif (tableau d'aide par niveau)
# (type, id, référence jusqu'au paragraphe, mode de calcul, unité, public par unité,
#  personnel par unité, options) — options : "niveau" (M 2 § 1 a), "res" (résidents J),
#  "noncumul" (effectif non cumulé pour le classement)
U_M2, U_PL, U_BANC, U_ML, U_P = "m²", "places", "m de banc", "ml", "personnes"
METHODES = [
    ("J", "J2-res", "J 2", "Résidents : déclaration du maître d'ouvrage ou du chef d'établissement", "résidents", 1, 0, "res"),
    ("J", "J2-vis", "J 2", "Visiteurs : 1 personne pour 3 résidents", "résidents", 1 / 3, 0, ""),
    ("J", "J2-pers", "J 2", "Personnel en travail effectif : déclaration", U_P, 0, 1, ""),
    ("J", "J2-ext", "J 2", "Salles recevant des personnes extérieures : selon leur utilisation (déclaration)", U_P, 1, 0, ""),
    ("L", "L3-sieges", "L 3 a)", "1 personne par siège ou place de banc numérotée", U_PL, 1, 0, ""),
    ("L", "L3-bancs", "L 3 a)", "1 personne par 0,50 m de banc non numéroté", U_BANC, 2, 0, ""),
    ("L", "L3-debout", "L 3 a)", "3 personnes par m² (sans sièges ni bancs)", U_M2, 3, 0, ""),
    ("L", "L3-prom", "L 3 a)", "5 personnes par mètre linéaire de promenoir ou de file d'attente", U_ML, 5, 0, ""),
    ("L", "L3-cab", "L 3 b)", "4 personnes pour 3 m² (estrades et aménagements fixes déduits)", U_M2, 4 / 3, 0, ""),
    ("L", "L3-poly", "L 3 c)", "1 personne par m² de surface totale de la salle", U_M2, 1, 0, ""),
    ("L", "L3-reu", "L 3 d)", "1 personne par m² de surface totale de la salle", U_M2, 1, 0, ""),
    ("L", "L3-mm", "L 3 e)", "Déclaration, au minimum 1 personne pour 2 m²", U_M2, 0.5, 0, ""),
    ("M", "M2-a", "M 2 § 1 a)", "selon le niveau", U_M2, 1 / 3, 0, "niveau"),
    ("M", "M2-mail", "M 2 § 1 b)", "Mails : 1 personne pour 5 m² de surface totale", U_M2, 0.2, 0, ""),
    ("M", "M2-bout", "M 2 § 1 b)", "Boutique de moins de 300 m² : 1 personne pour 6 m²", U_M2, 1 / 6, 0, ""),
    ("M", "M2-fd", "M 2 § 1 c)", "Faible densité de public : 1 personne pour 9 m²", U_M2, 1 / 9, 0, ""),
    ("M", "M2-pro", "M 2 § 1 d)", "Réservé aux professionnels : déclaration contrôlée du chef d'établissement", U_P, 1, 0, ""),
    ("M", "M2-air", "M 2 § 1 e)", "Aire de vente à l'air libre à dégagements indépendants : non cumulée pour le classement", U_P, 1, 0, "noncumul"),
    ("N", "N2-a", "N 2 a)", "1 personne par m²", U_M2, 1, 0, ""),
    ("N", "N2-decl", "N 2 a)", "Déclaration contrôlée des places assises (dans la limite de 1 personne pour 2 m²)", U_PL, 1, 0, ""),
    ("N", "N2-b", "N 2 b)", "2 personnes par m² (restauration debout)", U_M2, 2, 0, ""),
    ("N", "N2-c", "N 2 c)", "3 personnes par m² (files d'attente)", U_M2, 3, 0, ""),
    ("O", "O2-decl", "O 2", "Déclaration contrôlée du chef d'établissement", U_P, 1, 0, ""),
    ("O", "O2-usage", "O 2", "Conditions d'exploitation hôtelière d'usage", U_P, 1, 0, ""),
    ("O", "O2-salle", "O 2", "Salle à l'usage exclusif des clients : effectif non cumulé", U_P, 1, 0, "noncumul"),
    ("P", "P2", "P 2", "4 personnes pour 3 m² (estrades et aménagements fixes déduits)", U_M2, 4 / 3, 0, ""),
    ("P", "P2-bil", "P 2", "Billard : 4 personnes par billard", "billards", 4, 0, ""),
    ("R", "R2", "R 2", "Déclaration contrôlée du maître d'ouvrage ou du chef d'établissement", U_P, 1, 0, ""),
    ("S", "S2", "S 2", "Déclaration du maître d'ouvrage ou du chef d'établissement", U_P, 1, 0, ""),
    ("T", "T2a", "T 2 a)", "1 personne par m² (expositions, foires, salons temporaires)", U_M2, 1, 0, ""),
    ("T", "T2b", "T 2 b)", "1 personne pour 9 m² (expositions permanentes)", U_M2, 1 / 9, 0, ""),
    ("U", "U2-lits", "U 2 § 1", "1 personne par lit + 1 visiteur par lit ; personnel : 1 pour 3 lits", "lits", 2, 1 / 3, ""),
    ("U", "U2-lits2", "U 2 § 1", "1 personne par lit + 1 visiteur pour 2 lits (U 1 § 1 a, 2e tiret, et b) ; personnel : 1 pour 3 lits", "lits", 1.5, 1 / 3, ""),
    ("U", "U2-cons", "U 2 § 1", "8 personnes, personnel compris, par poste de consultation ou d'exploration externe", "postes", 8, 0, ""),
    ("U", "U2-decl", "U 2 § 2", "Locaux de la section XIV : déclaration du chef d'établissement", U_P, 1, 0, ""),
    ("U", "U2-autres", "U 2 § 3", "Autres salles : selon leur type d'exploitation (déclaration)", U_P, 1, 0, ""),
    ("V", "V2-s", "V 2 a)", "1 personne par siège", U_PL, 1, 0, ""),
    ("V", "V2-b", "V 2 a)", "1 personne par 0,50 m de banc", U_BANC, 2, 0, ""),
    ("V", "V2-d", "V 2 b)", "2 personnes par m² de surface réservée aux fidèles", U_M2, 2, 0, ""),
    ("W", "W2-decl", "W 2", "Déclaration du maître d'ouvrage", U_P, 1, 0, ""),
    ("W", "W2-a", "W 2 a)", "1 personne pour 10 m² de locaux aménagés pour le public", U_M2, 0.1, 0, ""),
    ("W", "W2-b", "W 2 b)", "1 personne pour 100 m² de surface de plancher", U_M2, 0.01, 0, ""),
    ("X", "X2-decl", "X 2 § 1", "Déclaration du maître d'ouvrage", U_P, 1, 0, ""),
    ("X", "X2-a4", "X 2 § 1 a)", "1 personne pour 4 m² d'aire d'activité sportive", U_M2, 0.25, 0, ""),
    ("X", "X2-a8", "X 2 § 1 a)", "1 personne pour 8 m² d'aire d'activité sportive (+ spectateurs)", U_M2, 0.125, 0, ""),
    ("X", "X2-ten", "X 2 § 1 a)", "Tennis : 25 personnes par court", "courts", 25, 0, ""),
    ("X", "X2-b1", "X 2 § 1 b)", "Patinoire : 2 personnes pour 3 m² de plan de patinage", U_M2, 2 / 3, 0, ""),
    ("X", "X2-b2", "X 2 § 1 b)", "Patinoire : 1 personne pour 10 m² de plan de patinage (+ spectateurs)", U_M2, 0.1, 0, ""),
    ("X", "X2-c", "X 2 § 1 c)", "Salle polyvalente à dominante sportive : 1 personne par m² (+ spectateurs)", U_M2, 1, 0, ""),
    ("X", "X2-d1", "X 2 § 1 d)", "Piscine couverte : 1 personne par m² de plan d'eau", U_M2, 1, 0, ""),
    ("X", "X2-d2", "X 2 § 1 d)", "Piscine couverte : 1 personne pour 5 m² de plan d'eau (+ spectateurs)", U_M2, 0.2, 0, ""),
    ("X", "X2-e1", "X 2 § 1 e)", "Piscine transformable découverte : 3 personnes pour 2 m² de plan d'eau", U_M2, 1.5, 0, ""),
    ("X", "X2-e2", "X 2 § 1 e)", "Piscine transformable découverte : 1 personne pour 5 m² (+ spectateurs)", U_M2, 0.2, 0, ""),
    ("X", "X2-sp1", "X 2 § 2", "Spectateurs : 1 personne par siège ou strapontin", U_PL, 1, 0, ""),
    ("X", "X2-sp2", "X 2 § 2", "Spectateurs : 1 personne par 0,50 m de banc", U_BANC, 2, 0, ""),
    ("X", "X2-sp3", "X 2 § 2", "Spectateurs : 5 personnes par mètre linéaire de promenoir", U_ML, 5, 0, ""),
    ("Y", "Y2", "Y 2 § 1", "1 personne pour 5 m² de salles accessibles au public", U_M2, 0.2, 0, ""),
    ("PA", "PA2-decl", "PA 2 § 1", "Déclaration du maître d'ouvrage", U_P, 1, 0, ""),
    ("PA", "PA2-a", "PA 2 § 1 a)", "1 personne pour 10 m² d'aire d'activité sportive", U_M2, 0.1, 0, ""),
    ("PA", "PA2-ten", "PA 2 § 1 a)", "Tennis : 25 personnes par court", "courts", 25, 0, ""),
    ("PA", "PA2-b", "PA 2 § 1 b)", "Piste de patinage : 2 personnes pour 3 m²", U_M2, 2 / 3, 0, ""),
    ("PA", "PA2-c", "PA 2 § 1 c)", "Bassin de natation : 3 personnes pour 2 m² de plan d'eau", U_M2, 1.5, 0, ""),
    ("PA", "PA2-s1", "PA 2 § 2", "Spectateurs : 1 personne par siège", U_PL, 1, 0, ""),
    ("PA", "PA2-s2", "PA 2 § 2", "Spectateurs : 1 personne par 0,50 m de banc ou de gradin", U_BANC, 2, 0, ""),
    ("PA", "PA2-s3", "PA 2 § 2", "Spectateurs debout : 3 personnes par m²", U_M2, 3, 0, ""),
    ("PA", "PA2-s4", "PA 2 § 2", "Spectateurs debout : 5 personnes par mètre linéaire", U_ML, 5, 0, ""),
    ("CTS", "CTS2", "CTS 2", "Selon le mode de calcul du type d'activité (livre II)", U_P, 1, 0, ""),
    ("SG", "SG2", "SG 2", "Selon le type d'activité, 1 personne par m² au plus", U_P, 1, 0, ""),
    ("OA", "OA2", "OA 2", "Chambres : conditions d'exploitation hôtelière d'usage", U_P, 1, 0, ""),
    ("REF", "REF4", "REF 4", "Déclaration contrôlée du maître d'ouvrage, de l'exploitant ou du propriétaire", U_P, 1, 0, ""),
    ("PS", "PS-decl", "GN 1 § 2 b)", "Déclaration (pas de règle de calcul propre au type PS)", U_P, 1, 0, ""),
    ("GA", "GA2-1", "GA 2 (2.2.1.1)", "Public stationnant : 1 personne par m²", U_M2, 1, 0, ""),
    ("GA", "GA2-2", "GA 2 (2.2.1.2)", "Stationne et transite, partie aérienne : 1 personne pour 2 m²", U_M2, 0.5, 0, ""),
    ("GA", "GA2-3", "GA 2 (2.2.2.1)", "Comptoir : 1 personne par mètre linéaire", U_ML, 1, 0, ""),
    ("GA", "GA2-4", "GA 2 (2.2.2.2)", "Magasin : 2 personnes par m² sur le tiers de la surface", U_M2, 2 / 3, 0, ""),
    ("GA", "GA2-d", "GA 2", "Effectif déclaré par le pétitionnaire", U_P, 1, 0, ""),
]

# Variantes de seuils (lignes du tableau PE 2) : index de la ligne par défaut et
# lignes utilisées pour la vérification (résidents / ensemble)
VARIANTES = {
    "J": [("Personnes âgées", [0, 1]), ("Personnes handicapées", [2, 3])],
    "L": [("Auditions, conférences, réunions, multimédia…", [0]), ("Spectacles, projections, cabarets", [1])],
    "R": [("Écoles maternelles, crèches, haltes-garderies", [0]), ("Autres établissements", [1]), ("Avec locaux réservés au sommeil", [2])],
    "U": [("Sans hébergement", [0]), ("Avec hébergement", [1])],
}
