"""Passe 2 : reconstruit l'arborescence en vigueur (et les versions à venir) des textes ciblés.

Usage : python -I legi_build.py <dossier_extrait> cibles.json AAAA-MM-JJ > reglementation.json

Le dossier extrait contient l'arborescence LEGI (…/legi/global/…) limitée aux textes ciblés.
Sortie : liste ordonnée de nœuds (sections et articles) prêts pour Grist.
"""
import html
import json
import os
import re
import sys

from lxml import etree

FIN_OUVERTE = "2999-01-01"

# Filtre des codes : seuls ces articles sont gardés (les sections vides sont élaguées)
FILTRE_CODES = {
    "CDT": re.compile(r"^R\.? ?42(16|27)-"),
    "CCH": re.compile(r"^(L|R)\.? ?14[1-6]-"),
}

ALLOWED_TAGS = {"p", "br", "table", "tr", "td", "th", "tbody", "thead", "ul", "ol", "li",
                "b", "strong", "i", "em", "sup", "sub", "u", "div", "span", "blockquote", "pre", "img"}


def index_dir(root):
    """id LEGI -> chemin du fichier (articles, sections, textes)."""
    idx = {}
    for d, _, files in os.walk(root):
        for f in files:
            if f.endswith(".xml"):
                key = f[:-4]
                p = os.path.join(d, f)
                if "/texte/struct/" in p:
                    idx["struct:" + key] = p
                elif "/texte/version/" in p:
                    idx["version:" + key] = p
                else:
                    idx[key] = p
    return idx


def valide(lien, date):
    return lien.get("debut", "") <= date < (lien.get("fin") or FIN_OUVERTE)


def a_venir(lien, date):
    return lien.get("debut", "") > date


def nettoie_html(el):
    """Conserve un HTML simple et sûr du contenu d'un article."""
    if el is None:
        return ""
    out = []

    def walk(node):
        tag = node.tag if isinstance(node.tag, str) else None
        if tag and tag.lower() in ALLOWED_TAGS:
            t = tag.lower()
            if t == "img":
                return  # les schémas Légifrance ne sont pas inclus (lien vers Légifrance)
            attrs = ""
            if t in ("td", "th"):
                for a in ("colspan", "rowspan"):
                    if node.get(a):
                        attrs += f' {a}="{html.escape(node.get(a))}"'
            out.append(f"<{t}{attrs}>")
            if node.text:
                out.append(html.escape(node.text))
            for c in node:
                walk(c)
            if t != "br":
                out.append(f"</{t}>")
        else:
            if node.text:
                out.append(html.escape(node.text))
            for c in node:
                walk(c)
        if node.tail:
            out.append(html.escape(node.tail))

    if el.text:
        out.append(html.escape(el.text))
    for c in el:
        walk(c)
    s = "".join(out)
    s = re.sub(r"(<br>\s*){3,}", "<br><br>", s)
    return s.strip()


def texte_brut(el):
    if el is None:
        return ""
    parts = []
    for t in el.itertext():
        parts.append(t)
    s = " ".join(parts)
    s = re.sub(r"[ \t\r\f\v]+", " ", s)
    s = re.sub(r"\s*\n\s*", "\n", s)
    return s.strip()


def lit_article(path):
    root = etree.parse(path).getroot()
    contenu = root.find("BLOC_TEXTUEL/CONTENU")
    nota = root.find("NOTA/CONTENU")
    liens_modif = []
    for l in root.findall("LIENS/LIEN"):
        if l.get("sens") == "cible" and l.get("typelien") in ("MODIFIE", "CREE", "CREATION", "TRANSFERE", "ABROGE"):
            liens_modif.append({
                "type": l.get("typelien"),
                "texte": (l.text or "").strip(),
                "date": l.get("datesignatexte") or "",
                "cid": l.get("cidtexte") or "",
            })
    return {
        "num": (root.findtext("META/META_SPEC/META_ARTICLE/NUM") or "").strip(),
        "etat": root.findtext("META/META_SPEC/META_ARTICLE/ETAT") or "",
        "debut": root.findtext("META/META_SPEC/META_ARTICLE/DATE_DEBUT") or "",
        "fin": root.findtext("META/META_SPEC/META_ARTICLE/DATE_FIN") or "",
        "html": nettoie_html(contenu),
        "texte": texte_brut(contenu),
        "nota": texte_brut(nota),
        "modifs": liens_modif,
    }


