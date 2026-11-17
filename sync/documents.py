"""Doctrine & guides : transforme les PDF du dossier documents/ en fiches consultables dans le widget.

Chaque PDF est découpé selon ses titres numérotés (« 2.1 DÉGAGEMENTS ET ISSUES », « 1. CONSTAT »),
à défaut selon ses intertitres, à défaut page par page. Les pages scannées sont lues par OCR (tesseract).
Les pages sont aussi rendues en images, pour garder schémas et tableaux.

Usage :
  python -I sync/documents.py fusionner data/reglementation.json [--images widget/documents]

  - retire de reglementation.json les fiches « DOC » précédentes et y ajoute celles des PDF actuels ;
  - avec --images : copie les PDF et écrit les images des pages pour la publication du widget.

Pour ajouter un document : déposer le PDF dans documents/ (et, si souhaité, une entrée dans
documents/catalogue.json : code, titre, catégorie, date d'édition, source).
Outils requis : pdftotext, pdftoppm (poppler-utils) ; tesseract + langue fra pour les scans.
"""
import datetime as dt
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DOSSIER = os.path.join(ROOT, "documents")
DOM = "DOC"

BULLETS = "•●▪■◦○➢➤►▶✓✔-–—*"
PUA = re.compile("[-]")  # puces des polices Symbol / Wingdings


# --------------------------------------------------------------------------- lecture du PDF

def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, **kw)


def nb_pages(pdf):
    out = run(["pdfinfo", pdf]).stdout.decode("utf-8", "replace")
    return int(re.search(r"Pages:\s+(\d+)", out).group(1))


def texte_page(pdf, i, tmp):
    """Texte d'une page (mise en page conservée) ; OCR si la page est une image."""
    t = run(["pdftotext", "-layout", "-enc", "UTF-8", "-f", str(i), "-l", str(i), pdf, "-"]).stdout.decode("utf-8", "replace")
    if len(re.sub(r"\s", "", t)) >= 40:
        return t, False
    if not shutil.which("tesseract"):
        return t, False
    base = os.path.join(tmp, f"ocr{i}")
    run(["pdftoppm", "-r", "300", "-gray", "-f", str(i), "-l", str(i), "-singlefile", pdf, base])
    run(["tesseract", base + ".pgm", base, "-l", "fra", "--psm", "4"])
    return open(base + ".txt", encoding="utf-8").read(), True


def lire(pdf):
    pages, ocr = [], 0
    with tempfile.TemporaryDirectory() as tmp:
        for i in range(1, nb_pages(pdf) + 1):
            t, o = texte_page(pdf, i, tmp)
            ocr += o
            pages.append(PUA.sub("•", t).replace("\f", ""))
    return pages, ocr


# --------------------------------------------------------------------------- nettoyage

def cle(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z]+", "", s)


def nettoie(pages):
    """Retire numéros de page et en-têtes / pieds répétés sur la plupart des pages."""
    from collections import Counter
    vus = Counter()
    for p in pages:
        for k in {cle(l) for l in p.splitlines() if 3 < len(cle(l)) < 120}:
            vus[k] += 1
    seuil = max(2, int(len(pages) * 0.6)) if len(pages) > 1 else 99
    repetes = {k for k, n in vus.items() if n >= seuil}
    out = []
    for p in pages:
        lignes = []
        for l in p.splitlines():
            s = l.strip()
            if re.fullmatch(r"#\s*\d+|\d+\s*/\s*\d+|page\s+\d+(\s*/\s*\d+)?|\d{1,3}", s, re.I):
                continue
            if cle(l) in repetes:
                continue
            lignes.append(l.rstrip())
        out.append(lignes)
    return out


def est_sommaire(lignes):
    return sum(1 for l in lignes if re.search(r"\S.*\s#\s*\d+\s*$", l)) >= 3


# --------------------------------------------------------------------------- titres

