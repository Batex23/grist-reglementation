"""Test du widget dans un faux Grist (iframe) : installation, idempotence, simulation d'un Journal officiel.
Usage : servir la racine du projet sur http://localhost:8765 puis  python tests/test_widget.py <dossier_captures>"""
import asyncio, copy, json, os, sys
from playwright.async_api import async_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp"
FAKE = open(os.path.join(ROOT, "tests", "fake-grist-api.js")).read()
DATA = json.load(open(os.path.join(ROOT, "widget", "data", "reglementation.json"), encoding="utf-8"))

def jo(data):
    d = copy.deepcopy(data)
    art = next(n for n in d if n["Numero"] == "CO 15")
    art["Identifiant"] = "LEGIARTI999999999001"
    art["Texte"] += "\nAlinéa ajouté par le test."
    art["En_vigueur_depuis"] = "2026-11-12"
    art["Historique"] = json.dumps([{"type": "MODIFIE", "texte": "Arrêté du 10 novembre 2026 - art. 1"}])
    d.remove(next(n for n in d if n["Numero"] == "GN 15"))
    return d

def ok(c, m):
    print(("OK   " if c else "ÉCHEC ") + m)
    if not c: sys.exit(1)

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        pg = await b.new_page(viewport={"width": 1440, "height": 900})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        state = {"v": None, "data": None}
        async def api(route): await route.fulfill(body=FAKE, content_type="application/javascript")
        async def version(route):
            if state["v"]: await route.fulfill(body=json.dumps(state["v"]), content_type="application/json")
            else: await route.continue_()
        async def regl(route):
            if state["data"] is not None: await route.fulfill(body=json.dumps(state["data"]), content_type="application/json")
            else: await route.continue_()
        await pg.route("**/grist-plugin-api.js", api)
        await pg.route("**/data/version.json", version)
        await pg.route("**/data/reglementation.json", regl)
        await pg.goto("http://localhost:8765/tests/host.html")
        fr = pg.frame_locator("#w")
        await fr.locator("#btnInstall").wait_for(timeout=20000)
        await pg.screenshot(path=f"{OUT}/w1-install.png")
        await fr.locator("#btnInstall").click()
        await fr.locator(".sign").first.wait_for(timeout=180000)
        db = lambda: pg.evaluate("({a: __db.T.REG_Articles.length, v: __db.T.REG_Veille.length, c: __db.T.REG_Commentaires.length, s: __db.T.REG_Synonymes.length, p: __db.T.REG_Parametres.map(x=>x.Cle+'='+x.Valeur)})")
        s1 = await db(); print(s1)
        ok(s1["a"] == len(DATA), f"{s1['a']} articles/sections installés")
        ok(s1["s"] > 50, "synonymes installés")
        await pg.screenshot(path=f"{OUT}/w2-home.png")
        # rechargement sans nouvelle version : rien ne bouge
        n_act = await pg.evaluate("__db.actions")
        await pg.evaluate("document.getElementById('w').contentWindow.location.reload()")
        await fr.locator(".sign").first.wait_for(timeout=60000); await pg.wait_for_timeout(1500)
        s2 = await db()
        ok(s2["v"] == s1["v"] and s2["a"] == s1["a"], "aucun changement au rechargement")
        ok(await pg.evaluate("__db.actions") - n_act <= 4, "pas de réécriture inutile")
        # nouveau Journal officiel publié
        state["v"] = {"version": "20261112-999999-test", "base": "2026-11-12"}
        state["data"] = jo(DATA)
        await pg.evaluate("document.getElementById('w').contentWindow.location.reload()")
        await fr.locator(".sign").first.wait_for(timeout=60000)
        await pg.wait_for_function("__db.T.REG_Veille.length > %d" % s2["v"], timeout=60000)
        await pg.wait_for_timeout(1500)
        s3 = await db(); print(s3)
        nat = await pg.evaluate("__db.T.REG_Veille.slice(%d).map(v => v.Nature + ' / ' + v.Titre)" % s2["v"])
        print(nat)
        ok(any("Modification /" in x and "CO 15" in x for x in nat), "modification de CO 15 dans la veille")
        ok(any("Abrogation" in x and "GN 15" in x for x in nat), "abrogation de GN 15 dans la veille")
        co15 = await pg.evaluate("__db.T.REG_Articles.filter(r => r.Numero === 'CO 15').map(r => [r.id, r.Identifiant])")
        ok(len(co15) == 1 and co15[0][1] == "LEGIARTI999999999001", "CO 15 mis à jour sur la même ligne")
        await fr.locator("#btnVeille").click(); await pg.wait_for_timeout(500)
        await fr.locator(".vitem [data-vdiff]").first.click(); await pg.wait_for_timeout(300)
        await pg.screenshot(path=f"{OUT}/w3-veille.png")
        # commentaire enregistré dans REG_Commentaires
        await fr.locator("#q").fill("CO 15"); await fr.locator("#q").press("Enter")
        await fr.locator(".art.active").wait_for()
        await fr.locator(".art.active .acts button[data-tab=cmt]").click()
        await fr.locator("#cform textarea").fill("Retour de visite")
        await fr.locator("#cform button[type=submit]").click(); await pg.wait_for_timeout(1000)
        c = await pg.evaluate("__db.T.REG_Commentaires")
        ok(len(c) == 1 and c[0]["Article"] == co15[0][0], "commentaire relié à CO 15")
        await pg.screenshot(path=f"{OUT}/w4-comment.png")
        ok(not errs, "aucune erreur JavaScript " + str(errs[:3]))
        await b.close()
asyncio.run(main())
