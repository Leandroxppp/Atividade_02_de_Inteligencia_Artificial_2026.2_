"""Questão 6 — Sistema fuzzy Mamdani para risco de crédito (continuidade da Lista 1).
Implementação em NumPy com a mesma semântica do scikit-fuzzy (trimf/trapmf, interp_membership, defuzz 'centroid').
Entradas: Renda (mil R$/mês, 0-40), Comprometimento (% da renda em dívidas, 0-100), Histórico (score 0-10)
Saída: Risco (0-100)."""
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

def trimf(x, a, b, c):
    return np.maximum(np.minimum((x-a)/(b-a+1e-12), (c-x)/(c-b+1e-12)), 0)
def trapmf(x, a, b, c, d):
    return np.maximum(np.minimum(np.minimum((x-a)/(b-a+1e-12), 1), (d-x)/(d-c+1e-12)), 0)
def interp_membership(x, mf, v): return float(np.interp(v, x, mf))
def centroid(x, mf): return float((x*mf).sum()/mf.sum()) if mf.sum() > 0 else 0.0

# ---------- Universos de discurso ----------
renda = np.arange(0, 40.01, 0.1)
comp  = np.arange(0, 100.01, 0.5)
hist  = np.arange(0, 10.01, 0.05)
risco = np.arange(0, 100.01, 0.5)

# ---------- Funções de pertinência (fuzzificação) ----------
MF = {
 "renda": {"baixa": trapmf(renda, 0, 0, 8, 16), "media": trimf(renda, 10, 22, 34), "alta": trapmf(renda, 28, 35, 40, 40)},
 "comp":  {"baixo": trapmf(comp, 0, 0, 15, 35), "medio": trimf(comp, 25, 45, 65), "alto": trapmf(comp, 55, 75, 100, 100)},
 "hist":  {"ruim": trapmf(hist, 0, 0, 2, 4.5), "regular": trimf(hist, 3, 5.5, 8), "bom": trapmf(hist, 6.5, 8.5, 10, 10)},
 "risco": {"baixo": trapmf(risco, 0, 0, 15, 35), "moderado": trimf(risco, 25, 50, 75), "alto": trapmf(risco, 65, 85, 100, 100)},
}
X = {"renda": renda, "comp": comp, "hist": hist, "risco": risco}

# ---------- Base de regras (Mamdani: AND=min, OR=max) ----------
# (renda, comp, hist) -> risco ; None = "qualquer"
R = [
 ("alta",  None,    "bom",     "baixo"),
 ("alta",  "baixo", None,      "baixo"),
 ("media", "baixo", "bom",     "baixo"),
 ("media", "medio", "regular", "moderado"),
 ("media", "baixo", "regular", "moderado"),
 ("alta",  "alto",  "regular", "moderado"),
 ("baixa", "baixo", "bom",     "moderado"),
 (None,    "medio", "bom",     "moderado"),
 ("media", "alto",  "regular", "alto"),      # R9 (corrigida: antes ignorava o histórico)
 ("media", "alto",  "bom",     "moderado"),  # R14 (nova): bom histórico atenua o endividamento alto
 ("alta",  "alto",  "bom",     "moderado"),  # R15 (nova)
 ("baixa", "alto",  None,      "alto"),
 ("baixa", None,    "ruim",    "alto"),
 (None,    None,    "ruim",    "alto"),
 ("baixa", "medio", None,      "alto"),
]