TITRE_NUM = re.compile(r"^\s*(\d{1,2}(?:\.\d{1,2}){0,2})\.?\s+(\S.{1,110})$")
PARTIE = re.compile(r"^\s*PARTIE\s+(\d+)\s*\.?\s*$", re.I)


def majuscules(s):
    lettres = [c for c in s if c.isalpha()]
    return lettres and sum(c.isupper() for c in lettres) / len(lettres) > 0.7


def successeur(prec, num):
    """Le numéro suit-il logiquement le précédent ? (1.2 → 1.3, 1.3 → 1.3.1, 2.3.2 → 2.4, 1.7 → 2.1…)"""
    a = [int(x) for x in num.split(".")]
    if prec is None:
        return all(x == 1 for x in a)
    p = [int(x) for x in prec.split(".")]
    if len(a) == len(p) + 1 and a[:-1] == p and a[-1] == 1:
        return True
    return any(a[:k] == p[:k] and a[k] == p[k] + 1 and all(x == 1 for x in a[k + 1:]) for k in range(min(len(a), len(p))))


def titres_numerotes(pages):
    """Repère les titres numérotés, dans l'ordre, en écartant les listes et le sommaire."""
    trouves, prec, partie = [], None, None
    for ip, lignes in enumerate(pages):
        if est_sommaire(lignes):
            continue
        for il, l in enumerate(lignes):
            m = PARTIE.match(l)
            if m:
                partie = int(m.group(1))
                trouves.append({"page": ip, "ligne": il, "num": f"P{partie}", "titre": "", "partie": True})
                continue
            m = TITRE_NUM.match(l)
            if not m:
                continue
            num, titre = m.group(1), m.group(2).strip()
            titre = re.sub(r"\s{2,}", " ", titre).rstrip(" .:")
            titre = re.sub(r"\.\s*\(\s*", " (", titre).replace(" )", ")")
            court = len(titre) <= 90 and not titre.endswith((",", ";"))
            # un titre est en majuscules, ou court et à un niveau ≥ 2 (« 5.1 Introduction. »)
            if not court or not (majuscules(titre) or ("." in num and len(titre) < 60)):
                continue
            if not successeur(prec, num):
                continue
            if partie is not None and "." in num and int(num.split(".")[0]) != partie and int(num.split(".")[0]) != partie + 1:
                continue
            trouves.append({"page": ip, "ligne": il, "num": num, "titre": titre})
            prec = num
    # parties dont l'intercalaire est une image (« PARTIE 1 » non lisible) : page courte juste avant n.1
    if any(t.get("partie") for t in trouves):
        connues = {t["num"] for t in trouves if t.get("partie")}
        for t in list(trouves):
            if t.get("partie") or not re.fullmatch(r"\d+\.1", t["num"]) or f"P{t['num'].split('.')[0]}" in connues:
                continue
            ip = t["page"] - 1
            if ip >= 0 and len(re.sub(r"\s", "", "".join(pages[ip]))) < 150:
                trouves.append({"page": ip, "ligne": -1, "num": f"P{t['num'].split('.')[0]}", "titre": "", "partie": True})
        trouves.sort(key=lambda t: (t["page"], t["ligne"]))
    # titre de partie : lignes non vides qui suivent « PARTIE n »
    for t in trouves:
        if t.get("partie"):
            mots = []
            for l in pages[t["page"]][t["ligne"] + 1:]:
                if TITRE_NUM.match(l) or len(" ".join(mots)) > 90:
                    break
                if l.strip() and not PARTIE.match(l):
                    mots.append(l.strip())
            titre = re.sub(r"#\s*\d*", "", " ".join(mots))
            titre = re.sub(r"\s+", " ", titre).strip(" .")
            t["titre"] = (titre[:1].upper() + titre[1:].lower()) if titre else f"Partie {t['num'][1:]}"
    nb = sum(1 for t in trouves if not t.get("partie"))
    return trouves if nb >= 2 else []


