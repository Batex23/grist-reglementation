# Planches illustrées

Planches isométriques dessinées pour le SDIS 33 d'après le texte en vigueur des articles (base Légifrance du widget).

- Moteur de dessin : `iso.py` ; une scène par fichier dans `scenes/` (métadonnées `META` + `dessiner()`).
- Rendu : `python3 illustrations/build.py [motif]` → `widget/illustrations/<id>.png` et `index.json` (lu par le widget).
- Aperçu d'une scène : `illustrations/apercu.sh <motif> <sortie.jpg>`.

Icônes (véhicules, personnages, feu, fumée, végétation) : © SDMIS — Service départemental-métropolitain
d'incendie et de secours du Rhône, 2023, licence CC BY-NC-SA 4.0
(https://creativecommons.org/licenses/by-nc-sa/4.0/deed.fr). Usage non commercial ; les planches qui les
intègrent sont diffusées sous la même licence, avec mention sur chaque image.
