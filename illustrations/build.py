"""Rend toutes les planches illustrées et écrit le catalogue lu par le widget.

Chaque fichier de illustrations/scenes/ définit :
  META = {"id", "titre", "articles": ["ERP:CO 2", …], "fiche", "legende", "ecarts": [...]}
  def dessiner() -> Scene

Usage : python3 illustrations/build.py [motif]   (motif : ne rend que les scènes dont le nom le contient)
Sortie : widget/illustrations/<id>.png + widget/illustrations/index.json
"""
import hashlib
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(HERE)
SORTIE = os.path.join(RACINE, "widget", "illustrations")
sys.path.insert(0, HERE)


def norm(num):
    return re.sub(r"\s+", " ", num.strip()).upper()


def charger(chemin):
    spec = importlib.util.spec_from_file_location(os.path.basename(chemin)[:-3], chemin)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main(filtre=""):
    scenes = sorted(f for f in os.listdir(os.path.join(HERE, "scenes")) if f.endswith(".py") and not f.startswith("_"))
    index_path = os.path.join(SORTIE, "index.json")
    ancien = {f["id"]: f for f in json.load(open(index_path, encoding="utf-8"))["fiches"]} if os.path.exists(index_path) else {}
    connus = None
    reg = os.path.join(RACINE, "widget", "data", "reglementation.json")
    if os.path.exists(reg):
        connus = {f'{n["Domaine"]}:{norm(n["Numero"])}' for n in json.load(open(reg, encoding="utf-8")) if n.get("Type") == "Article" and n.get("Numero")}
    fiches = []
    for f in scenes:
        mod = charger(os.path.join(HERE, "scenes", f))
        meta = dict(mod.META)
        if not filtre or filtre in f:
            png = mod.dessiner().enregistrer(os.path.join(SORTIE, meta["id"]))
            print("rendu", os.path.relpath(png, RACINE))
        png = os.path.join(SORTIE, meta["id"] + ".png")
        if not os.path.exists(png):
            print("  ! image absente :", meta["id"]); continue
        h = hashlib.sha1(open(png, "rb").read()).hexdigest()[:10]
        meta["image"] = f'{meta["id"]}.png?v={h}'
        meta["articles"] = [f'{a.split(":")[0]}:{norm(a.split(":")[1])}' for a in meta["articles"]]
        if connus is not None:
            for a in meta["articles"]:
                if a not in connus:
                    print(f"  ! {meta['id']} : article inconnu {a}")
        meta.setdefault("ordre", len(fiches))
        fiches.append(meta)
    def cle(m):
        dom, num = m["articles"][0].split(":")
        mm = re.match(r"([A-Z]+)\s*(\d+)", num)
        return (dom, mm.group(1) if mm else num, int(mm.group(2)) if mm else 0, m["id"])
    fiches.sort(key=cle)
    for i, m in enumerate(fiches):
        m["ordre"] = i
    json.dump({"version": 1, "credit": "Icônes © SDMIS 2023 (CC BY-NC-SA 4.0) — planches SDIS 33", "fiches": fiches},
              open(index_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(fiches), "planches au catalogue")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "")