def sections_manuelles(sections, pages):
    """Découpage imposé par le catalogue : [{"num", "titre", "page", "debut"?}] — utile pour les scans."""
    if not sections:
        return []
    out = []
    for i, sec in enumerate(sections, 1):
        ip = int(sec.get("page", 1)) - 1
        ligne = -1
        if sec.get("debut"):
            k = cle(sec["debut"])
            ligne = next((il for il, l in enumerate(pages[ip]) if k and k in cle(l)), -1)
        out.append({"page": ip, "ligne": ligne, "num": str(sec.get("num", i)), "titre": sec["titre"]})
    return out


def intertitres(pages):
    """Sans numérotation : intertitres courts, isolés entre deux lignes vides."""
    trouves = []
    for ip, lignes in enumerate(pages):
        for il, l in enumerate(lignes):
            s = l.strip().lstrip(BULLETS + " ")
            if not (4 <= len(s) <= 70) or not s[0].isupper():
                continue
            avant = il == 0 or not lignes[il - 1].strip()
            apres = il + 1 < len(lignes) and not lignes[il + 1].strip()
            if avant and apres and not s.endswith((".", ",", ";", ":")) and len(s.split()) <= 9:
                trouves.append({"page": ip, "ligne": il, "num": str(len(trouves) + 1), "titre": s})
    return trouves if len(trouves) >= 2 else []


# --------------------------------------------------------------------------- corps de texte

def paragraphes(lignes):
    """Regroupe les lignes en paragraphes, puces et sous-titres ; renvoie [(type, texte)]."""
    # puces en milieu de ligne (« Rf ● Article M 1 ») : une ligne par puce
    eclatees = []
    for l in lignes:
        morceaux = re.split(r"\s+[●•▪■➢➤►]\s+", l)
        eclatees.append(morceaux[0])
        eclatees += ["• " + m for m in morceaux[1:]]
    blocs, cur, titre_attendu = [], None, False
    for l in eclatees:
        s = l.strip()
        if not s:
            if cur and not (cur[0] == "h" and titre_attendu):
                blocs.append(cur)
                cur = None
            continue
        if s in ("Rf", "Rf.", "Réf", "Réf."):
            if cur:
                blocs.append(cur)
            blocs.append(["h", "Références réglementaires"])
            cur = None
            continue
        if re.fullmatch(r"(?:[a-z]\.\s*)+", s):
            # « a. » seul sur sa ligne : la ligne suivante est un sous-titre
            if cur:
                blocs.append(cur)
            cur, titre_attendu = ["h", s.split()[-1]], True
            continue
        if titre_attendu:
            cur[1] += " " + s
            blocs.append(cur)
            cur, titre_attendu = None, False
            continue
        m = re.match(r"^((?:[a-z]\.\s+)+)(\S.{0,80})$", s)
        if m and not s.endswith((".", ",", ";")) and len(m.group(2).split()) <= 12:
            # « a.      Calcul théorique et fréquentation réelle » : sous-titre
            if cur:
                blocs.append(cur)
            blocs.append(["h", m.group(1).split()[-1] + " " + m.group(2)])
            cur = None
            continue
        puce = s[0] in BULLETS and (len(s) == 1 or s[1] in " \t")
        if puce:
            if cur:
                blocs.append(cur)
            cur = ["li", s[1:].strip()]
            continue
        if cur is None:
            cur = ["p", s]
        else:
            cur[1] = (cur[1][:-1] + s) if cur[1].endswith("-") and not cur[1].endswith(" -") else (cur[1] + " " + s)
    if cur:
        blocs.append(cur)
    out = []
    for typ, t in blocs:
        t = re.sub(r"\s{2,}", " ", t).strip()
        if t and t not in ("•", "-"):
            out.append((typ, t))
    return out


def html_de(blocs):
    h, liste = [], False
    for typ, t in blocs:
        if typ == "li" and not liste:
            h.append("<ul>")
            liste = True
        if typ != "li" and liste:
            h.append("</ul>")
            liste = False
        e = html.escape(t)
        h.append(f"<li>{e}</li>" if typ == "li" else f"<p><b>{e}</b></p>" if typ == "h" else f"<p>{e}</p>")
    if liste:
        h.append("</ul>")
    return "".join(h)


