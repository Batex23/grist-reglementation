"""Synchronisation de la base réglementaire sécurité incendie vers Grist.

Commandes
---------
  init        crée les tables dans le document Grist (à lancer une seule fois)
  charger     envoie reglementation.json dans la table Reglementation (sans créer de veille)
  extraire    applique les incréments quotidiens Légifrance (DILA) et régénère data/reglementation.json
              (pas besoin de Grist) ; ensuite « charger --veille » pousse les différences et la veille
  actus       ajoute à la veille les dernières parutions annoncées par SiteSecurite.com
  publier     écrit widget/data/ : le widget met lui-même Grist à jour (mode recommandé, sans clé API)

Les commandes init, charger et actus écrivent directement dans Grist avec une clé API ;
elles ne servent que si vous disposez d'un compte dédié au script.

Variables d'environnement
-------------------------
  GRIST_SERVER   ex. https://grist.numerique.gouv.fr
  GRIST_DOC_ID   identifiant du document (dans l'URL, après /doc/ ou le nom court)
  GRIST_API_KEY  clé API personnelle (Profil > Clé API)
"""
import argparse
import datetime as dt
import html
import io
import json
import os
import re
import shutil
import sys
import tarfile
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

DILA = "https://echanges.dila.gouv.fr/OPENDATA/LEGI/"
UA = {"User-Agent": "grist-veille-incendie/1.0"}

# --------------------------------------------------------------------------- schéma Grist

CHOIX_DOMAINE = ["ERP", "IGH", "HAB", "CDT", "CCH"]


def choix(*vals):
    return json.dumps({"choices": list(vals)})


SCHEMA = [
    ("REG_Articles", [
        ("Identifiant", "Text", "Identifiant Légifrance"),
        ("Parent", "Text", "Parent (identifiant)"),
        ("Type", "Choice", "Type", choix("Texte", "Section", "Article")),
        ("Domaine", "Choice", "Domaine", choix(*CHOIX_DOMAINE)),
        ("Numero", "Text", "N° d'article"),
        ("Titre", "Text", "Titre"),
        ("Chemin", "Text", "Emplacement"),
        ("Niveau", "Int", "Niveau"),
        ("Ordre", "Int", "Ordre"),
        ("Texte", "Text", "Texte en vigueur"),
        ("Texte_HTML", "Text", "Texte (mise en forme)"),
        ("Nota", "Text", "Nota"),
        ("Etat", "Choice", "État", choix("VIGUEUR", "VIGUEUR_DIFF", "MODIFIE", "A_VENIR", "ABROGE")),
        ("En_vigueur_depuis", "Date", "En vigueur depuis"),
        ("Fin_de_vigueur", "Date", "Fin de vigueur"),
        ("Historique", "Text", "Modifié par (JSON)"),
        ("Version_a_venir", "Text", "Version à venir"),
        ("Version_a_venir_HTML", "Text", "Version à venir (mise en forme)"),
        ("Date_a_venir", "Date", "Date d'entrée en vigueur à venir"),
        ("A_venir_par", "Text", "À venir par (JSON)"),
        ("Texte_officiel", "Text", "Texte officiel (LEGITEXT)"),
        ("Derniere_modif_texte", "Date", "Dernière modification du texte"),
        ("Lien_Legifrance", "Text", "Lien Légifrance"),
        ("Mots_cles", "ChoiceList", "Mots-clés (libres)", choix()),
        ("Vecteur", "Text", "Vecteur sémantique"),
        ("Mis_a_jour", "Date", "Synchronisé le"),
    ]),
    ("REG_Commentaires", [
        ("Article", "Ref:REG_Articles", "Article"),
        ("Type", "Choice", "Type", choix("Interprétation", "Retour terrain", "Photo / schéma", "Question", "Jurisprudence", "Doctrine / réponse ministérielle")),
        ("Texte", "Text", "Commentaire"),
        ("Images", "Attachments", "Images"),
        ("Auteur", "Text", "Auteur", None, "user.Name"),
        ("Auteur_email", "Text", "E-mail de l'auteur", None, "user.Email"),
        ("Cree_le", "DateTime:Europe/Paris", "Créé le", None, "NOW()"),
    ]),
    ("REG_Veille", [
        ("Date", "Date", "Date"),
        ("Domaine", "Choice", "Domaine", choix(*CHOIX_DOMAINE, "Divers")),
        ("Nature", "Choice", "Nature", choix("Modification", "Nouvel article", "Abrogation", "Modification à venir", "Parution SiteSecurite")),
        ("Titre", "Text", "Titre"),
        ("Article", "Ref:REG_Articles", "Article"),
        ("Ancien_texte", "Text", "Ancien texte"),
        ("Nouveau_texte", "Text", "Nouveau texte"),
        ("Source", "Text", "Texte modificatif / source"),
        ("Lien", "Text", "Lien"),
        ("Date_effet", "Date", "Date d'effet"),
        ("Statut", "Choice", "Statut", choix("À lire", "Lu", "Impact analysé")),
        ("Analyse", "Text", "Analyse / impact"),
        ("Cle", "Text", "Clé technique"),
    ]),
    ("REG_Synonymes", [
        ("Terme", "Text", "Terme"),
        ("Equivalents", "Text", "Équivalents (séparés par des virgules)"),
    ]),
    ("REG_Parametres", [
        ("Cle", "Text", "Paramètre"),
        ("Valeur", "Text", "Valeur"),
    ]),
]


