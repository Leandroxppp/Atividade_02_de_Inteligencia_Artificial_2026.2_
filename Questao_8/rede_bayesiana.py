"""Questão 8 — Rede Bayesiana para diagnóstico de pneumonia (inferência exata por enumeração).
Implementação própria em NumPy/Python (equivalente a pgmpy.VariableElimination para redes pequenas)."""
import itertools
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, networkx as nx

# Todas as variáveis são binárias: True = "sim"
# CPT: variável -> (pais, {tupla_de_valores_dos_pais: P(var=True | pais)})
NET = {
 "Fumante":   ((), {(): 0.25}),
 "Contato":   ((), {(): 0.15}),                                    # contato recente c/ pessoa com infecção respiratória
 "Pneumonia": (("Fumante", "Contato"), {(True, True): 0.30, (True, False): 0.08, (False, True): 0.15, (False, False): 0.02}),
 "Febre":     (("Pneumonia",), {(True,): 0.85, (False,): 0.10}),
 "Tosse":     (("Pneumonia", "Fumante"), {(True, True): 0.95, (True, False): 0.90, (False, True): 0.35, (False, False): 0.08}),
 "Dispneia":  (("Pneumonia",), {(True,): 0.70, (False,): 0.05}),
 "RaioX":     (("Pneumonia",), {(True,): 0.90, (False,): 0.03}),   # Raio-X com infiltrado pulmonar
}
ORDEM = list(NET)                                                   # já em ordem topológica

def prob(var, val, a):
    pais, t = NET[var]
    p = t[tuple(a[x] for x in pais)]
    return p if val else 1 - p

def conjunta(a): 
    r = 1.0
    for v in ORDEM: r *= prob(v, a[v], a)
    return r

def inferir(consulta, evidencia=None):
    """P(consulta | evidencia) por enumeração da distribuição conjunta."""
    ev = evidencia or {}
    livres = [v for v in ORDEM if v not in ev]
    tot = {True: 0.0, False: 0.0}
    for vals in itertools.product([True, False], repeat=len(livres)):
        a = dict(ev); a.update(zip(livres, vals))
        tot[a[consulta]] += conjunta(a)
    z = tot[True] + tot[False]
    return tot[True] / z

def fmt(ev): return ", ".join(f"{k}={'Sim' if v else 'Não'}" for k, v in ev.items()) or "(nenhuma)"

def exportar_bif(path="pneumonia.bif"):
    """Arquivo de projeto portátil (BIF): abre em pgmpy (BIFReader) e pode ser importado em ferramentas como GeNIe/Netica via conversão."""
    L = ["network pneumonia {\n}"]
    for v in ORDEM: L.append(f"variable {v} {{\n  type discrete [ 2 ] {{ Sim, Nao }};\n}}")
    for v in ORDEM:
        pais, t = NET[v]
        if not pais: L.append(f"probability ( {v} ) {{\n  table {t[()]}, {round(1-t[()],6)};\n}}")
        else:
            L.append(f"probability ( {v} | {', '.join(pais)} ) {{")
            for k, p in t.items(): L.append(f"  ({', '.join('Sim' if x else 'Nao' for x in k)}) {p}, {round(1-p,6)};")
            L.append("}")
    open(path, "w", encoding="utf-8").write("\n".join(L) + "\n")

if __name__ == "__main__":
    exportar_bif()
    print("A priori: P(Pneumonia)=%.4f" % inferir("Pneumonia"))
    print("\n=== Experimento 1: atualização sequencial ===")
    ev = {}
    print(f"{'Evidências acumuladas':<58}{'P(Pneumonia|e)':>15}")
    print(f"{fmt(ev):<58}{inferir('Pneumonia', ev):>15.4f}")
    for k, v in [("Febre", True), ("Tosse", True), ("Dispneia", True), ("RaioX", True)]:
        ev[k] = v; print(f"{fmt(ev):<58}{inferir('Pneumonia', ev):>15.4f}")
    print("\n=== Experimento 2: comparação de conjuntos de evidência (explaining away) ===")
    for e in [{"Tosse": True}, {"Tosse": True, "Fumante": True}, {"Tosse": True, "Fumante": False},
              {"Febre": True, "Tosse": True}, {"Febre": True, "Tosse": True, "Fumante": True}]:
        print(f"{fmt(e):<58}{inferir('Pneumonia', e):>15.4f}")
    print("\n=== Experimento 3: evidência negativa e fatores de risco (inferência causal/diagnóstica) ===")
    for e in [{"Fumante": True, "Contato": True}, {"Fumante": False, "Contato": False},
              {"Febre": False, "Tosse": False, "Dispneia": False}, {"RaioX": True}, {"RaioX": False, "Febre": True, "Tosse": True}]:
        print(f"{fmt(e):<58}{inferir('Pneumonia', e):>15.4f}")
    print("\n=== Predição de sintomas dado diagnóstico ===")
    for e in [{"Pneumonia": True}, {"Pneumonia": False}]:
        print(fmt(e), {s: round(inferir(s, e), 3) for s in ["Febre", "Tosse", "Dispneia", "RaioX"]})
    # --- verificação de independência condicional: Febre ⟂ Tosse | Pneumonia ---
    a = inferir("Febre", {"Pneumonia": True, "Tosse": True}); b = inferir("Febre", {"Pneumonia": True})
    c = inferir("Febre", {"Tosse": True});                    d = inferir("Febre")
    print(f"\nFebre⟂Tosse|Pneumonia? P(F|P,T)={a:.4f} = P(F|P)={b:.4f};  mas sem P: P(F|T)={c:.4f} ≠ P(F)={d:.4f}")
    # --- grafo ---
    g = nx.DiGraph([(p, v) for v, (ps, _) in NET.items() for p in ps])
    pos = {"Fumante": (0, 2), "Contato": (2, 2), "Pneumonia": (1, 1), "Tosse": (-0.5, 0), "Febre": (0.7, 0), "Dispneia": (1.8, 0), "RaioX": (3, 0)}
    plt.figure(figsize=(8, 4.5))
    nx.draw(g, pos, with_labels=True, node_size=3200, node_color="#cfe3ff", arrowsize=18, font_size=9, edgecolors="k")
    plt.savefig("rede.png", dpi=120, bbox_inches="tight")
