"""Construit le plan des pages SiteSecurite.com (liens uniquement, aucun contenu recopié).

Chaque chapitre SiteSecurite découpe ses articles en pages par plage (« CO 1 à 5 » → co01a05.php).
Le widget s'en sert pour ouvrir, d'un clic, la page SiteSecurite qui contient l'article lu.

Usage : python -I sync/sitesecurite_liens.py widget/data/sitesecurite.json
"""
import html
import json
import re
import sys
import time
import urllib.request

BASE = "https://sitesecurite.com"
UA = {"User-Agent": "Mozilla/5.0 (grist-veille-incendie)"}

# Pages « sommaire » par code (dispositions communes, générales, particulières, 5e catégorie, spéciales)
ERP = {
    "GN": "erp-dispositions-communes.php?id=accdct_GN",
    **{c: f"erp-dispositions-generales.php?id=accdct_{c}" for c in "GE CO AM DF CH GZ EL EC AS GC MS".split()},
    **{c: f"erp-dispositions-particulieres.php?id=accdct_{c}" for c in "J L M N O P R S T U V W X Y".split()},
    **{c: f"erp-dispositions-5e-categorie.php?id=accdct_{c}" for c in "PE PO PU PX".split()},
    **{c: f"erp-dispositions-speciales.php?id=accdct_{c}" for c in "PA CTS SG OA REF PS GA EF".split()},
}


def get(url):
    for essai in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return r.read().decode("utf-8", "replace")
        except Exception:
            if essai == 2:
                raise
            time.sleep(4 * (essai + 1))


def propre(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def plages(page, code, dossier_base):
    """Extrait les blocs « CODE n à m » → url de la section accordéon du code demandé."""
    i = page.find(f'id="accdct_{code}"')
    if i < 0:
        return [], ""
    j = page.find('id="accdct_', i + 10)
    bloc = page[i: j if j > 0 else len(page)]
    titre = propre(re.search(r'<h2[^>]*>(.*?)</h2>', bloc, re.S).group(1)) if re.search(r'<h2', bloc) else ""
    out, section = [], ""
    for m in re.finditer(r'class="intitule[^"]*">(.*?)</div>|DoHref\(\'([^\']+)\'\);"[^>]*>(.*?)</div>', bloc, re.S):
        if m.group(1) is not None:
            section = propre(m.group(1))
            continue
        cible, libelle = m.group(2), propre(m.group(3))
        url = BASE + "/contenu/" + re.sub(r"^(\.\./)+", "", cible)
        nums = [int(x) for x in re.findall(r"\d+", libelle)]
        if not nums:
            continue
        out.append({"code": code, "de": nums[0], "a": nums[-1], "libelle": libelle, "section": section, "url": url})
    return out, titre


def main(sortie):
    import os
    ancien = json.load(open(sortie, encoding="utf-8")) if os.path.exists(sortie) else {"erp": {}, "chapitres": {}}
    resultat = {"erp": {}, "chapitres": {}, "portails": {
        "ERP": BASE + "/portail-erp.php", "IGH": BASE + "/portail-igh.php", "HAB": BASE + "/portail-hab.php",
        "CDT": BASE + "/portail-bup.php", "CCH": BASE + "/contenu/portail/code/code-construction-2021.php"}}
    for code, chemin in ERP.items():
        url = f"{BASE}/contenu/portail/erp/{chemin}"
        try:
            page = get(url)
        except Exception as e:
            # page momentanément indisponible : on garde le plan connu
            print(f"{code} : indisponible ({e}), plan précédent conservé")
            if code in ancien.get("erp", {}):
                resultat["erp"][code] = ancien["erp"][code]
                resultat["chapitres"][code] = ancien["chapitres"].get(code, {"url": url, "titre": ""})
            continue
        p, titre = plages(page, code, url)
        if not p and code in ancien.get("erp", {}):
            p = ancien["erp"][code]
        resultat["erp"][code] = p
        resultat["chapitres"][code] = {"url": url, "titre": titre}
        print(f"{code} : {len(p)} pages")
        time.sleep(0.6)
    # IGH : pages GH n à m listées sur le portail
    try:
        page = get(BASE + "/portail-igh.php")
        igh = []
        for m in re.finditer(r'href="(/contenu/_igh/igh/gh(\d+)a(\d+)\.php)"', page):
            igh.append({"code": "GH", "de": int(m.group(2)), "a": int(m.group(3)), "libelle": f"GH {int(m.group(2))} à {int(m.group(3))}", "url": BASE + m.group(1)})
        resultat["erp"]["GH"] = igh
        print(f"GH : {len(igh)} pages")
    except Exception as e:
        print("IGH indisponible", e)
        if "GH" in ancien.get("erp", {}):
            resultat["erp"]["GH"] = ancien["erp"]["GH"]
    json.dump(resultat, open(sortie, "w", encoding="utf-8"), ensure_ascii=False, indent=0)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "widget/data/sitesecurite.json")
