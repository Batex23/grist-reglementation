"""Jurisprudence ERP : documents/jurisprudence-erp.odt → widget/data/jurisprudence.json.

Usage : python3 sync/jurisprudence.py   (nécessite pandoc)
Structure du document : titres de chapitre en gras suivis d'une référence en italique
(répétés en tête de page), titres de section en gras, principes en gras (phrases),
décisions précédées d'une puce image et suivies de la référence en italique « (CE, …) ».
"""
import html
import json
import os
import re
import subprocess

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(RACINE, "documents", "jurisprudence-erp.odt")
OUT = os.path.join(RACINE, "widget", "data", "jurisprudence.json")

JURI = re.compile(r"^\s*\(?\s*((?:CE|Conseil d'[ÉE]tat|CAA(?: de| d')?\s*[\wÀ-ÿ\-]+|TA(?: de| d')?\s*[\wÀ-ÿ\-]+|Cass\.?[^,]*|C\.\s*cass\.?[^,]*|Cour de cassation[^,]*|CA(?: de| d')?\s*[\wÀ-ÿ\-]+|Cour d'appel[^,]*|Trib\.[^,]*|Tribunal[^,]*|T\.\s*corr\.[^,]*|Crim\.?[^,]*))", re.I)
DATE = re.compile(r"(\d{1,2}(?:er)?\s+(?:janvier|f[ée]vrier|mars|avril|mai|juin|juillet|ao[ûu]t|septembre|octobre|novembre|d[ée]cembre)\s+\d{4})", re.I)


def md_inline(s):
    s = s.replace("\\'", "'").replace("\\\"", '"').replace("\\...", "…").replace("\\[", "[").replace("\\]", "]").replace("\\*", "*")
    s = re.sub(r"!\[\]\([^)]*\)(\{[^}]*\})?", "", s)
    s = re.sub(r"\[\]\{#[^}]*\}", "", s)
    s = html.escape(s, quote=False)
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s, flags=re.S)
    s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s, flags=re.S)
    s = re.sub(r"\^(.+?)\^", r"<sup>\1</sup>", s)
    s = s.replace("</strong><sup><strong>", "<sup>").replace("</strong></sup><strong>", "</sup>")
    s = s.replace("\\\n", "<br>").replace("\n", " ")
    return s.strip()


def plain(h):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h))).strip()


def main():
    md = subprocess.run(["pandoc", SRC, "-t", "markdown", "--wrap=none"], capture_output=True, text=True, check=True).stdout
    blocks = [b.strip() for b in md.split("\n\n") if b.strip()]
    bold_count = {}
    for b in blocks:
        if b.startswith("**"):
            k = plain(md_inline(b.split("\\\n*(")[0]))
            bold_count[k] = bold_count.get(k, 0) + 1
    chap = sec = prin = ""
    items, chapitres = [], []
    last = None
    for b in blocks:
        raw = re.sub(r"^\[\]\{#[^}]*\}", "", b)
        if raw.startswith("[**") and "sitesecurite" in raw:
            continue
        if raw.startswith("**"):
            head = raw.split("\\\n*(")[0]
            t = plain(md_inline(head))
            if t.startswith("ontenu"):
                t = "C" + t
            if "\\\n*(" in raw or bold_count.get(t, 0) > 1 and t.startswith(("Contenu", "De nombreuses")):
                sub = plain(md_inline(raw[len(head):])) if "\\\n*(" in raw else ""
                if t != chap:
                    chap, sec, prin = t, "", ""
                    if t not in [c["t"] for c in chapitres]:
                        chapitres.append({"t": t, "ref": sub.strip("() ")})
                continue
            if t.startswith("Solution identique") or (len(t) > 85 or t.endswith((".", ":"))) and not (t.endswith(":") and len(t) < 60):
                prin = t
            else:
                t = t.rstrip(" :\u00a0")
                if t != sec:
                    sec, prin = t, ""
            last = None
            continue
        if raw.startswith("![") or last is None:
            body = raw
            last = {"chap": chap, "sec": sec, "prin": prin, "parts": [body]}
            items.append(last)
        else:
            last["parts"].append(raw)
    out = []
    for it in items:
        txt = "\n\n".join(it["parts"])
        lines = [l for l in re.split(r"\\\n|\n\n", txt)]
        paras, cites = [], []
        for l in lines:
            l2 = l.strip()
            m = re.fullmatch(r"\*\((.+)\)\*\.?", l2, flags=re.S) or re.fullmatch(r"\(\*(.+)\*\)", l2, flags=re.S)
            if m and (JURI.match(m.group(1)) or DATE.search(m.group(1))):
                cites.append(plain(md_inline(m.group(1))))
            elif l2:
                paras.append(md_inline(l2))
        if not paras and not cites:
            continue
        juri = date = ""
        if cites:
            mj = JURI.match(cites[0]); md_ = DATE.search(cites[0])
            juri = re.sub(r"\s+", " ", mj.group(1)).strip() if mj else ""
            date = md_.group(1) if md_ else ""
        annee = re.search(r"\b(19|20)\d{2}\b", date or (cites[0] if cites else ""))
        out.append({"c": it["chap"], "s": it["sec"], "p": it["prin"], "h": "<p>" + "</p><p>".join(paras) + "</p>",
                    "cite": cites, "j": juri, "d": date, "y": int(annee.group(0)) if annee else None})
    data = {"chapitres": chapitres, "decisions": out,
            "source": "Compilation de jurisprudence ERP (d'après SiteSécurité, sitesecurite.com) — CCH dans sa numérotation antérieure à 2022 (R. 123-x)"}
    json.dump(data, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(f"{len(chapitres)} chapitres, {len(out)} décisions → {os.path.relpath(OUT, RACINE)}")


if __name__ == "__main__":
    main()
