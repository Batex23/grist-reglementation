"""Petit moteur de dessin isométrique au style des icônes SDMIS (trois tons par face, contour noir).

Repère : x vers la droite-bas de l'écran, y vers la gauche-bas, z vers le haut ; unités en mètres.
Une scène est une liste d'éléments dessinés dans l'ordre (du fond vers l'avant), exportée en SVG puis PNG.

Icônes : © SDMIS (Service départemental-métropolitain d'incendie et de secours du Rhône), 2023,
licence CC BY-NC-SA 4.0 — https://creativecommons.org/licenses/by-nc-sa/4.0/deed.fr
"""
import base64
import html
import math
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
SPRITES = os.path.join(HERE, "sprites")

C30, S30 = math.cos(math.radians(30)), 0.5
TRAIT = "#141414"

# palettes : (dessus, face gauche +y, face droite +x) — tons des icônes SDMIS
BEIGE = ("#EAD9C4", "#D9C2A6", "#B89E80")
BLEU_VITRE = ("#C8E3F4", "#A9D2EE", "#86B7DB")
GRIS = ("#E4E6EA", "#C9CDD3", "#A4AAB3")
BETON = ("#D8D8D4", "#BDBDB8", "#9C9C97")
ROUGE_CF = ("#F28B82", "#E06A60", "#C24E45")
VERT_GAZON = "#CFE3B5"
ENROBE = "#9EA3A8"
ENROBE_CLAIR = "#B9BDC1"