def inferir(v_renda, v_comp, v_hist, verbose=False):
    mu = {"renda": {k: interp_membership(renda, f, v_renda) for k, f in MF["renda"].items()},
          "comp":  {k: interp_membership(comp,  f, v_comp)  for k, f in MF["comp"].items()},
          "hist":  {k: interp_membership(hist,  f, v_hist)  for k, f in MF["hist"].items()}}
    agg = np.zeros_like(risco)
    if verbose:
        print("Fuzzificação:"); [print(f"  {a}: { {k: round(v,2) for k,v in d.items()} }") for a, d in mu.items()]
        print("Regras ativadas (força = min dos antecedentes):")
    for i, (r, c, h, out) in enumerate(R, 1):
        ants = [mu["renda"][r] if r else 1, mu["comp"][c] if c else 1, mu["hist"][h] if h else 1]
        w = min(ants)
        agg = np.maximum(agg, np.minimum(w, MF["risco"][out]))   # implicação (corte) + agregação (max)
        if verbose and w > 0:
            q = lambda v: "qualquer" if v is None else v
            print(f"  R{i:<2} SE renda={q(r)} E comp={q(c)} E hist={q(h)} ENTÃO risco={out}  -> w={w:.2f}")
    return centroid(risco, agg), agg

def bisector(x, mf):
    c = np.cumsum(mf); return float(x[np.searchsorted(c, c[-1] / 2)]) if c[-1] > 0 else 0.0
def mom(x, mf):   # média dos máximos
    return float(x[mf >= mf.max() - 1e-9].mean()) if mf.max() > 0 else 0.0

def rotulo(v): return "BAIXO" if v < 33 else "MODERADO" if v < 66 else "ALTO"

if __name__ == "__main__":
    casos = {"Cliente A (renda alta, pouco endividado, bom histórico)": (32, 12, 9),
             "Cliente B (renda média, endividamento médio, histórico regular)": (20, 45, 5),
             "Cliente C (renda baixa, muito endividado, histórico ruim)": (6, 80, 1.5),
             "Cliente D (renda média, endividamento alto, bom histórico)": (22, 70, 8),
             "Cliente E (renda alta, endividamento alto, bom histórico)": (36, 70, 8)}
    out = []
    for nome, (a, b, c) in casos.items():
        print(f"\n=== {nome}: renda={a}k, comprometimento={b}%, histórico={c}")
        v, agg = inferir(a, b, c, verbose=True)
        print(f"Defuzzificação (centroide): risco = {v:.1f} -> {rotulo(v)}")
        out.append((nome, agg, v))
        print(f"  Outros defuzzificadores: bisetriz={bisector(risco, agg):.1f} | média dos máximos={mom(risco, agg):.1f}")
    # ----- Figuras -----
    fig, ax = plt.subplots(2, 2, figsize=(11, 7))
    for a, (k, t) in zip(ax.ravel(), [("renda","Renda (mil R$)"),("comp","Comprometimento (%)"),("hist","Histórico (0-10)"),("risco","Risco (0-100)")]):
        for nm, f in MF[k].items(): a.plot(X[k], f, label=nm)
        a.set_title(t); a.legend(); a.set_ylim(-0.02, 1.05)
    plt.tight_layout(); plt.savefig("funcoes_pertinencia.png", dpi=110); plt.close()
    fig, ax = plt.subplots(1, len(out), figsize=(17, 3.2), sharey=True)
    for a, (nm, agg, v) in zip(ax, out):
        a.fill_between(risco, agg, alpha=.4); a.axvline(v, color="r"); a.set_title(nm[:9] + f"\nrisco={v:.1f}", fontsize=9)
    plt.tight_layout(); plt.savefig("agregacao_defuzz.png", dpi=110)
    # superfície: risco x (renda, comprometimento) com histórico=5
    Rr, Cc = np.meshgrid(np.linspace(0,40,21), np.linspace(0,100,21))
    Z = np.array([[inferir(r, c, 5)[0] for r in np.linspace(0,40,21)] for c in np.linspace(0,100,21)])
    fig = plt.figure(figsize=(6,5)); a = fig.add_subplot(111, projection="3d")
    a.plot_surface(Rr, Cc, Z, cmap="viridis"); a.set_xlabel("Renda"); a.set_ylabel("Compr."); a.set_zlabel("Risco"); a.set_title("Superfície (histórico=5)")
    plt.savefig("superficie.png", dpi=110)
