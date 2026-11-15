"""Questão 7 — Avaliação Leave-One-Out do CBR com varredura dos pesos da similaridade e de k.
Cada caso é retirado da base e diagnosticado pelos demais. USO: python avaliacao.py"""
import itertools
from collections import defaultdict
import cbr_medico as C

casos = C.carregar()
def sim(q, c, w, pesos):
    a, b = set(q["sintomas"]), set(c["sintomas"])
    uni = sum(w.get(s, 1) for s in a | b); inter = sum(w.get(s, 1) for s in a & b)
    si = 1 - min(abs(q["idade"] - c["idade"]), 60) / 60; sd = 1 - min(abs(q["dias"] - c["dias"]), 10) / 10
    return pesos[0] * (inter / uni if uni else 0) + pesos[1] * si + pesos[2] * sd
def loo(pesos, k):
    ok = 0
    for i, q in enumerate(casos):
        resto = casos[:i] + casos[i + 1:]; w = C.pesos(resto)
        viz = sorted(((sim(q, c, w, pesos), c) for c in resto), key=lambda t: -t[0])[:k]
        votos = defaultdict(float)
        for s, c in viz: votos[c["diagnostico"]] += s ** 2
        ok += max(votos, key=votos.get) == q["diagnostico"]
    return ok / len(casos)
print(f"Base: {len(casos)} casos")
print("pesos (sintomas, idade, duração)   k=1    k=3    k=5")
for p in [(0.85, 0.10, 0.05), (1, 0, 0), (0.7, 0.2, 0.1), (0.9, 0.1, 0), (0.6, 0.3, 0.1)]:
    print(f"{str(p):<34}" + "  ".join(f"{loo(p, k):5.1%}" for k in (1, 3, 5)))