class Scene:
    def __init__(self, w=1600, h=1100, echelle=26, origine=(800, 300), fond="#FFFFFF"):
        self.w, self.h, self.s = w, h, echelle
        self.ox, self.oy = origine
        self.fond = fond
        self.items = []
        self.defs = []

    # ------------------------------------------------------------------ projection
    def p(self, x, y, z=0.0):
        return (self.ox + (x - y) * C30 * self.s, self.oy + (x + y) * S30 * self.s - z * self.s)

    def pts(self, pts3):
        return " ".join(f"{u:.1f},{v:.1f}" for u, v in (self.p(*q) for q in pts3))

    # ------------------------------------------------------------------ primitives
    def poly(self, pts3, fill, trait=TRAIT, ep=2.2, opacite=1.0, tirets=None):
        dash = f' stroke-dasharray="{tirets}"' if tirets else ""
        st = f'stroke="{trait}" stroke-width="{ep}"' if trait else 'stroke="none"'
        self.items.append(f'<polygon points="{self.pts(pts3)}" fill="{fill}" fill-opacity="{opacite}" {st} stroke-linejoin="round"{dash}/>')

    def sol(self, x, y, dx, dy, fill, trait=TRAIT, ep=1.6, z=0.0, tirets=None, opacite=1.0):
        self.poly([(x, y, z), (x + dx, y, z), (x + dx, y + dy, z), (x, y + dy, z)], fill, trait, ep, opacite, tirets)

    def boite(self, x, y, z, dx, dy, dz, pal=BEIGE, ep=2.4, opacite=1.0, tirets=None):
        dessus, gauche, droite = pal
        # face +y (gauche à l'écran)
        self.poly([(x, y + dy, z), (x + dx, y + dy, z), (x + dx, y + dy, z + dz), (x, y + dy, z + dz)], gauche, ep=ep, opacite=opacite, tirets=tirets)
        # face +x (droite à l'écran)
        self.poly([(x + dx, y, z), (x + dx, y + dy, z), (x + dx, y + dy, z + dz), (x + dx, y, z + dz)], droite, ep=ep, opacite=opacite, tirets=tirets)
        self.poly([(x, y, z + dz), (x + dx, y, z + dz), (x + dx, y + dy, z + dz), (x, y + dy, z + dz)], dessus, ep=ep, opacite=opacite, tirets=tirets)

    def boite_fantome(self, x, y, z, dx, dy, dz, couleur="#6B7280"):
        """Volume en transparence (arêtes cachées en tirets) pour montrer ce qu'il masquerait."""
        pts = lambda *q: [(x + a * dx, y + b * dy, z + c * dz) for a, b, c in q]
        for f in ([(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)], [(0, 0, 0), (0, 1, 0), (0, 1, 1), (0, 0, 1)]):
            self.poly(pts(*f), "#FFFFFF", trait=couleur, ep=1.4, opacite=0.25, tirets="6 5")
        self.boite(x, y, z, dx, dy, dz, ("#F3F4F6", "#E5E7EB", "#D1D5DB"), ep=1.6, opacite=0.55)

    def ligne(self, a, b, couleur=TRAIT, ep=2.0, tirets=None):
        (u1, v1), (u2, v2) = self.p(*a), self.p(*b)
        dash = f' stroke-dasharray="{tirets}"' if tirets else ""
        self.items.append(f'<line x1="{u1:.1f}" y1="{v1:.1f}" x2="{u2:.1f}" y2="{v2:.1f}" stroke="{couleur}" stroke-width="{ep}" stroke-linecap="round"{dash}/>')

    def fenetres_y(self, x, y, z, dx, dz, nb_x, nb_z, larg=1.2, haut=1.3, pal=BLEU_VITRE, marge_bas=0.9):
        """Fenêtres sur la face +y d'un volume (façade tournée vers le spectateur, à gauche)."""
        pas_x, pas_z = dx / nb_x, dz / nb_z
        for i in range(nb_x):
            for k in range(nb_z):
                cx = x + pas_x * (i + 0.5)
                cz = z + pas_z * k + marge_bas
                self.poly([(cx - larg / 2, y, cz), (cx + larg / 2, y, cz), (cx + larg / 2, y, cz + haut), (cx - larg / 2, y, cz + haut)], pal[1], ep=1.4)

    def fenetres_x(self, x, y, z, dy, dz, nb_y, nb_z, larg=1.2, haut=1.3, pal=BLEU_VITRE, marge_bas=0.9):
        pas_y, pas_z = dy / nb_y, dz / nb_z
        for i in range(nb_y):
            for k in range(nb_z):
                cy = y + pas_y * (i + 0.5)
                cz = z + pas_z * k + marge_bas
                self.poly([(x, cy - larg / 2, cz), (x, cy + larg / 2, cz), (x, cy + larg / 2, cz + haut), (x, cy - larg / 2, cz + haut)], pal[2], ep=1.4)

    # ------------------------------------------------------------------ cotes et étiquettes
    def fleche(self, a, b, couleur="#C1121F", ep=2.6, double=True):
        (u1, v1), (u2, v2) = self.p(*a), self.p(*b)
        mid = f"m{len(self.defs)}"
        self.defs.append(f'<marker id="{mid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5.5" markerHeight="5.5" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{couleur}"/></marker>')
        deb = f' marker-start="url(#{mid})"' if double else ""
        self.items.append(f'<line x1="{u1:.1f}" y1="{v1:.1f}" x2="{u2:.1f}" y2="{v2:.1f}" stroke="{couleur}" stroke-width="{ep}"{deb} marker-end="url(#{mid})"/>')

    def cote(self, a, b, texte, decal=(0, 0, 0), couleur="#C1121F", rappel=True, pos=0.5, dx_txt=0, dy_txt=0):
        """Cote entre deux points 3D, décalée de `decal`, avec lignes de rappel et étiquette."""
        a2 = tuple(a[i] + decal[i] for i in range(3))
        b2 = tuple(b[i] + decal[i] for i in range(3))
        if rappel and any(decal):
            self.ligne(a, a2, couleur, 1.4, "4 3")
            self.ligne(b, b2, couleur, 1.4, "4 3")
        self.fleche(a2, b2, couleur)
        m = tuple(a2[i] + (b2[i] - a2[i]) * pos for i in range(3))
        u, v = self.p(*m)
        if texte:
            self.etiquette(u + dx_txt, v + dy_txt, texte, couleur)

    def etiquette(self, u, v, texte, couleur="#C1121F", taille=22, fond="#FFFFFF", gras=True, ancre="middle"):
        lignes = texte.split("\n")
        lmax = max(len(l) for l in lignes)
        w = lmax * taille * 0.56 + 18
        h = len(lignes) * taille * 1.22 + 10
        x0 = u - w / 2 if ancre == "middle" else (u if ancre == "start" else u - w)
        y0 = v - h / 2
        self.items.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{w:.1f}" height="{h:.1f}" rx="7" fill="{fond}" stroke="{couleur}" stroke-width="2"/>')
        for i, l in enumerate(lignes):
            ty = y0 + 6 + taille * 1.0 + i * taille * 1.22
            self.items.append(f'<text x="{x0 + w / 2:.1f}" y="{ty:.1f}" text-anchor="middle" font-family="Inter, DejaVu Sans, sans-serif" font-size="{taille}" font-weight="{700 if gras else 500}" fill="{couleur}">{html.escape(l)}</text>')

    def texte(self, u, v, texte, taille=22, couleur=TRAIT, gras=False, ancre="start", italique=False):
        st = ' font-style="italic"' if italique else ""
        self.items.append(f'<text x="{u:.1f}" y="{v:.1f}" text-anchor="{ancre}" font-family="Inter, DejaVu Sans, sans-serif" font-size="{taille}" font-weight="{700 if gras else 500}" fill="{couleur}"{st}>{html.escape(texte)}</text>')

    def repere(self, pt3, texte, du=0, dv=-60, couleur=TRAIT, taille=20):
        """Étiquette reliée par un trait à un point de la scène."""
        u, v = self.p(*pt3)
        self.items.append(f'<line x1="{u:.1f}" y1="{v:.1f}" x2="{u + du:.1f}" y2="{v + dv:.1f}" stroke="{couleur}" stroke-width="1.6"/>')
        self.items.append(f'<circle cx="{u:.1f}" cy="{v:.1f}" r="4" fill="{couleur}"/>')
        self.etiquette(u + du, v + dv, texte, couleur, taille=taille, gras=False)

    # ------------------------------------------------------------------ icônes
    def icone(self, nom, pt3, largeur_px, ancre=(0.5, 0.92)):
        """Place une icône SDMIS : `ancre` = point de l'image (fractions) posé sur pt3."""
        chemin = os.path.join(SPRITES, nom + ".png")
        from PIL import Image
        with Image.open(chemin) as im:
            w, h = im.size
        hauteur = largeur_px * h / w
        u, v = self.p(*pt3)
        data = base64.b64encode(open(chemin, "rb").read()).decode()
        self.items.append(f'<image x="{u - ancre[0] * largeur_px:.1f}" y="{v - ancre[1] * hauteur:.1f}" width="{largeur_px:.1f}" height="{hauteur:.1f}" href="data:image/png;base64,{data}"/>')

    # ------------------------------------------------------------------ aides de composition
    def motif(self, ident, couleur="#E0A800", ep=3, pas=14, angle=30, fond=None):
        """Hachures réutilisables : renvoie l'url à passer en `fill`."""
        if not any(f'id="{ident}"' in d for d in self.defs):
            bg = f'<rect width="{pas}" height="{pas}" fill="{fond}"/>' if fond else ""
            self.defs.append(f'<pattern id="{ident}" width="{pas}" height="{pas}" patternUnits="userSpaceOnUse" patternTransform="rotate({angle})">{bg}<line x1="0" y1="0" x2="0" y2="{pas}" stroke="{couleur}" stroke-width="{ep}"/></pattern>')
        return f"url(#{ident})"

    def mur_x(self, x, y, z, dx, h, ep=0.25, pal=BEIGE, trait=1.6):
        """Mur mince parallèle à l'axe x (de x à x+dx), épaisseur vers +y."""
        self.boite(x, y, z, dx, ep, h, pal, ep=trait)

    def mur_y(self, x, y, z, dy, h, ep=0.25, pal=BEIGE, trait=1.6):
        self.boite(x, y, z, ep, dy, h, pal, ep=trait)

    def chemin(self, pts3, couleur="#15803D", ep=4.5, tirets=None, fleche=True, opacite=1.0):
        """Cheminement (évacuation…) : polyligne avec flèche finale."""
        mid = f"c{len(self.defs)}"
        self.defs.append(f'<marker id="{mid}" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="3.6" markerHeight="3.6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{couleur}"/></marker>')
        dash = f' stroke-dasharray="{tirets}"' if tirets else ""
        fin = f' marker-end="url(#{mid})"' if fleche else ""
        self.items.append(f'<polyline points="{self.pts(pts3)}" fill="none" stroke="{couleur}" stroke-width="{ep}" stroke-linejoin="round" stroke-linecap="round" stroke-opacity="{opacite}"{dash}{fin}/>')

    def arc_sol(self, c, r, a0, a1, z=0.0, couleur=TRAIT, ep=1.6, tirets="5 4", n=18):
        """Arc horizontal (angles en degrés dans le plan xy, 0 = +x, 90 = +y)."""
        pts = [(c[0] + r * math.cos(math.radians(a0 + (a1 - a0) * k / n)), c[1] + r * math.sin(math.radians(a0 + (a1 - a0) * k / n)), z) for k in range(n + 1)]
        dash = f' stroke-dasharray="{tirets}"' if tirets else ""
        self.items.append(f'<polyline points="{self.pts(pts)}" fill="none" stroke="{couleur}" stroke-width="{ep}"{dash}/>')

    def porte(self, charniere, larg, a_ferme, a_ouvert, z=0.0, couleur=TRAIT, ep=3.2):
        """Porte vue en plan : vantail ouvert (trait plein) + débattement (arc)."""
        cx, cy = charniere
        ex = cx + larg * math.cos(math.radians(a_ouvert)); ey = cy + larg * math.sin(math.radians(a_ouvert))
        self.ligne((cx, cy, z), (ex, ey, z), couleur, ep)
        self.arc_sol((cx, cy), larg, a_ferme, a_ouvert, z, couleur, 1.4)

    def vantail(self, charniere, larg, angle, h=2.1, couleur="#C24E45", z=0.0, arc=True):
        """Vantail de porte ouvert dessiné en volume (panneau vertical) + débattement au sol."""
        cx, cy = charniere
        ex = cx + larg * math.cos(math.radians(angle)); ey = cy + larg * math.sin(math.radians(angle))
        self.poly([(cx, cy, z), (ex, ey, z), (ex, ey, z + h), (cx, cy, z + h)], couleur, ep=1.8)

    def escalier(self, x, y, z, long, larg, haut, n, axe="x", pal=BETON):
        """Volée droite montant dans le sens +axe : n marches."""
        for k in range(n):
            if axe == "x":
                self.boite(x + long * k / n, y, z, long / n, larg, haut * (k + 1) / n, pal, ep=1.2)
            else:
                self.boite(x, y + long * k / n, z, larg, long / n, haut * (k + 1) / n, pal, ep=1.2)

    def ufr(self, u, v, taille=40, fond="#1D4ED8"):
        """Pictogramme « personne en fauteuil roulant » (dessin simplifié)."""
        k = taille / 100
        self.items.append(
            f'<g transform="translate({u - taille / 2:.1f},{v - taille / 2:.1f}) scale({k:.3f})">'
            f'<rect width="100" height="100" rx="14" fill="{fond}" stroke="{TRAIT}" stroke-width="5"/>'
            '<circle cx="44" cy="18" r="9" fill="#fff"/>'
            '<path d="M42 31 L42 58 L66 58 L76 82" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>'
            '<path d="M42 42 L62 42" stroke="#fff" stroke-width="8" stroke-linecap="round"/>'
            '<path d="M30 48 A22 22 0 1 0 62 80" fill="none" stroke="#fff" stroke-width="7" stroke-linecap="round"/></g>')

    def pastille(self, u, v, texte, fond="#C1121F", couleur="#FFFFFF", taille=18, ancre="middle"):
        w = len(texte) * taille * 0.6 + 18
        x0 = u - w / 2 if ancre == "middle" else (u if ancre == "start" else u - w)
        self.items.append(f'<rect x="{x0:.1f}" y="{v - taille * 0.85:.1f}" width="{w:.1f}" height="{taille * 1.55:.1f}" rx="{taille * 0.77:.1f}" fill="{fond}" stroke="{TRAIT}" stroke-width="1.6"/>')
        self.items.append(f'<text x="{x0 + w / 2:.1f}" y="{v + taille * 0.36:.1f}" text-anchor="middle" font-family="Inter, DejaVu Sans, sans-serif" font-size="{taille}" font-weight="700" fill="{couleur}">{html.escape(texte)}</text>')

    def legende(self, u, v, items, taille=17, titre=None, largeur=None):
        """Encadré de légende : items = [(couleur ou url, texte), …]."""
        h = len(items) * (taille + 14) + 20 + (taille + 12 if titre else 0)
        w = largeur or max(len(t) for _, t in items) * taille * 0.56 + 70
        self.items.append(f'<rect x="{u}" y="{v}" width="{w:.0f}" height="{h}" rx="8" fill="#FFFFFF" fill-opacity="0.94" stroke="#9CA3AF" stroke-width="1.4"/>')
        y = v + 14
        if titre:
            self.texte(u + 14, y + taille, titre, taille, TRAIT, gras=True); y += taille + 12
        for fill, t in items:
            self.items.append(f'<rect x="{u + 14}" y="{y}" width="{taille + 8}" height="{taille}" rx="3" fill="{fill}" stroke="{TRAIT}" stroke-width="1.4"/>')
            self.texte(u + taille + 32, y + taille * 0.82, t, taille)
            y += taille + 14
        return h

    def bandeau(self, lignes, hauteur=None, fond="#F3F4F6"):
        """Bande de texte en bas de planche : lignes = [texte] ou [(texte, taille, couleur)]."""
        lignes = [(l, 21, TRAIT) if isinstance(l, str) else l for l in lignes]
        h = hauteur or (sum(t + 9 for _, t, _ in lignes) + 54)
        self.items.append(f'<rect x="0" y="{self.h - h}" width="{self.w}" height="{h}" fill="{fond}"/>')
        y = self.h - h + 18
        for t, taille, c in lignes:
            y += taille + 9
            self.texte(40, y, t, taille, c)
        return h

    def personne(self, pt3, largeur=24, variante=1, femme=False):
        self.icone(("femme20%d" if femme else "homme10%d") % variante, pt3, largeur)

    # ------------------------------------------------------------------ maquettes (plans en volume)
    def volumes(self, boites):
        """Dessine des boîtes alignées sur les axes dans le bon ordre de recouvrement.
        boites : liste de dict(x, y, z, dx, dy, dz, pal, ep, opacite)."""
        n = len(boites)
        def avant(a, b):  # a doit être dessinée avant b ?
            if a["x"] + a["dx"] <= b["x"] + 1e-6: return True
            if a["y"] + a["dy"] <= b["y"] + 1e-6: return True
            if a["z"] + a["dz"] <= b["z"] + 1e-6 and not (b["x"] + b["dx"] <= a["x"] or b["y"] + b["dy"] <= a["y"]): return True
            return False
        succ = {i: set() for i in range(n)}
        deg = [0] * n
        for i in range(n):
            for j in range(n):
                if i != j and avant(boites[i], boites[j]) and not avant(boites[j], boites[i]):
                    succ[i].add(j)
        for i in range(n):
            for j in succ[i]:
                deg[j] += 1
        prets = sorted([i for i in range(n) if deg[i] == 0], key=lambda i: boites[i]["x"] + boites[i]["y"])
        ordre = []
        while prets:
            i = prets.pop(0); ordre.append(i)
            for j in succ[i]:
                deg[j] -= 1
                if deg[j] == 0:
                    prets.append(j)
            prets.sort(key=lambda k: boites[k]["x"] + boites[k]["y"])
        ordre += [i for i in range(n) if i not in ordre]   # cycles éventuels
        for i in ordre:
            b = boites[i]
            self.boite(b["x"], b["y"], b["z"], b["dx"], b["dy"], b["dz"], b.get("pal", BEIGE), b.get("ep", 1.6), b.get("opacite", 1.0))


    # ------------------------------------------------------------------ cartouche
    def cartouche(self, titre, sous_titre, refs, credit=True):
        self.items.append(f'<rect x="0" y="0" width="{self.w}" height="86" fill="#1F2A37"/>')
        self.texte(32, 50, titre, 34, "#FFFFFF", gras=True)
        self.texte(32, 76, sous_titre, 19, "#C9D3DE")
        self.texte(self.w - 32, 52, refs, 26, "#FFD166", gras=True, ancre="end")
        if credit:
            self.texte(self.w - 20, self.h - 16, "Icônes véhicules et personnages © SDMIS 2023, CC BY-NC-SA 4.0 — dessin adapté, SDIS 33", 14, "#6B7280", ancre="end")

    # ------------------------------------------------------------------ export
    def svg(self):
        defs = f"<defs>{''.join(self.defs)}</defs>" if self.defs else ""
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}">'
                f'{defs}<rect width="100%" height="100%" fill="{self.fond}"/>' + "".join(self.items) + "</svg>")

    def enregistrer(self, base):
        """Écrit le PNG (palette optimisée, ~100 ko) ; le SVG de travail va dans cache/illustrations."""
        from PIL import Image
        nom = os.path.basename(base)
        tmp = os.path.join(HERE, "..", "cache", "illustrations")
        os.makedirs(tmp, exist_ok=True)
        os.makedirs(os.path.dirname(base), exist_ok=True)
        svg = os.path.join(tmp, nom + ".svg")
        open(svg, "w", encoding="utf-8").write(self.svg())
        brut = os.path.join(tmp, nom + ".png")
        subprocess.run(["rsvg-convert", "-w", str(self.w), svg, "-o", brut], check=True)
        im = Image.open(brut).convert("RGB")
        im.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(base + ".png", optimize=True)
        return base + ".png"


def mur(x1, y1, x2, y2, h=3.0, ep=0.3, pal=None, z=0.0):
    """Mur entre deux points alignés sur un axe (épaisseur centrée)."""
    pal = pal or ("#F4EFE6", "#D9CDB8", "#BFAF95")
    if abs(y1 - y2) < 1e-9:
        x0, x1_ = min(x1, x2), max(x1, x2)
        return dict(x=x0, y=y1 - ep / 2, z=z, dx=x1_ - x0, dy=ep, dz=h, pal=pal)
    y0, y1_ = min(y1, y2), max(y1, y2)
    return dict(x=x1 - ep / 2, y=y0, z=z, dx=ep, dy=y1_ - y0, dz=h, pal=pal)


MUR = ("#F4EFE6", "#D9CDB8", "#BFAF95")
MUR_CF = ("#F7C6C2", "#EE9D96", "#D9776F")
MUR_PF = ("#FDE2B8", "#F7C27A", "#E0A04A")
MUR_BLEU = ("#D6E6F7", "#A9C8EC", "#7FA8D8")
SOL_INT = "#F6F3EE"