# --------------------------------------------------------------------------- client Grist

class Grist:
    def __init__(self):
        self.server = os.environ["GRIST_SERVER"].rstrip("/")
        self.doc = os.environ["GRIST_DOC_ID"]
        self.key = os.environ["GRIST_API_KEY"]

    def call(self, method, path, body=None):
        url = f"{self.server}/api/docs/{self.doc}{path}"
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method, headers={
            "Authorization": f"Bearer {self.key}", "Content-Type": "application/json", **UA})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                raw = r.read()
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as e:
            raise SystemExit(f"Erreur Grist {e.code} sur {method} {path} : {e.read().decode()[:500]}")

    def tables(self):
        return {t["id"] for t in self.call("GET", "/tables")["tables"]}

    def records(self, table):
        return self.call("GET", f"/tables/{table}/records")["records"]

    def add(self, table, rows):
        ids = []
        for i in range(0, len(rows), 200):
            r = self.call("POST", f"/tables/{table}/records", {"records": [{"fields": f} for f in rows[i:i + 200]]})
            ids += [x["id"] for x in r["records"]]
        return ids

    def update(self, table, rows):
        for i in range(0, len(rows), 200):
            self.call("PATCH", f"/tables/{table}/records", {"records": rows[i:i + 200]})

    def upsert(self, table, key, rows):
        for i in range(0, len(rows), 200):
            self.call("PUT", f"/tables/{table}/records?noparse=true", {"records": [
                {"require": {key: f[key]}, "fields": f} for f in rows[i:i + 200]]})

    def param(self, cle, valeur=None):
        rows = [r for r in self.records("REG_Parametres") if r["fields"].get("Cle") == cle]
        if valeur is None:
            return rows[0]["fields"].get("Valeur") if rows else None
        if rows:
            self.update("REG_Parametres", [{"id": rows[0]["id"], "fields": {"Valeur": valeur}}])
        else:
            self.add("REG_Parametres", [{"Cle": cle, "Valeur": valeur}])


# --------------------------------------------------------------------------- commandes

def cmd_init(g, _args):
    existantes = g.tables()
    for tid, cols in SCHEMA:
        defs = []
        for c in cols:
            cid, typ, label = c[0], c[1], c[2]
            f = {"label": label, "type": typ}
            if len(c) > 3 and c[3]:
                f["widgetOptions"] = c[3]
            if len(c) > 4 and c[4]:
                # formule « déclencheur » : calculée à la création de la ligne uniquement
                f.update({"formula": c[4], "isFormula": False, "recalcWhen": 0, "recalcDeps": None})
            defs.append({"id": cid, "fields": f})
        if tid in existantes:
            have = {c["id"] for c in g.call("GET", f"/tables/{tid}/columns")["columns"]}
            manque = [d for d in defs if d["id"] not in have]
            if manque:
                g.call("POST", f"/tables/{tid}/columns", {"columns": manque})
            print(f"{tid} : déjà présente ({len(manque)} colonne(s) ajoutée(s))")
        else:
            g.call("POST", "/tables", {"tables": [{"id": tid, "columns": defs}]})
            print(f"{tid} : créée")
    # synonymes de départ
    if not g.records("REG_Synonymes"):
        syn = json.load(open(os.path.join(HERE, "synonymes.json"), encoding="utf-8"))
        g.add("REG_Synonymes", [{"Terme": k, "Equivalents": v} for k, v in syn.items()])
        print(f"Synonymes : {len(syn)} entrées ajoutées")