def build(root_dir, cibles, date):
    idx = index_dir(root_dir)
    nodes = []
    ordre = [0]

    for legitext, info in cibles.items():
        dom = info["domaine"]
        est_code = legitext in ("LEGITEXT000006074096", "LEGITEXT000006072050")
        filtre = FILTRE_CODES.get(dom) if est_code else None
        vpath = idx.get("version:" + legitext)
        spath = idx.get("struct:" + legitext)
        if not spath:
            print(f"!! struct introuvable pour {legitext}", file=sys.stderr)
            continue
        vroot = etree.parse(vpath).getroot() if vpath else None
        titre_txt = (vroot.findtext(".//TITREFULL") if vroot is not None else None) or info.get("titre") or legitext
        derniere = etree.parse(spath).getroot().findtext(".//DERNIERE_MODIFICATION") or ""
        base_url = "https://www.legifrance.gouv.fr/" + ("codes" if est_code else "loda")

        text_node = {
            "Identifiant": legitext, "Parent": "", "Type": "Texte", "Domaine": dom,
            "Numero": "", "Titre": re.sub(r"\s+", " ", titre_txt.strip()), "Niveau": 0,
            "Texte_officiel": legitext, "Derniere_modif_texte": derniere,
            "Lien_Legifrance": f"{base_url}/id/{legitext}/" if not est_code else f"{base_url}/texte_lc/{legitext}/",
        }

        def sections_et_articles(el):
            return [c for c in el if c.tag in ("LIEN_SECTION_TA", "LIEN_ART")]

        def visite(liens, parent_id, niveau, chemin):
            produits = []
            # articles regroupés par numéro pour repérer les versions à venir
            futurs = {}
            for l in liens:
                if l.tag == "LIEN_ART" and a_venir(l, date):
                    futurs.setdefault(l.get("num") or l.get("id"), []).append(l)
            for l in liens:
                if not valide(l, date):
                    continue
                lid = l.get("id")
                if l.tag == "LIEN_SECTION_TA":
                    p = idx.get(lid)
                    if not p:
                        continue
                    sroot = etree.parse(p).getroot()
                    titre = re.sub(r"\s+", " ", (sroot.findtext("TITRE_TA") or l.text or "").strip())
                    ordre[0] += 1
                    snode = {
                        "Identifiant": lid, "Parent": parent_id, "Type": "Section", "Domaine": dom,
                        "Numero": "", "Titre": titre, "Niveau": niveau, "Ordre": ordre[0],
                        "Chemin": " › ".join(chemin), "Texte_officiel": legitext,
                        "Lien_Legifrance": f"{base_url}/section_lc/{legitext}/{lid}/",
                    }
                    enfants = visite(sections_et_articles(sroot.find("STRUCTURE_TA")), lid, niveau + 1, chemin + [titre])
                    if filtre and not enfants:
                        continue
                    produits.append(snode)
                    produits.extend(enfants)
                else:
                    num = (l.get("num") or "").strip()
                    if filtre and not filtre.match(num):
                        continue
                    p = idx.get(lid)
                    if not p:
                        print(f"!! article introuvable {lid}", file=sys.stderr)
                        continue
                    a = lit_article(p)
                    ordre[0] += 1
                    node = {
                        "Identifiant": lid, "Parent": parent_id, "Type": "Article", "Domaine": dom,
                        "Numero": a["num"] or num, "Titre": "", "Niveau": niveau, "Ordre": ordre[0],
                        "Chemin": " › ".join(chemin), "Texte_officiel": legitext,
                        "Texte": a["texte"], "Texte_HTML": a["html"], "Nota": a["nota"],
                        "Etat": a["etat"], "En_vigueur_depuis": a["debut"],
                        "Fin_de_vigueur": "" if a["fin"] == FIN_OUVERTE else a["fin"],
                        "Historique": json.dumps(a["modifs"], ensure_ascii=False),
                        "Lien_Legifrance": f"{base_url}/article_lc/{lid}/",
                    }
                    f = [x for x in futurs.get(num or lid, []) if x.get("id") != lid]
                    if f:
                        f.sort(key=lambda x: x.get("debut"))
                        fl = f[0]
                        fp = idx.get(fl.get("id"))
                        if fp:
                            fa = lit_article(fp)
                            node["Version_a_venir"] = fa["texte"]
                            node["Version_a_venir_HTML"] = fa["html"]
                            node["Date_a_venir"] = fl.get("debut")
                            node["A_venir_par"] = json.dumps(fa["modifs"], ensure_ascii=False)
                    produits.append(node)
            # articles créés dans le futur (n'existent pas encore aujourd'hui)
            nums_courants = {(l.get("num") or l.get("id")) for l in liens if l.tag == "LIEN_ART" and valide(l, date)}
            for num, lst in futurs.items():
                if num in nums_courants:
                    continue
                if filtre and not filtre.match(num):
                    continue
                fl = sorted(lst, key=lambda x: x.get("debut"))[0]
                fp = idx.get(fl.get("id"))
                if not fp:
                    continue
                fa = lit_article(fp)
                ordre[0] += 1
                produits.append({
                    "Identifiant": fl.get("id"), "Parent": parent_id, "Type": "Article", "Domaine": dom,
                    "Numero": fa["num"] or num, "Titre": "", "Niveau": niveau, "Ordre": ordre[0],
                    "Chemin": " › ".join(chemin), "Texte_officiel": legitext,
                    "Texte": "", "Texte_HTML": "", "Etat": "A_VENIR",
                    "Version_a_venir": fa["texte"], "Version_a_venir_HTML": fa["html"],
                    "Date_a_venir": fl.get("debut"), "A_venir_par": json.dumps(fa["modifs"], ensure_ascii=False),
                    "Lien_Legifrance": f"{base_url}/article_lc/{fl.get('id')}/",
                })
            return produits

        ordre[0] += 1
        text_node["Ordre"] = ordre[0]
        struct = etree.parse(spath).getroot().find("STRUCT")
        corps = visite(sections_et_articles(struct), legitext, 1, [text_node["Titre"] if not est_code else ("Code de la construction et de l'habitation" if dom == "CCH" else "Code du travail")])
        nodes.append(text_node)
        nodes.extend(corps)
        n_art = sum(1 for n in corps if n["Type"] == "Article")
        print(f"{dom} {legitext}: {n_art} articles, {len(corps) - n_art} sections", file=sys.stderr)
    return repartit_cch(nodes)


