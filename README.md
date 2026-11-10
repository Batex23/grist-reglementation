# Réglementation incendie dans Grist

Base de la réglementation sécurité incendie **ERP, IGH, habitation et Code du travail**, à jour chaque jour à partir des textes officiels de Légifrance, consultable dans Grist avec :

- une **lecture continue** : on clique sur un chapitre, tous ses articles s'affichent à la suite ;
- des **références vivantes** : survoler « CO 15 » ou « R. 4227-28 » dans un texte affiche l'article cité, sans ouvrir de lien ; on peut l'épingler à côté pour comparer ;
- une **recherche par mots-clés** instantanée (synonymes métier inclus : désenfumage ↔ évacuation des fumées, UP ↔ unité de passage…) et un mode **Question** qui comprend « ERP de type L », « 5e catégorie », etc. ;
- une **recherche sémantique sans clé API** (modèle exécuté dans le navigateur), et la possibilité de brancher plus tard un LLM (Albert, Mistral…) ;
- des **commentaires illustrés** (photos, schémas) sur chaque article ;
- une **veille** : chaque modification publiée au JO est détectée avec le texte avant / après, les modifications à venir sont signalées (ex. arrêté « bois » applicable au 1er juin 2027), et les parutions annoncées par SiteSecurite.com sont ajoutées.

## Pourquoi Légifrance plutôt que SiteSecurite.com

SiteSecurite.com est un service sur abonnement dont les conditions limitent l'accès à un usage personnel : son contenu ne peut pas être recopié dans un document partagé. Les textes officiels, eux, sont libres de réutilisation. Ils sont pris dans la base **LEGI** publiée chaque jour par la DILA en open data (aucune clé nécessaire). SiteSecurite reste accessible depuis chaque article (bouton « SiteSecurite ↗ ») pour ses commentaires et sa jurisprudence, et ses annonces de parution alimentent la veille.

## Comment ça marche

```
Journal officiel ──► base LEGI (DILA, open data) ──► GitHub, chaque matin :
                                                    textes à jour + widget publiés sur GitHub Pages
                                                                    │
GPREV (Grist) ◄── le widget compare et met à jour les tables REG_ ◄─┘
                  avec les droits de l'agent qui ouvre la page
```

**Aucune clé API, aucun compte de service.** GitHub ne touche jamais à GPREV : il ne publie que des textes publics. C'est le widget, ouvert par un agent du service, qui met les tables `REG_` à jour. La première personne qui ouvre la page dans la journée déclenche la mise à jour (quelques secondes, en arrière-plan), et la veille se remplit à ce moment-là.

## Ce que contient ce dossier

| Élément | Rôle |
|---|---|
| `widget/` | Le widget Grist (navigation, recherche, commentaires, veille, mise à jour) |
| `widget/data/` | Les textes à jour au 10/11/2026 (base LEGI du 09/11/2026), régénérés chaque matin |
| `data/cibles.json` | Les textes suivis (identifiants Légifrance) |
| `sync/` | Les scripts qui préparent les textes (Python + Node) |
| `.github/workflows/veille.yml` | La préparation automatique quotidienne |
| `tests/` | Tests de la synchronisation et du widget dans un faux Grist |

## Installation dans GPREV (environ 15 minutes)

La réglementation s'installe directement dans GPREV, pour apparaître dans la barre de gauche comme les autres applications et rattacher les commentaires aux agents déjà invités. Toutes ses tables commencent par `REG_` : aucune table existante n'est modifiée.

