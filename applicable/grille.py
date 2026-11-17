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
