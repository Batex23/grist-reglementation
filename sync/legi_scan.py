"""Passe 1 : repère, dans une archive LEGI (DILA), les textes ciblés et leur dossier.

Usage :
  python -I legi_scan.py archive.tar.gz > cibles.json          repère les textes
  python -I legi_scan.py extract archive.tar.gz cibles.json dest   extrait leurs dossiers
  python -I legi_scan.py bootstrap dest cibles.json               télécharge + repère + extrait
"""
import json
import re
import sys
import tarfile

from lxml import etree


def rel(name):
    """Chemin relatif à la racine « legi/ » de l'archive."""
    return re.sub(r"^(?:.*?/)?legi/", "", name, count=1)

# Textes recherchés : (domaine, motif sur le titre complet)
CIBLES_TITRE = [
    ("ERP", re.compile(r"^Arrêté du 25 juin 1980 portant approbation des dispositions générales du règlement de sécurité contre les risques d'incendie et de panique dans les établissements recevant du public", re.I)),
    ("IGH", re.compile(r"^Arrêté du 30 décembre 2011 portant règlement de sécurité pour la construction des immeubles de grande hauteur", re.I)),
    ("HAB", re.compile(r"^Arrêté du 31 janvier 1986 relatif à la protection contre l'incendie des bâtiments d'habitation", re.I)),
    ("CDT", re.compile(r"^Arrêté du 5 août 1992 pris pour l'application des articles", re.I)),
]
CODES = {
    "LEGITEXT000006074096": "CCH",   # Code de la construction et de l'habitation
    "LEGITEXT000006072050": "CDT",   # Code du travail
}


def main(path):
    found = {}
    with tarfile.open(path, "r|gz") as tar:
        for m in tar:
            n = m.name
            if "/texte/version/" not in n or not n.endswith(".xml"):
                continue
            leg = n.rsplit("/", 1)[1][:-4]
            base = n.split("/texte/version/")[0]
            if leg in CODES:
                found[leg] = {"domaine": CODES[leg], "dir": rel(base), "titre": None}
                continue
            if "_non_vigueur" in n:
                continue
            data = tar.extractfile(m).read()
            if b"incendie" not in data and b"5 ao" not in data:
                continue
            root = etree.fromstring(data)
            titre = (root.findtext(".//TITREFULL") or "").strip()
            for dom, rx in CIBLES_TITRE:
                if rx.search(titre):
                    if dom == "CDT" and "incendie" not in titre.lower():
                        continue
                    found[leg] = {"domaine": dom, "dir": rel(base), "titre": titre}
                    print(f"trouvé {dom}: {leg} {titre[:90]}", file=sys.stderr)
    json.dump(found, sys.stdout, ensure_ascii=False, indent=1)




def extract(path, cibles, dest):
    """Passe 2 : extrait de l'archive globale uniquement les dossiers des textes ciblés."""
    import os
    import shutil
    dirs = [c["dir"] for c in cibles.values()]
    n = 0
    dest_abs = os.path.abspath(dest)
    with tarfile.open(path, "r|gz") as tar:
        for m in tar:
            if not m.isfile():
                continue
            r = rel(m.name)
            if not any(r.startswith(d + "/") for d in dirs):
                continue
            out = os.path.normpath(os.path.join(dest_abs, r))
            if not out.startswith(dest_abs):
                continue
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with open(out, "wb") as f:
                shutil.copyfileobj(tar.extractfile(m), f)
            n += 1
    print(f"{n} fichiers extraits dans {dest}", file=sys.stderr)


def bootstrap(dest, cibles_path):
    """Télécharge la dernière archive globale LEGI, repère les textes et extrait leurs dossiers."""
    import os
    import re as _re
    import tempfile
    import urllib.request
    base = "https://echanges.dila.gouv.fr/OPENDATA/LEGI/"
    page = urllib.request.urlopen(base, timeout=60).read().decode("utf-8", "replace")
    nom = sorted(set(_re.findall(r'href="(Freemium_legi_global_\d{8}-\d{6}\.tar\.gz)"', page)))[-1]
    tmp = os.path.join(tempfile.gettempdir(), nom)
    if not os.path.exists(tmp):
        print(f"téléchargement de {nom}…", file=sys.stderr)
        urllib.request.urlretrieve(base + nom, tmp)
    if not os.path.exists(cibles_path):
        import contextlib
        import io
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            main(tmp)
        open(cibles_path, "w", encoding="utf-8").write(buf.getvalue())
    cibles = json.load(open(cibles_path, encoding="utf-8"))
    extract(tmp, cibles, dest)
    # date de l'archive : les incréments postérieurs seront appliqués ensuite
    stamp = _re.search(r"(\d{8}-\d{6})", nom).group(1)
    open(os.path.join(dest, "..", "dernier_increment.txt"), "w").write(stamp)


if __name__ == "__main__":
    if sys.argv[1] == "bootstrap":
        bootstrap(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "extract":
        extract(sys.argv[2], json.load(open(sys.argv[3], encoding="utf-8")), sys.argv[4])
    else:
        main(sys.argv[1])