CHAMPS_SYNC = ["Identifiant", "Parent", "Type", "Domaine", "Numero", "Titre", "Chemin", "Niveau", "Ordre",
               "Texte", "Texte_HTML", "Nota", "Etat", "En_vigueur_depuis", "Fin_de_vigueur", "Historique",
               "Version_a_venir", "Version_a_venir_HTML", "Date_a_venir", "A_venir_par", "Texte_officiel",
               "Derniere_modif_texte", "Lien_Legifrance", "Vecteur"]


def normalise(n, today):
    f = {k: n.get(k, "") for k in CHAMPS_SYNC}
    for k in ("Niveau", "Ordre"):
        f[k] = int(n.get(k) or 0)
    for k in ("En_vigueur_depuis", "Fin_de_vigueur", "Date_a_venir", "Derniere_modif_texte"):
        f[k] = n.get(k) or None
    f["Mis_a_jour"] = today
    return f


def jour(s):
    return s if s else None


def applique(g, nouveaux, today, avec_veille):
    """Compare l'état Grist et la nouvelle extraction ; met à jour et journalise la veille."""
    exist = {r["fields"]["Identifiant"]: r for r in g.records("REG_Articles") if r["fields"].get("Identifiant")}
    par_num = {}
    for r in exist.values():
        f = r["fields"]
        if f.get("Type") == "Article" and f.get("Etat") != "ABROGE":
            par_num[(f.get("Texte_officiel"), f.get("Numero"))] = r
    nouveaux_ids = {n["Identifiant"] for n in nouveaux}
    veille, maj, ajout = [], [], []
    deja = {r["fields"].get("Cle") for r in g.records("REG_Veille")}

    def note(**kw):
        if kw["Cle"] not in deja:
            deja.add(kw["Cle"])
            kw.setdefault("Statut", "À lire")
            kw.setdefault("Date", today)
            veille.append(kw)

    for n in nouveaux:
        f = normalise(n, today)
        r = exist.get(n["Identifiant"])
        if r is None and n["Type"] == "Article":
            # nouvelle version d'un article existant (nouvel identifiant LEGIARTI) ?
            ancien = par_num.get((n.get("Texte_officiel"), n.get("Numero")))
            if ancien and ancien["fields"]["Identifiant"] not in nouveaux_ids:
                f["Mots_cles"] = ancien["fields"].get("Mots_cles")
                maj.append({"id": ancien["id"], "fields": f})   # même ligne → commentaires conservés
                exist[n["Identifiant"]] = ancien
                hist = json.loads(n.get("Historique") or "[]")
                src = hist[-1]["texte"] if hist else ""
                if avec_veille and (ancien["fields"].get("Texte") or "") != (n.get("Texte") or ""):
                    note(Domaine=n["Domaine"], Nature="Modification", Titre=f"Article {n['Numero']} modifié",
                         Article=ancien["id"], Ancien_texte=ancien["fields"].get("Texte"), Nouveau_texte=n.get("Texte"),
                         Source=src, Lien=n.get("Lien_Legifrance"), Date_effet=jour(n.get("En_vigueur_depuis")),
                         Cle=f"modif:{n['Identifiant']}")
                continue
        if r is None:
            ajout.append(f)
            continue
        old = r["fields"]
        changed = any((old.get(k) or "") != (f.get(k) or "") for k in ("Texte", "Etat", "Version_a_venir", "Titre", "Chemin", "Ordre", "Parent", "Vecteur"))
        if changed:
            maj.append({"id": r["id"], "fields": f})
        if avec_veille and n["Type"] == "Article":
            if (old.get("Texte") or "") != (n.get("Texte") or "") and old.get("Texte"):
                note(Domaine=n["Domaine"], Nature="Modification", Titre=f"Article {n['Numero']} modifié",
                     Article=r["id"], Ancien_texte=old.get("Texte"), Nouveau_texte=n.get("Texte"),
                     Lien=n.get("Lien_Legifrance"), Date_effet=jour(n.get("En_vigueur_depuis")),
                     Cle=f"modif:{n['Identifiant']}:{n.get('En_vigueur_depuis')}")

    # articles disparus de la version en vigueur → abrogés
    for ident, r in exist.items():
        f = r["fields"]
        if ident in nouveaux_ids or f.get("Type") != "Article" or f.get("Etat") == "ABROGE":
            continue
        if any(m["id"] == r["id"] for m in maj):
            continue
        maj.append({"id": r["id"], "fields": {"Etat": "ABROGE", "Fin_de_vigueur": today, "Mis_a_jour": today}})
        if avec_veille:
            note(Domaine=f.get("Domaine"), Nature="Abrogation", Titre=f"Article {f.get('Numero')} abrogé",
                 Article=r["id"], Ancien_texte=f.get("Texte"), Lien=f.get("Lien_Legifrance"), Cle=f"abro:{ident}")

    if maj:
        g.update("REG_Articles", maj)
    ids = g.add("REG_Articles", ajout) if ajout else []
    rows = {r["fields"]["Identifiant"]: r["id"] for r in exist.values()}
    rows.update({f["Identifiant"]: rid for f, rid in zip(ajout, ids)})
    # modifications programmées (versions à venir) : toujours signalées, une seule fois par date
    for n in nouveaux:
        if n["Type"] == "Article" and n.get("Version_a_venir"):
            hist = json.loads(n.get("A_venir_par") or "[]")
            nature = "Nouvel article" if n.get("Etat") == "A_VENIR" else "Modification à venir"
            note(Domaine=n["Domaine"], Nature="Modification à venir",
                 Titre=f"{'Nouvel article' if nature == 'Nouvel article' else 'Article'} {n['Numero']} : "
                       f"{'entre en vigueur' if nature == 'Nouvel article' else 'nouvelle rédaction'} le {dt.date.fromisoformat(n['Date_a_venir']).strftime('%d/%m/%Y')}",
                 Article=rows.get(n["Identifiant"]), Ancien_texte=n.get("Texte"), Nouveau_texte=n.get("Version_a_venir"),
                 Source=hist[-1]["texte"] if hist else "", Lien=n.get("Lien_Legifrance"),
                 Date_effet=jour(n.get("Date_a_venir")), Cle=f"avenir:{n['Numero']}:{n['Texte_officiel']}:{n.get('Date_a_venir')}")
    if avec_veille:
        for f, rid in zip(ajout, ids):
            if f["Type"] == "Article" and f.get("Etat") != "A_VENIR":
                note(Domaine=f["Domaine"], Nature="Nouvel article", Titre=f"Nouvel article {f['Numero']}",
                     Article=rid, Nouveau_texte=f.get("Texte") or f.get("Version_a_venir"), Lien=f.get("Lien_Legifrance"),
                     Date_effet=jour(f.get("En_vigueur_depuis") or f.get("Date_a_venir")), Cle=f"nouv:{f['Identifiant']}")
    if veille:
        g.add("REG_Veille", veille)
    print(f"Reglementation : {len(ajout)} ajout(s), {len(maj)} mise(s) à jour ; Veille : {len(veille)} entrée(s)")


