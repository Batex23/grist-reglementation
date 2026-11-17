"""Construit widget/data/applicable.json pour l'espace « Réglementation applicable ».

Usage : python3 applicable/build.py [--detail TYPE]
"""
import json
import os
import re
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, ICI)
import grille as G  # noqa: E402

BASE = os.path.join(RACINE, "widget", "data", "reglementation.json")
SORTIE = os.path.join(RACINE, "widget", "data", "applicable.json")
CLIC = os.path.join(ICI, "clic_dp.json")

FAIBLE = re.compile(r"^(?:g[ée]n[ée]ralit[ée]s?|objet|domaine d'application|textes applicables|d[ée]finitions?|champ d'application|dispositions g[ée]n[ée]rales|dispositions applicables)\.?$", re.I)
CLIC_THEMES = {
    "Type": "classement", "Catégorie": "classement", "Desserte": "desserte", "Façades accessibles": "facades_acc",
    "Isolement": "isolement", "Franchissement": "franchissement", "Résistance au feu": "structures", "Couverture": "couverture",
    "Façades": "facades", "Distributions Intérieures": "distribution", "Locaux à risque": "locaux", "Conduits et gaines": "conduits",
    "Aménagements": "amenagements", "Conception": "conception", "UP / Sorties": "calcul", "Enfouissement": "enfouissement",
    "Dégt Accessoires": "accessoires", "Balisage": "balisage", "Sorties": "sorties", "Escaliers": "escaliers",
    "Evacuation Handicapés": "psh", "Désenfumage": "df", "Electricité": "el", "Eclairage": "ec", "Chauffage": "ch",
    "Grandes cuisines": "gc", "Cuisines isolées": "gc", "Cuisines ouvertes": "gc", "Installation Gaz": "gz", "Réserve": "locaux",
    "Moyens d'extinction": "ms_ext", "SSI": "ssi", "Dispositions spéciales": "autres",
}


def charger():
    d = json.load(open(BASE, encoding="utf-8"))
    arts = [x for x in d if x.get("Type") == "Article" and x.get("Domaine") == "ERP" and x.get("Etat", "VIGUEUR") != "ABROGE"]
    return arts


def prefixe(num):
    m = re.match(r"^([A-Z]+) (\d+)", num or "")
    return (m.group(1), int(m.group(2))) if m else (None, None)


def titre(a):
    t = (a.get("Texte") or "").split("\n")[0].strip()
    return t if t and len(t) < 140 and not t.startswith("§") else ""


def section(a):
    return (a.get("Chemin") or "").split(" › ")[-1]


def developper(refs, nums, ordre):
    out = []
    for r in refs:
        m = re.match(r"^([A-Z]+) (\d+)-\1 (\d+)$", r)
        if m:
            p, a, b = m.group(1), int(m.group(2)), int(m.group(3))
            hits = [n for n in ordre if prefixe(n)[0] == p and a <= prefixe(n)[1] <= b]
            if not hits:
                raise SystemExit(f"plage vide : {r}")
            out += hits
        else:
            if r not in nums:
                raise SystemExit(f"référence inconnue : {r}")
            out.append(r)
    return out


def ranger(texte, faible_ok=True):
    if not texte:
        return None
    if not faible_ok:
        texte = re.sub(r"domaine d'application(?: de l'article [A-Z]+ ?\d+)?\.?\s*-?\s*", "", texte, flags=re.I).strip()
        if not texte or FAIBLE.match(texte):
            return None
    for rid, rx in G.MOTS:
        if re.search(rx, texte, re.I):
            return rid
    return None


def refs_clic(chaine):
    """« J 10 (zones) - J 11 (compartiments) » → ['J 10', 'J 11'] ; « S 16 à S 19 » → plage."""
    out = []
    for m in re.finditer(r"\b([A-Z]{1,3}) ?(\d+)(?:\s*à\s*\1 ?(\d+))?", chaine):
        p, a, b = m.group(1), int(m.group(2)), m.group(3)
        out += [f"{p} {i}" for i in range(a, int(b) + 1)] if b else [f"{p} {a}"]
    return out


