"""Catalogue des planches illustrées : chaque fiche pointe vers une image publiée et des articles existants."""
import json
import os
import re

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_catalogue_coherent():
    cat = json.load(open(os.path.join(RACINE, "widget", "illustrations", "index.json"), encoding="utf-8"))
    ids = set()
    reg = os.path.join(RACINE, "widget", "data", "reglementation.json")
    connus = None
    if os.path.exists(reg):
        connus = {f'{n["Domaine"]}:{re.sub(r"\s+", " ", n["Numero"]).upper()}' for n in json.load(open(reg, encoding="utf-8")) if n.get("Type") == "Article" and n.get("Numero")}
    for f in cat["fiches"]:
        assert f["id"] not in ids, f["id"]
        ids.add(f["id"])
        assert os.path.exists(os.path.join(RACINE, "widget", "illustrations", f["image"].split("?")[0])), f["image"]
        assert f["articles"] and f["titre"] and f["legende"]
        if connus is not None:
            for a in f["articles"]:
                assert a in connus, (f["id"], a)