def cmd_charger(g, args):
    data = json.load(open(args.fichier, encoding="utf-8"))
    applique(g, data, dt.date.today().isoformat(), avec_veille=args.veille)


# --------------------------------------------------------------------------- incréments DILA

def liste_increments():
    with urllib.request.urlopen(urllib.request.Request(DILA, headers=UA), timeout=60) as r:
        page = r.read().decode("utf-8", "replace")
    return sorted(set(re.findall(r'href="(LEGI_(\d{8}-\d{6})\.tar\.gz)"', page)), key=lambda x: x[1])


def applique_increment(url, cache_dir, dossiers):
    """Extrait dans le cache les fichiers d'un incrément qui concernent nos textes."""
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=600) as r:
        buf = io.BytesIO(r.read())
    n = 0
    with tarfile.open(fileobj=buf, mode="r:gz") as tar:
        for m in tar:
            name = m.name
            if name.endswith("liste_suppression_legi.dat"):
                for line in tar.extractfile(m).read().decode().splitlines():
                    line = line.strip()
                    if any(d in line for d in dossiers):
                        p = os.path.join(cache_dir, re.sub(r"^(?:.*?/)?legi/", "", line, count=1) + ".xml")
                        if os.path.exists(p):
                            os.remove(p)
                continue
            if not m.isfile() or "legi/" not in name:
                continue
            rel = re.sub(r"^(?:.*?/)?legi/", "", name, count=1)
            if not any(rel.startswith(d + "/") for d in dossiers):
                continue
            dest = os.path.normpath(os.path.join(cache_dir, rel))
            if not dest.startswith(os.path.abspath(cache_dir)):
                continue
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "wb") as out:
                shutil.copyfileobj(tar.extractfile(m), out)
            n += 1
    return n