def main():
    arts = charger()
    ordre = [a["Numero"] for a in arts]
    nums = set(ordre)
    par_num = {a["Numero"]: a for a in arts}
    clic = json.load(open(CLIC, encoding="utf-8"))

    def rub(lst):
        return [{"c": c, "id": i, "t": t, "dg": developper(r, nums, ordre)} for c, i, t, r in lst]

    rub1, rub2 = rub(G.RUBRIQUES_G1), rub(G.RUBRIQUES_G2)
    ids = {r["id"] for r in rub1} | {r["id"] for r in rub2} | {G.AUTRES}

    def placer(liste_nums, code_clic=None):
        place, autres, trace = {}, {}, []
        clic_map = {}
        for row in clic.get(code_clic or "", []):
            rid = CLIC_THEMES.get(row["theme"])
            if row["theme"] == "Chauffage" and "ventilation" in row["dg"]:
                rid = "ventilation"
            if row["theme"] == "Chauffage" and "app production" in row["dg"]:
                rid = "appareils"
            refs = refs_clic(row["dp"])
            if len(refs) > 6:  # plages trop larges dans le tableau source : ignorées
                continue
            for n in refs:
                if n in nums and prefixe(n)[0] == code_clic:
                    clic_map.setdefault(n, rid)
        for n in liste_nums:
            a = par_num[n]
            t, s = titre(a), section(a)
            sec = ranger(re.sub(r"^(Section|Sous-section|Chapitre) [^:]*: ", "", s), faible_ok=False)
            rid = ranger(t, faible_ok=False) or (sec if not t else None) or clic_map.get(n) or sec or (ranger(t) if t else None)
            if rid and rid in ids and rid != G.AUTRES:
                place.setdefault(rid, []).append(n)
            else:
                autres.setdefault(s, []).append(n)
            trace.append((n, t or s, rid))
        return place, [{"s": k, "n": v} for k, v in autres.items()], trace

    types = []
    for code, label, livre in G.TYPES:
        propres = [n for n in ordre if prefixe(n)[0] == code]
        if not propres:
            raise SystemExit(f"type sans article : {code}")
        chap = (par_num[propres[0]].get("Chemin") or "").split(" › ")
        chap = next((c for c in chap if re.search(r"(type|Chapitre)", c, re.I) and code in c), chap[-2] if len(chap) > 1 else "")
        dp, autres, trace = placer(propres, code)
        eff = [n for n in propres if re.search(r"effectif", titre(par_num[n]), re.I)][:2]
        t = {"code": code, "label": label, "livre": livre, "chapitre": chap, "dp": dp, "autres": autres,
             "effectif": eff, "seuils": G.SEUILS.get(code, []), "n": len(propres)}
        if code in G.CHAP5:
            p5 = [n for n in ordre if prefixe(n)[0] == G.CHAP5[code]]
            t["dp5"], t["autres5"], tr5 = placer(p5)
            t["chap5"] = G.CHAP5[code]
            trace += tr5
        if code in G.SOMMEIL_TYPES:
            t["sommeil"] = G.SOMMEIL_TYPES[code]
        types.append(t)
        if len(sys.argv) > 2 and sys.argv[1] == "--detail" and sys.argv[2] in (code, "ALL"):
            print(f"===== {code}")
            for n, tt, rid in trace:
                print(f"  {n:8s} {str(rid):14s} {tt[:80]}")

    sommeil = {k: developper(v, nums, ordre) for k, v in G.SOMMEIL.items()}
    methodes = []
    codes = {c for c, _, _ in G.TYPES}
    for t, mid, ref, lab, unite, k, kp, opt in G.METHODES:
        art = re.match(r"^([A-Z]+ \d+)", ref).group(1)
        if art not in nums or t not in codes:
            raise SystemExit(f"mode de calcul : référence inconnue {ref} ({t})")
        methodes.append({"t": t, "id": mid, "ref": ref, "art": art, "lab": lab, "u": unite, "k": round(k, 6), "kp": round(kp, 6), "o": opt})
    for t in types:
        if t["code"] in G.VARIANTES:
            t["var"] = [{"l": l, "rows": r} for l, r in G.VARIANTES[t["code"]]]
    data = {"rub1": rub1, "rub2": rub2, "sommeil": sommeil, "types": types, "methodes": methodes,
            "source": "Grille d'après le tableau CLIC/DVECRM (PRV2) et le règlement de sécurité en vigueur"}
    json.dump(data, open(SORTIE, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(f"{len(types)} types, {sum(len(r['dg']) for r in rub1)} renvois DG (1er groupe) → {os.path.relpath(SORTIE, RACINE)}")


if __name__ == "__main__":
    main()