def texte_de(blocs):
    return "\n".join(("• " if typ == "li" else "") + t for typ, t in blocs)


# --------------------------------------------------------------------------- document → fiches

def slug(nom):
    s = unicodedata.normalize("NFKD", os.path.splitext(nom)[0]).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-") or "document"


def meta_pdf(pdf):
    out = run(["pdfinfo", pdf]).stdout.decode("utf-8", "replace")
    m = re.search(r"CreationDate:\s+\w{3}\s+(\w{3})\s+(\d+)\s+[\d:]+\s+(\d{4})", out)
    if m:
        try:
            return dt.datetime.strptime(" ".join(m.groups()), "%b %d %Y").date().isoformat()
        except ValueError:
            pass
    return None


def fiches(nom, info, ordre0):
    pdf = os.path.join(DOSSIER, nom)
    brut, ocr = lire(pdf)
    pages = nettoie(brut)
    code = info.get("code") or re.sub(r"[^A-Z0-9]", "", slug(nom).upper())[:5]
    sid = f"DOC:{slug(nom)}"
    titre = info.get("titre") or next((l.strip() for p in pages for l in p if len(l.strip()) > 10), nom)
    edition = info.get("edition") or meta_pdf(pdf)
    lien = f"documents/{nom}"
    empreinte = hashlib.sha1(open(pdf, "rb").read()).hexdigest()[:12]
    racine = {
        "Identifiant": sid, "Parent": "", "Type": "Texte", "Domaine": DOM, "Numero": code, "Titre": titre,
        "Chemin": info.get("categorie") or "Autres documents", "Niveau": 0, "Texte_officiel": sid,
        "Derniere_modif_texte": edition, "En_vigueur_depuis": edition, "Lien_Legifrance": lien,
        "Nota": info.get("source", ""), "Pages": f"1-{len(pages)}", "Etat": "VIGUEUR",
        "Historique": json.dumps({"empreinte": empreinte, "ocr": ocr}, ensure_ascii=False),
    }
    titres = sections_manuelles(info.get("sections"), pages) or titres_numerotes(pages) or intertitres(pages)
    if not titres:
        titres = [{"page": i, "ligne": 0, "num": f"p. {i + 1}", "titre": f"Page {i + 1}"} for i in range(len(pages)) if any(l.strip() for l in pages[i])]
    noeuds, ordre = [racine], ordre0
    racine["Ordre"] = ordre
    partie_id = None
    for k, t in enumerate(titres):
        fin = titres[k + 1] if k + 1 < len(titres) else {"page": len(pages) - 1, "ligne": 10 ** 6}
        # lignes du titre jusqu'au titre suivant
        corps = []
        for ip in range(t["page"], fin["page"] + 1):
            lignes = pages[ip]
            a = t["ligne"] + 1 if ip == t["page"] else 0
            b = fin["ligne"] if ip == fin["page"] and k + 1 < len(titres) else len(lignes)
            corps += lignes[a:b] + [""]
        ordre += 1
        p1 = t["page"] + 1
        fp = fin["page"]
        if k + 1 < len(titres) and fp > t["page"]:
            p2 = fp + 1 if any(l.strip() for l in pages[fp][:fin["ligne"]]) else fp
        else:
            p2 = fp + 1
        p2 = max(p1, p2)
        if t.get("partie"):
            partie_id = f"{sid}:{t['num']}"
            noeuds.append({"Identifiant": partie_id, "Parent": sid, "Type": "Section", "Domaine": DOM, "Numero": "",
                           "Titre": f"Partie {t['num'][1:]} — {t['titre']}", "Chemin": titre, "Niveau": 1, "Ordre": ordre,
                           "Texte_officiel": sid, "Lien_Legifrance": f"{lien}#page={p1}", "Pages": f"{p1}"})
            continue
        blocs = paragraphes(corps)
        noeuds.append({
            "Identifiant": f"{sid}:{t['num'].replace(' ', '')}", "Parent": partie_id or sid, "Type": "Article", "Domaine": DOM,
            "Numero": t["num"], "Titre": t["titre"].capitalize() if majuscules(t["titre"]) else t["titre"],
            "Niveau": 2 if partie_id else 1, "Ordre": ordre,
            "Chemin": " › ".join(x for x in [titre, next((n["Titre"] for n in noeuds if n["Identifiant"] == partie_id), "")] if x),
            "Texte": texte_de(blocs), "Texte_HTML": html_de(blocs), "Etat": "VIGUEUR",
            "En_vigueur_depuis": edition, "Texte_officiel": sid, "Lien_Legifrance": f"{lien}#page={p1}",
            "Pages": f"{p1}-{p2}" if p2 > p1 else f"{p1}",
        })
    print(f"{nom} : {len(pages)} pages{f' (dont {ocr} lues par OCR)' if ocr else ''}, {sum(1 for n in noeuds if n['Type'] == 'Article')} fiches", file=sys.stderr)
    return noeuds, ordre


