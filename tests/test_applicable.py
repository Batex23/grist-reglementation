"""Grille « Réglementation applicable » : chaque renvoi existe dans la base."""
import json
import os
import subprocess
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_grille():
    subprocess.run([sys.executable, os.path.join(RACINE, "applicable", "build.py")], check=True, capture_output=True)
    data = json.load(open(os.path.join(RACINE, "widget", "data", "applicable.json"), encoding="utf-8"))
    base = json.load(open(os.path.join(RACINE, "widget", "data", "reglementation.json"), encoding="utf-8"))
    nums = {x["Numero"] for x in base if x.get("Type") == "Article" and x.get("Domaine") == "ERP"}
    vus = set()
    for r in data["rub1"] + data["rub2"]:
        assert r["dg"], r["id"]
        vus.update(r["dg"])
    for t in data["types"]:
        assert t["dp"], t["code"]
        for lst in list(t["dp"].values()) + list(t.get("dp5", {}).values()):
            vus.update(lst)
        for a in t["autres"] + t.get("autres5", []):
            vus.update(a["n"])
        if t["livre"] == "II":
            assert t["seuils"], t["code"]
    manquants = vus - nums
    assert not manquants, manquants
    codes = {t["code"] for t in data["types"]}
    assert {"J", "L", "M", "N", "O", "P", "R", "S", "T", "U", "V", "W", "X", "Y", "PA", "CTS", "SG", "OA", "REF", "PS", "GA"} <= codes
