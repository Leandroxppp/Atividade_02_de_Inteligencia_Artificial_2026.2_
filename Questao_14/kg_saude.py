"""Questão 14 — Grafo de Conhecimento (saúde): triplas, inferência por regras e aprendizagem de embeddings (TransE).
O equivalente em Neo4j/Cypher está em neo4j_saude.cypher."""
import numpy as np
from collections import defaultdict

T = [("Dengue","subclasse_de","Arbovirose"),("Zika","subclasse_de","Arbovirose"),("Chikungunya","subclasse_de","Arbovirose"),
     ("Arbovirose","subclasse_de","DoencaInfecciosa"),("Gripe","subclasse_de","DoencaInfecciosa"),
     ("Dengue","tem_sintoma","Febre"),("Dengue","tem_sintoma","DorMuscular"),("Dengue","tem_sintoma","Manchas"),("Dengue","tem_sintoma","DorOcular"),
     ("Zika","tem_sintoma","Manchas"),("Zika","tem_sintoma","Febre"),("Zika","tem_sintoma","Conjuntivite"),
     ("Chikungunya","tem_sintoma","Febre"),("Chikungunya","tem_sintoma","DorArticular"),("Chikungunya","tem_sintoma","Manchas"),
     ("Gripe","tem_sintoma","Febre"),("Gripe","tem_sintoma","Tosse"),("Gripe","tem_sintoma","DorMuscular"),
     ("Paracetamol","trata","Febre"),("Ibuprofeno","trata","Febre"),("Ibuprofeno","contraindicado_em","Dengue"),("Oseltamivir","trata","Gripe"),
     ("Paciente1","tem_sintoma","Febre"),("Paciente1","tem_sintoma","Manchas"),("Paciente1","tem_sintoma","DorOcular"),("Paciente1","toma","Ibuprofeno")]

idx = defaultdict(lambda: defaultdict(set))
for s, r, o in T: idx[r][s].add(o)

def ancestrais(c):                                   # regra: subclasse_de é transitiva
    out, front = set(), [c]
    while front:
        x = front.pop()
        for p in idx["subclasse_de"][x]:
            if p not in out: out.add(p); front.append(p)
    return out

def diagnosticar(paciente):                          # inferência: doenças ordenadas por Jaccard entre sintomas do paciente e da doença
    sp = idx["tem_sintoma"][paciente]; res = []
    for d in {s for s, r, o in T if r == "subclasse_de" and not any(x == s for x, rr, _ in T if rr == "subclasse_de" and _ == s)}:  # folhas
        sd = idx["tem_sintoma"][d]
        if sd: res.append((len(sp & sd) / len(sp | sd), d, sorted(sp & sd)))
    return sorted(res, reverse=True)

def alertas(paciente, diag):                         # regra SWRL-like: toma(P,M) ∧ contraindicado_em(M,D) ∧ suspeita(P,D) ⇒ alerta(P,M)
    return [(m, diag) for m in idx["toma"][paciente] if diag in idx["contraindicado_em"][m]]

# ---------------- Aprendizagem: TransE (h + r ≈ t) ----------------
def transe(triplas, dim=16, ep=400, lr=.05, margem=1.0, seed=1):
    rng = np.random.default_rng(seed); ents = sorted({x for s, _, o in triplas for x in (s, o)}); rels = sorted({r for _, r, _ in triplas})
    ei = {e: i for i, e in enumerate(ents)}; ri = {r: i for i, r in enumerate(rels)}
    E = rng.normal(0, .3, (len(ents), dim)); R = rng.normal(0, .3, (len(rels), dim))
    for _ in range(ep):
        E /= np.linalg.norm(E, axis=1, keepdims=True)
        for s, r, o in triplas:
            s_, r_, o_ = ei[s], ri[r], ei[o]; o_neg = rng.integers(len(ents))
            pos = E[s_] + R[r_] - E[o_]; neg = E[s_] + R[r_] - E[o_neg]
            if margem + np.linalg.norm(pos) - np.linalg.norm(neg) > 0:
                gp, gn = pos / (np.linalg.norm(pos) + 1e-9), neg / (np.linalg.norm(neg) + 1e-9)
                E[s_] -= lr * (gp - gn); R[r_] -= lr * (gp - gn); E[o_] += lr * gp; E[o_neg] -= lr * gn
    return E, R, ei, ri, ents

if __name__ == "__main__":
    print("1) Fechamento transitivo: Dengue ⊑", sorted(ancestrais("Dengue")))
    print("\n2) Diagnóstico por similaridade de subgrafos para Paciente1 (Febre, Manchas, DorOcular):")
    for sc, d, comum in diagnosticar("Paciente1"): print(f"   {d:<12} Jaccard={sc:.2f}  sintomas em comum={comum}")
    top = diagnosticar("Paciente1")[0][1]
    print(f"\n3) Regra de segurança: suspeita={top}; alertas =", alertas("Paciente1", top) or "nenhum",
          "<- Ibuprofeno é contraindicado em Dengue (inferência de um fato novo: alerta)")
    # Aprendizagem: esconde uma tripla e testa se TransE a recupera no ranking
    oculta = ("Zika", "tem_sintoma", "Febre"); treino = [t for t in T if t != oculta]
    E, R, ei, ri, ents = transe(treino)
    q = E[ei["Zika"]] + R[ri["tem_sintoma"]]
    rank = sorted(ents, key=lambda e: np.linalg.norm(q - E[ei[e]]))
    print(f"\n4) TransE (link prediction): tripla oculta {oculta}")
    print("   ranking de candidatos para (Zika, tem_sintoma, ?):", rank[:5], f"-> posição de 'Febre' = {rank.index('Febre')+1}/{len(ents)}")
    # Avaliação mais robusta: oculta CADA tripla tem_sintoma (uma por vez) e repete com 5 sementes; mede posição média (MR) e Hits@3
    pos = []
    for oc in [t for t in T if t[1] == "tem_sintoma" and t[0] not in ("Paciente1",)]:
        for sd in range(5):
            E, R, ei, ri, ents = transe([t for t in T if t != oc], seed=sd)
            if oc[2] not in ei: continue                      # entidade só existia nessa tripla (não há embedding): não avaliável
            q = E[ei[oc[0]]] + R[ri["tem_sintoma"]]
            cand = [e for e in sorted(ents, key=lambda e: np.linalg.norm(q - E[ei[e]])) if (oc[0], "tem_sintoma", e) not in T or e == oc[2]]   # filtra triplas já conhecidas
            pos.append(cand.index(oc[2]) + 1)
    print(f"\n5) Avaliação sobre {len(pos)} previsões (cada tripla oculta × 5 sementes) (ranking filtrado): posição média = {np.mean(pos):.2f}, "
          f"Hits@3 = {np.mean([p <= 3 for p in pos]):.0%}, acaso ≈ metade do nº de candidatos")
