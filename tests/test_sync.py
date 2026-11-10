"""Test de bout en bout de la synchronisation, contre un faux serveur Grist en mémoire.

Usage : python -I tests/test_sync.py   (écrit aussi widget/demo-data.json)
"""
import copy
import datetime as dt
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "sync"))
import grist_sync as gs  # noqa: E402


class FakeGrist(gs.Grist):
    def __init__(self):
        self.t = {}
        self.cols = {}
        self.next = 1

    def call(self, method, path, body=None):
        if path == "/tables" and method == "GET":
            return {"tables": [{"id": k} for k in self.t]}
        if path == "/tables" and method == "POST":
            for tb in body["tables"]:
                self.t[tb["id"]] = []
                self.cols[tb["id"]] = tb["columns"]
            return {}
        if path.endswith("/columns") and method == "GET":
            return {"columns": self.cols[path.split("/")[2]]}
        if path.endswith("/columns") and method == "POST":
            self.cols[path.split("/")[2]] += body["columns"]
            return {}
        raise NotImplementedError(method + path)

    def records(self, table):
        return copy.deepcopy(self.t[table])

    def add(self, table, rows):
        ids = []
        for f in rows:
            f = dict(f)
            if table == "REG_Commentaires":
                f.setdefault("Auteur", "Test")
            self.t[table].append({"id": self.next, "fields": f})
            ids.append(self.next)
            self.next += 1
        return ids

    def update(self, table, rows):
        by = {r["id"]: r for r in self.t[table]}
        for r in rows:
            by[r["id"]]["fields"].update(r["fields"])


def check(cond, msg):
    print(("OK   " if cond else "ÉCHEC ") + msg)
    if not cond:
        sys.exit(1)


def main():
    data = json.load(open(os.path.join(ROOT, "widget", "data", "reglementation.json"), encoding="utf-8"))
    g = FakeGrist()
    gs.cmd_init(g, None)
    check(set(g.t) == {"REG_Articles", "REG_Commentaires", "REG_Veille", "REG_Synonymes", "REG_Parametres"}, "tables créées")
    gs.applique(g, data, "2026-11-10", avec_veille=False)
    reg = g.t["REG_Articles"]
    check(len(reg) == len(data), f"{len(reg)} nœuds chargés")
    avenir = [v for v in g.t["REG_Veille"] if v["fields"]["Nature"] == "Modification à venir"]
    check(len(avenir) == sum(1 for n in data if n.get("Version_a_venir")), f"{len(avenir)} modifications à venir signalées dès le chargement")

    # un commentaire sur CO 15 doit survivre à une modification de l'article
    co15 = next(r for r in reg if r["fields"]["Numero"] == "CO 15")
    g.add("REG_Commentaires", [{"Article": co15["id"], "Type": "Interprétation", "Texte": "Test"}])

    # rechargement identique : rien ne doit bouger
    gs.applique(g, data, "2026-11-11", avec_veille=True)
    check(len(g.t["REG_Veille"]) == len(avenir), "aucune fausse alerte quand rien ne change")

    # simulation d'un Journal officiel : CO 15 modifié (nouvel identifiant), un article abrogé, un nouvel article
    jo = copy.deepcopy(data)
    art = next(n for n in jo if n["Numero"] == "CO 15")
    art["Identifiant"] = "LEGIARTI999999999001"
    art["Texte"] = art["Texte"].replace("doivent", "devront", 1) + " Alinéa ajouté pour le test."
    art["En_vigueur_depuis"] = "2026-11-12"
    art["Historique"] = json.dumps([{"type": "MODIFIE", "texte": "Arrêté du 10 novembre 2026 - art. 1", "date": "2026-11-10"}])
    abroge = next(n for n in jo if n["Numero"] == "GN 15")
    jo.remove(abroge)
    nouv = dict(art, Identifiant="LEGIARTI999999999002", Numero="CO 15-1", Texte="Article de test.")
    jo.insert(jo.index(art) + 1, nouv)
    gs.applique(g, jo, "2026-11-12", avec_veille=True)
    nat = [v["fields"]["Nature"] for v in g.t["REG_Veille"][len(avenir):]]
    check(nat.count("Modification") == 1, "modification de CO 15 détectée")
    check(nat.count("Abrogation") == 1, "abrogation de GN 15 détectée")
    check(nat.count("Nouvel article") == 1, "nouvel article détecté")
    co15b = next(r for r in g.t["REG_Articles"] if r["fields"].get("Numero") == "CO 15")
    check(co15b["id"] == co15["id"] and co15b["fields"]["Identifiant"] == "LEGIARTI999999999001", "CO 15 garde sa ligne (et ses commentaires)")
    mod = next(v for v in g.t["REG_Veille"] if v["fields"]["Nature"] == "Modification")
    check("Alinéa ajouté" in mod["fields"]["Nouveau_texte"] and "Alinéa ajouté" not in mod["fields"]["Ancien_texte"], "texte avant / après conservé")

    # parutions SiteSecurite (réseau)
    try:
        gs.cmd_actus(g, None)
        n1 = len(g.t["REG_Veille"])
        gs.cmd_actus(g, None)
        check(len(g.t["REG_Veille"]) == n1, "parutions SiteSecurite non dupliquées")
    except Exception as e:  # pragma: no cover
        print("     (parutions SiteSecurite non testées :", e, ")")



if __name__ == "__main__":
    main()
