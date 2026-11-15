"""Questão 2 — KNN sobre a base de risco de crédito (30 instâncias, Lista 1).
Atributos todos categóricos -> distância de sobreposição (Hamming): d(x,y)=nº de atributos diferentes.
Variante ponderada: pesos = ganho de informação de cada atributo (calculado na Lista 1)."""
import csv, math
from collections import Counter

ATTRS = ["Historia_Credito", "Divida", "Garantia", "Renda", "Emprego", "Patrimonio"]
TARGET = "Risco"
rows = list(csv.DictReader(open("risco_credito_ampliado.csv", encoding="utf-8")))

def entropy(rs):
    c, n = Counter(r[TARGET] for r in rs), len(rs)
    return -sum(v/n*math.log2(v/n) for v in c.values())
def gain(rs, a):
    g = {}
    for r in rs: g.setdefault(r[a], []).append(r)
    return entropy(rs) - sum(len(x)/len(rs)*entropy(x) for x in g.values())
W_GAIN = {a: gain(rows, a) for a in ATTRS}

def dist(x, y, w=None):
    return sum((w[a] if w else 1) for a in ATTRS if x[a] != y[a])

def knn(query, data, k=3, w=None, verbose=False):
    ds = sorted(((dist(query, r, w), r["Exemplo"], r) for r in data), key=lambda t: (t[0], t[1]))
    viz = ds[:k]                      # desempate por ordem do ID
    votos = Counter()
    for d, _, r in viz:               # voto ponderado por 1/(1+d)
        votos[r[TARGET]] += 1/(1+d)
    pred = votos.most_common(1)[0][0]
    if verbose:
        print(f"\nConsulta: {({a: query[a] for a in ATTRS})}")
        print(f"{'ID':<5}{'dist':>6}  classe   | atributos")
        for d, i, r in ds[:8]:
            mark = "<-- vizinho" if (d, i, r) in viz else ""
            print(f"{i:<5}{d:>6.2f}  {r[TARGET]:<9}| {[r[a] for a in ATTRS]} {mark}")
        print("Votos (peso 1/(1+d)):", {c: round(v, 3) for c, v in votos.items()}, "=>", pred)
    return pred

if __name__ == "__main__":
    print("Pesos (ganho de informação):", {a: round(g, 3) for a, g in W_GAIN.items()})
    novo = dict(Historia_Credito="Boa", Divida="Alta", Garantia="Nenhuma",
                Renda="15-35k", Emprego="Estavel", Patrimonio="Medio")
    for k in (1, 3, 5):
        print(f"\n=== k={k} (Hamming) ===")
        pred = knn(novo, rows, k, verbose=True)
        print(f"  => predição com k={k}: {pred}")
    novo2 = dict(Historia_Credito="Ruim", Divida="Baixa", Garantia="Adequada",
                 Renda=">35k", Emprego="Estavel", Patrimonio="Medio")
    print("\n=== Segundo caso, k=3 ===")
    knn(novo2, rows, 3, verbose=True)
    # Caso novo que NÃO existe na base (os dois anteriores têm cópia exata/quase exata): tabela completa das 30 distâncias
    novo3 = dict(Historia_Credito="Boa", Divida="Baixa", Garantia="Adequada", Renda="15-35k", Emprego="Instavel", Patrimonio="Medio")
    print("\n=== Terceiro caso (não existe na base): distâncias a TODAS as 30 instâncias ===")
    for d, i, c in sorted(((dist(novo3, r), r["Exemplo"], r[TARGET]) for r in rows), key=lambda t: (t[0], t[1])):
        print(f"  {i:<4} d={d}  {c}")
    for k in (1, 3, 5, 7):
        print(f"  k={k}: Hamming -> {knn(novo3, rows, k, verbose=(k == 3))} | ponderado por ganho de informação -> {knn(novo3, rows, k, W_GAIN)}")
    print("  (pelas árvores da Lista 1 (ID3/C4.5/CART), Emprego=Instável => Alto: o KNN com Hamming simples DISCORDA, pois Emprego é só 1 de 6 atributos iguais)")
    print("\nAcurácia Leave-One-Out")
    print(f"{'k':>3} {'Hamming':>9} {'Ponderado':>10}")
    for k in (1, 3, 5, 7, 9):
        r = []
        for w in (None, W_GAIN):
            ok = sum(knn(q, [x for x in rows if x is not q], k, w) == q[TARGET] for q in rows)
            r.append(ok/len(rows))
        print(f"{k:>3} {r[0]:>9.1%} {r[1]:>10.1%}")