def cmd_extraire(args):
    """Applique les incréments DILA au cache local puis reconstruit data/reglementation.json."""
    import legi_build
    cibles = json.load(open(args.cibles, encoding="utf-8"))
    dossiers = [c["dir"] for c in cibles.values()]
    etat_path = os.path.join(args.cache, "..", "dernier_increment.txt")
    dernier = open(etat_path).read().strip() if os.path.exists(etat_path) else args.depuis
    a_traiter = [(f, d) for f, d in liste_increments() if d > dernier]
    if not a_traiter:
        print(f"Aucun nouvel incrément depuis {dernier}.")
    for f, d in a_traiter:
        n = applique_increment(DILA + f, args.cache, dossiers)
        print(f"incrément {d} : {n} fichier(s) concernant nos textes")
        open(etat_path, "w").write(d)
    noeuds = legi_build.build(args.cache, cibles, dt.date.today().isoformat())
    if os.path.exists(args.vecteurs):
        vec = json.load(open(args.vecteurs, encoding="utf-8"))
        for n in noeuds:
            v = vec.get(n["Identifiant"])
            if v and v.get("h") == legi_build.empreinte(n):
                n["Vecteur"] = v["v"]
    json.dump(noeuds, open(args.sortie, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"{len(noeuds)} nœuds écrits dans {args.sortie}")


# --------------------------------------------------------------------------- actualités SiteSecurite

CAT = {"erp": "ERP", "igh": "IGH", "hab": "HAB", "ert": "CDT", "bup": "CDT"}


def nettoie(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


MOIS = {m: i for i, m in enumerate(["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
                                      "septembre", "octobre", "novembre", "décembre"], 1)}


def date_fr(s):
    """« Parution du 4 décembre 2022 » → 2022-12-04 (None si illisible)."""
    m = re.search(r"(\d{1,2})(?:\s*er)?\s+([a-zéû]+)\s+(\d{4})", (s or "").lower())
    if m and m.group(2) in MOIS:
        return dt.date(int(m.group(3)), MOIS[m.group(2)], int(m.group(1))).isoformat()
    return None


def lire_actus():
    """Dernières parutions annoncées par SiteSecurite (titre, date, lien), sans doublon."""
    vus, lignes = set(), []
    for cat in ("erp", "igh", "hab", "ert"):
        url = f"https://sitesecurite.com/news/api/?category={cat}"
        for essai in range(3):
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                    items = json.loads(r.read().decode("utf-8", "replace"))
                break
            except (urllib.error.URLError, ConnectionError):
                if essai == 2:
                    raise
                import time
                time.sleep(5 * (essai + 1))
        for it in items:
            cle = f"sitesecurite:{it.get('ID')}"
            if cle in vus:
                continue
            vus.add(cle)
            texte = re.sub(r"\s*(Voir le texte|Voir la réponse.*|Texte modifié\s*:.*)$", "", nettoie(it.get("text")))
            liens = re.findall(r'href="([^"]+)"', it.get("text") or "")
            titre = nettoie(it.get("title")) or texte[:120]
            lignes.append({
                "Date": date_fr(nettoie(it.get("date"))) or dt.date.today().isoformat(), "Domaine": CAT.get(cat, "Divers"),
                "Nature": "Parution SiteSecurite", "Titre": titre,
                "Source": " — ".join(x for x in [nettoie(it.get("date")), (texte[:280] + "…") if len(texte) > 280 else texte] if x),
                "Lien": liens[0] if liens else "https://sitesecurite.com/news/actualites.php",
                "Cle": cle,
            })
    return lignes


def cmd_actus(g, _args):
    deja = {r["fields"].get("Cle") for r in g.records("REG_Veille")}
    lignes = [dict(x, Statut="À lire") for x in lire_actus() if x["Cle"] not in deja]
    if lignes:
        g.add("REG_Veille", lignes)
    print(f"Veille SiteSecurite : {len(lignes)} nouvelle(s) parution(s)")


def cmd_publier(args):
    """Écrit à côté du widget les données qu'il charge lui-même dans Grist (aucune clé API nécessaire)."""
    out = args.dossier
    os.makedirs(out, exist_ok=True)
    noeuds = json.load(open(args.fichier, encoding="utf-8"))
    json.dump(noeuds, open(os.path.join(out, "reglementation.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    try:
        actus = lire_actus()
    except Exception as e:  # SiteSecurite indisponible : on garde les parutions précédentes
        print(f"Parutions SiteSecurite indisponibles ({e})")
        prec = os.path.join(out, "actus.json")
        actus = json.load(open(prec, encoding="utf-8")) if os.path.exists(prec) else []
    json.dump(actus, open(os.path.join(out, "actus.json"), "w", encoding="utf-8"), ensure_ascii=False)
    shutil.copy(os.path.join(HERE, "synonymes.json"), os.path.join(out, "synonymes.json"))
    etat = os.path.join(HERE, "..", "cache", "dernier_increment.txt")
    inc = open(etat).read().strip() if os.path.exists(etat) else dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    import hashlib
    empreinte = hashlib.sha1(json.dumps(noeuds, sort_keys=True).encode() + json.dumps(actus, sort_keys=True).encode()).hexdigest()[:8]
    version = {"version": f"{inc}-{empreinte}", "base": f"{inc[:4]}-{inc[4:6]}-{inc[6:8]}",
               "genere": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
               "articles": sum(1 for n in noeuds if n["Type"] == "Article")}
    json.dump(version, open(os.path.join(out, "version.json"), "w", encoding="utf-8"), ensure_ascii=False)
    print(f"Publié dans {out} : {version}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init")
    c = sub.add_parser("charger")
    c.add_argument("fichier", nargs="?", default=os.path.join(HERE, "..", "data", "reglementation.json"))
    c.add_argument("--veille", action="store_true", help="journaliser les différences dans la veille")
    m = sub.add_parser("extraire")
    m.add_argument("--cibles", default=os.path.join(HERE, "..", "data", "cibles.json"))
    m.add_argument("--cache", default=os.path.join(HERE, "..", "cache", "legi"))
    m.add_argument("--depuis", default="20261109-999999", help="incrément de départ si jamais synchronisé")
    m.add_argument("--vecteurs", default=os.path.join(HERE, "..", "data", "vecteurs.json"))
    m.add_argument("--sortie", default=os.path.join(HERE, "..", "data", "reglementation.json"))
    sub.add_parser("actus")
    pb = sub.add_parser("publier")
    pb.add_argument("fichier", nargs="?", default=os.path.join(HERE, "..", "data", "reglementation.json"))
    pb.add_argument("--dossier", default=os.path.join(HERE, "..", "widget", "data"))
    args = p.parse_args()
    if args.cmd == "extraire":
        return cmd_extraire(args)
    if args.cmd == "publier":
        return cmd_publier(args)
    g = Grist()
    {"init": cmd_init, "charger": cmd_charger, "actus": cmd_actus}[args.cmd](g, args)


if __name__ == "__main__":
    main()
