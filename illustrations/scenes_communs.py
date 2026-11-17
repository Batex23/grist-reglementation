"""Éléments de dessin partagés entre scènes."""
from iso import *

ROUGE = "#C1121F"


def volee(x0, x1, y, larg, z0, dz, n=9):
    """Volée droite de x0 vers x1 (sens quelconque), montant de dz."""
    out = []
    w = (x1 - x0) / n
    for k in range(n):
        xa = x0 + k * w
        out.append(dict(x=min(xa, xa + w), y=y, z=z0, dx=abs(w), dy=larg, dz=dz * (k + 1) / n, pal=BETON, ep=1.1))
    return out



def cage_escalier(s, X=6.0, Y=3.2, hn=3.0, N=3):
    """Cage d'escalier encloisonnée en coupe (3 niveaux), portes sur la face +x. Renvoie (X, Y, hn, N)."""
    s.sol(-3, -3, 14, 10, "#E5E7EB", trait=None)
    v = [dict(x=-0.3, y=-0.3, z=0, dx=0.3, dy=Y + 0.3, dz=N * hn, pal=MUR_CF), dict(x=0, y=-0.3, z=0, dx=X, dy=0.3, dz=N * hn, pal=MUR_CF)]
    for k in range(N):
        z0 = k * hn
        v.append(dict(x=4.6, y=0, z=z0 - 0.2 if k else 0, dx=X - 4.6, dy=Y, dz=0.2 if k else 0.05, pal=BETON, ep=1.4))
        v += volee(4.6, 1.0, 0, 1.45, z0, hn / 2)
        v.append(dict(x=0, y=0, z=z0 + hn / 2 - 0.2, dx=1.0, dy=Y, dz=0.2, pal=BETON, ep=1.4))
        v += volee(1.0, 4.6, Y - 1.45, 1.45, z0 + hn / 2, hn / 2)
    s.volumes([b for b in v if b["z"] < N * hn - 0.5])
    s.poly([(0, Y, 0), (X, Y, 0), (X, Y, N * hn), (0, Y, N * hn)], MUR_CF[1], trait=ROUGE, ep=2, opacite=0.22, tirets="8 6")
    s.poly([(X, 0, 0), (X, Y, 0), (X, Y, N * hn), (X, 0, N * hn)], MUR_CF[2], trait=ROUGE, ep=2, opacite=0.30)
    s.poly([(0, 0, N * hn), (X, 0, N * hn), (X, Y, N * hn), (0, Y, N * hn)], "#F3F4F6", trait=TRAIT, ep=2, opacite=0.55)
    for k in range(N):
        z0 = k * hn
        s.poly([(X, 0.9, z0), (X, 2.2, z0), (X, 2.2, z0 + 2.2), (X, 0.9, z0 + 2.2)], "#E8A39C" if k else "#3F8F5A", ep=2)
    return X, Y, hn, N