def documents():
    if not os.path.isdir(DOSSIER):
        return []
    cat_path = os.path.join(DOSSIER, "catalogue.json")
    cat = json.load(open(cat_path, encoding="utf-8")) if os.path.exists(cat_path) else {}
    noms = sorted(f for f in os.listdir(DOSSIER) if f.lower().endswith(".pdf"))
    # ordre : catégories puis ordre du catalogue
    rang = {n: i for i, n in enumerate(cat)}
    noms.sort(key=lambda n: (cat.get(n, {}).get("categorie", "~"), rang.get(n, 999), n))
    out, ordre = [], 10 ** 6
    for nom in noms:
        n, ordre = fiches(nom, cat.get(nom, {}), ordre + 1)
        out += n
    return out


def images(dest):
    """Copie les PDF et rend chaque page en image (JPEG ~110 dpi) : dest/<slug>/p001.jpg."""
    os.makedirs(dest, exist_ok=True)
    for nom in os.listdir(DOSSIER):
        if not nom.lower().endswith(".pdf"):
            continue
        pdf = os.path.join(DOSSIER, nom)
        shutil.copy(pdf, os.path.join(dest, nom))
        d = os.path.join(dest, slug(nom))
        os.makedirs(d, exist_ok=True)
        run(["pdftoppm", "-r", "110", "-jpeg", "-jpegopt", "quality=72", pdf, os.path.join(d, "p")])
        # pdftoppm numérote p-01 / p-001 selon le nombre de pages : on uniformise
        for f in os.listdir(d):
            m = re.match(r"p-(\d+)\.jpg$", f)
            if m:
                os.replace(os.path.join(d, f), os.path.join(d, f"p{int(m.group(1)):03d}.jpg"))
    print(f"PDF et images des pages écrits dans {dest}", file=sys.stderr)


def fusionner(fichier, dossier_images=None):
    noeuds = json.load(open(fichier, encoding="utf-8")) if os.path.exists(fichier) else []
    noeuds = [n for n in noeuds if n.get("Domaine") != DOM]
    docs = documents()
    json.dump(noeuds + docs, open(fichier, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"{sum(1 for n in docs if n['Type'] == 'Texte')} document(s), {sum(1 for n in docs if n['Type'] == 'Article')} fiche(s) fusionnés dans {fichier}", file=sys.stderr)
    if dossier_images:
        images(dossier_images)


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "fusionner":
        img = sys.argv[sys.argv.index("--images") + 1] if "--images" in sys.argv else None
        fusionner(sys.argv[2], img)
    elif len(sys.argv) >= 2 and sys.argv[1] == "apercu":
        for n in documents():
            print(("  " * n["Niveau"]) + f"[{n['Type'][0]}] {n['Numero']:6} {n['Titre'][:70]}  (p. {n.get('Pages', '')})  {len(n.get('Texte', ''))} car.")
    else:
        print(__doc__)