DOM_CCH = {"141": "CCH", "142": "HAB", "143": "ERP", "144": "CDT", "145": "IGH", "146": "IGH"}
LIB_CCH = {"CCH": "dispositions communes", "HAB": "bâtiments d'habitation", "ERP": "établissements recevant du public",
           "CDT": "bâtiments à usage professionnel", "IGH": "immeubles de moyenne et de grande hauteur"}


def repartit_cch(nodes):
    """Range les articles incendie du CCH sous la réglementation qu'ils concernent (ERP, IGH, HAB…)."""
    cch = "LEGITEXT000006074096"
    autres = [n for n in nodes if n["Texte_officiel"] != cch]
    du_code = [n for n in nodes if n["Texte_officiel"] == cch]
    if not du_code:
        return nodes
    racine = next(n for n in du_code if n["Type"] == "Texte")
    par_id = {n["Identifiant"]: n for n in du_code}
    sortie = list(autres)
    for dom in ["ERP", "IGH", "HAB", "CDT", "CCH"]:
        garder = set()
        for n in du_code:
            if n["Type"] == "Article":
                m = re.match(r"^[LR]\.? ?(\d{3})-", n["Numero"])
                if m and DOM_CCH.get(m.group(1)) == dom:
                    garder.add(n["Identifiant"])
                    p = n["Parent"]
                    while p in par_id and par_id[p]["Type"] != "Texte":
                        garder.add(p)
                        p = par_id[p]["Parent"]
        if not garder:
            continue
        vid = f"{cch}#{dom}"
        sortie.append({**racine, "Identifiant": vid, "Domaine": dom, "Texte_officiel": vid,
                       "Titre": f"Code de la construction et de l'habitation — {LIB_CCH[dom]}"})
        for n in du_code:
            if n["Identifiant"] in garder:
                c = dict(n, Domaine=dom, Texte_officiel=vid)
                if c["Parent"] == cch:
                    c["Parent"] = vid
                # le doublon de section entre domaines reçoit un identifiant propre
                if c["Type"] == "Section":
                    c["Identifiant"] = f"{n['Identifiant']}#{dom}"
                elif par_id.get(c["Parent"], {}).get("Type") == "Section":
                    c["Parent"] = f"{c['Parent']}#{dom}"
                if c["Type"] == "Section" and par_id.get(n["Parent"], {}).get("Type") == "Section":
                    c["Parent"] = f"{n['Parent']}#{dom}"
                sortie.append(c)
    # ordre global : domaine, puis texte, puis ordre d'origine
    rang = {"ERP": 0, "IGH": 1, "HAB": 2, "CDT": 3, "CCH": 4}
    textes = {}
    for n in sortie:
        if n["Type"] == "Texte":
            textes[n["Texte_officiel"]] = (rang.get(n["Domaine"], 9), 1 if "#" in n["Texte_officiel"] else 0, n["Ordre"])
    sortie.sort(key=lambda n: (textes[n["Texte_officiel"]], 0 if n["Type"] == "Texte" else 1, n["Ordre"]))
    for i, n in enumerate(sortie, 1):
        n["Ordre"] = i
    return sortie


if __name__ == "__main__":
    root_dir, cibles_path, date = sys.argv[1], sys.argv[2], sys.argv[3]
    cibles = json.load(open(cibles_path, encoding="utf-8"))
    json.dump(build(root_dir, cibles, date), sys.stdout, ensure_ascii=False)


def empreinte(n):
    """Empreinte du contenu indexé sémantiquement (pour ne recalculer que ce qui change)."""
    import hashlib
    return hashlib.sha1((n.get("Numero", "") + n.get("Chemin", "") + n.get("Titre", "") + n.get("Texte", "") + n.get("Version_a_venir", "")).encode()).hexdigest()[:12]