| Table | Contenu |
|---|---|
| `REG_Articles` | Les textes (mis à jour par le widget ; seuls les mots-clés se modifient à la main) |
| `REG_Commentaires` | Commentaires et images ; l'auteur et son e-mail sont remplis automatiquement |
| `REG_Veille` | Journal de veille (statut, analyse d'impact) |
| `REG_Synonymes` | Synonymes métier utilisés par la recherche, modifiables |
| `REG_Parametres` | Version des textes chargés (usage interne) |

### 1. Publier le widget sur GitHub

1. Créez un dépôt GitHub (public ou privé selon votre offre GitHub : Pages sur un dépôt privé demande un compte payant) et envoyez-y le contenu de ce dossier.
2. *Settings → Pages* : source **GitHub Actions**.
3. Onglet *Actions* → « Veille réglementaire incendie » → **Run workflow**.
   La première exécution télécharge la base Légifrance (environ 15 minutes), puis publie le widget. Son adresse s'affiche à la fin : `https://<compte>.github.io/<dépôt>/`.
   Ensuite, elle tourne seule chaque matin. Aucun secret à configurer.

### 2. Ajouter la page dans GPREV

1. Dans GPREV : **Ajouter** → **Ajouter une page**.
2. « Choisir la vue » : **Personnalisée** ; « Choisir les données source » : n'importe quelle table pour l'instant (par exemple *Commentaire*) → *Ajouter une page*.
3. Panneau de droite : *URL personnalisée* = l'adresse du widget ; *Accès* = **Accès complet au document**.
4. Le widget propose **Installer et charger les textes** : cliquez (il faut être propriétaire ou éditeur de GPREV). Les 5 tables `REG_` sont créées et les textes chargés en une à deux minutes.
5. Dans le panneau de droite, changez la table source du widget pour **REG_Commentaires** (les nouveaux commentaires s'afficheront ainsi immédiatement chez tous).
6. Renommez la page (par exemple « 🔥 Réglementation incendie ») et agrandissez le widget en pleine page.

Le widget ne lit que les tables `REG_` ; l'accès complet est nécessaire pour enregistrer commentaires, images et mises à jour.

### 3. Vérifier les droits des agents

- Pour **consulter et commenter** : lire `REG_Articles`, `REG_Veille`, `REG_Synonymes`, et ajouter des lignes dans `REG_Commentaires`.
- Pour que la **mise à jour quotidienne** se fasse, au moins un agent qui ouvre la page doit pouvoir modifier `REG_Articles`, `REG_Veille` et `REG_Parametres` (un éditeur suffit). Un agent en lecture seule consulte normalement ; la mise à jour attend simplement le passage d'un éditeur.

Si GPREV n'a pas de règles d'accès particulières, il n'y a rien à faire : les éditeurs ont déjà ces droits.

Pour relier un commentaire à la fiche de l'agent, ajoutez dans `REG_Commentaires` une colonne de référence vers votre table du personnel, avec une formule du type `Personnel_du_GPREV.lookupOne(Email=$Auteur_email)` (adaptez le nom de la table et de la colonne e-mail).

## Utilisation

- **/** ou **Ctrl+K** : rechercher. Un numéro (« CO 15 », « R. 4227-28 ») ouvre directement l'article.
- **Mots-clés / Question** : le mode Question classe les articles selon ce qui est compris de la question (réglementation, type d'ERP, catégorie, notions) et montre les deux phrases les plus pertinentes de chaque article.
- **j / k** : article suivant / précédent pendant la lecture.
- Cliquer sur la plaque d'un article ouvre ses commentaires, son historique (textes modificatifs) et la comparaison avec la version à venir.
- Les images se déposent par glisser-déposer ou copier-coller dans le formulaire de commentaire ; elles sont redimensionnées avant envoi.
- La page d'accueil indique la date de la base Légifrance chargée ; une petite notification signale les mises à jour appliquées.
- **Réglages** (roue dentée) : activer la recherche sémantique (téléchargement unique d'environ 120 Mo, puis en cache), brancher un LLM compatible OpenAI si vous en obtenez l'accès plus tard (la clé reste dans votre navigateur).

## Ce qui est suivi

| Domaine | Texte |
|---|---|
| ERP | Arrêté du 25 juin 1980 (dispositions générales, particulières, 5e catégorie, établissements spéciaux) |
| IGH | Arrêté du 30 décembre 2011 |
| Habitation | Arrêté du 31 janvier 1986 |
| Code du travail | Articles R. 4216-1 et suivants (maître d'ouvrage), R. 4227-1 et suivants (employeur), arrêté du 5 août 1992 |
| CCH | Articles L. 141-1 à R. 146 (dispositions incendie du Code de la construction) |

Pour suivre un autre texte (une instruction technique, par exemple), ajoutez son identifiant à `data/cibles.json` et videz le cache GitHub (*Actions → Caches*) : il sera extrait à la prochaine exécution, puis chargé dans GPREV par le widget.

## Lancer à la main (sans GitHub)

Sur un poste avec Python 3 et Node 22, puis hébergez le dossier `widget/` sur n'importe quel serveur web en HTTPS :

```bash
pip install lxml
npm install --prefix sync @huggingface/transformers@3
python -I sync/legi_scan.py bootstrap cache/legi data/cibles.json   # une seule fois (1,2 Go téléchargés)
python -I sync/grist_sync.py extraire                                # applique les parutions du JO
(cd sync && node embed.mjs ../data/reglementation.json ../data/vecteurs.json)
python -I sync/grist_sync.py publier                                 # écrit widget/data/
```

Tests : `python -I tests/test_sync.py`, puis, en servant la racine du projet sur le port 8765, `python tests/test_widget.py`.

## Limites à connaître

- La recherche « Question » sans LLM est une recherche documentaire : elle trouve et surligne les passages, elle ne rédige pas de réponse. Lisez toujours l'article complet.
- Les schémas et figures des textes ne sont pas repris : le lien Légifrance de chaque article permet de les voir.
- Les jours sans visite d'un éditeur, la mise à jour attend : les textes affichés restent ceux du dernier passage (la date est indiquée sur l'accueil).
- Les instructions techniques (IT 246, IT 247…), circulaires et réponses ministérielles ne sont pas incluses par défaut.
