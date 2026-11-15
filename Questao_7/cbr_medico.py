"""Questão 7 — Sistema de Apoio ao Diagnóstico Baseado em Casos (CBR): Retrieve, Reuse, Revise, Retain.
USO: python cbr_medico.py            -> menu interativo
     python cbr_medico.py --demo     -> demonstração automática (usa cópia da base)
AVISO: casos 100% fictícios, apenas para fins educacionais. Não é ferramenta clínica."""
import json, math, sys, shutil, os
from collections import defaultdict

BASE = "casos.json"
SINTOMAS = ["febre","febre_alta","tosse","tosse_seca","tosse_com_catarro","dor_de_cabeca","dor_muscular","dor_atras_dos_olhos",
            "manchas_na_pele","coriza","espirros","coceira_nos_olhos","falta_de_ar","dor_toracica","perda_olfato_paladar",
            "nausea","vomito","diarreia","dor_abdominal","fadiga","dor_de_garganta","calafrios"]

def carregar(path=BASE): return json.load(open(path, encoding="utf-8"))
def salvar(casos, path=BASE): json.dump(casos, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

def pesos(casos):
    """Peso IDF de cada sintoma: sintomas raros (ex.: perda de olfato) discriminam mais que febre."""
    n = len(casos)
    return {s: math.log((n + 1) / (1 + sum(s in c["sintomas"] for c in casos))) + 1 for s in SINTOMAS}

def similaridade(q, c, w):
    """sim = 0.85 * Jaccard ponderado dos sintomas + 0.10 * sim(idade) + 0.05 * sim(duração)."""
    a, b = set(q["sintomas"]), set(c["sintomas"])
    uni = sum(w.get(s, 1) for s in a | b); inter = sum(w.get(s, 1) for s in a & b)
    sim_s = inter / uni if uni else 0
    sim_i = 1 - min(abs(q.get("idade", c["idade"]) - c["idade"]), 60) / 60
    sim_d = 1 - min(abs(q.get("dias", c["dias"]) - c["dias"]), 10) / 10
    return 0.85 * sim_s + 0.10 * sim_i + 0.05 * sim_d

# ---------------- RETRIEVE ----------------
def recuperar(q, casos, k=3):
    w = pesos(casos)
    return sorted(((similaridade(q, c, w), c) for c in casos), key=lambda t: -t[0])[:k]

# ---------------- REUSE ----------------
def reutilizar(vizinhos):
    """Voto ponderado pela similaridade (ao quadrado, para dar mais peso aos mais próximos)."""
    votos = defaultdict(float)
    for s, c in vizinhos: votos[c["diagnostico"]] += s ** 2
    tot = sum(votos.values()); rank = sorted(votos.items(), key=lambda t: -t[1])
    diag = rank[0][0]
    caso_ref = next(c for s, c in vizinhos if c["diagnostico"] == diag)
    return diag, rank[0][1] / tot, caso_ref["tratamento"], rank

# ---------------- REVISE / RETAIN ----------------
def revisar(diag_sug, diag_confirmado=None, tratamento_corrigido=None, trat_sug=""):
    """O médico confirma ou corrige. Retorna (diagnóstico, tratamento, foi_corrigido)."""
    if diag_confirmado is None or diag_confirmado == diag_sug:
        return diag_sug, tratamento_corrigido or trat_sug, False
    return diag_confirmado, tratamento_corrigido or "(definir tratamento)", True

def reter(casos, query, diag, trat, corrigido, path=BASE):
    novo = {"id": f"C{len(casos)+1:02d}", **query, "diagnostico": diag, "tratamento": trat, "corrigido_na_revisao": corrigido}
    casos.append(novo); salvar(casos, path); return novo

def relatorio(q, casos, k=3):
    viz = recuperar(q, casos, k)
    diag, conf, trat, rank = reutilizar(viz)
    print(f"\nSintomas informados: {', '.join(q['sintomas'])} | idade={q.get('idade','?')} | dias={q.get('dias','?')}")
    print(f"RETRIEVE — {k} casos mais semelhantes:")
    for s, c in viz:
        print(f"  {c['id']} sim={s:.3f}  {c['diagnostico']:<18} sintomas={','.join(c['sintomas'])}")
    print(f"REUSE — diagnóstico sugerido: {diag} (confiança relativa {conf:.0%}); ranking: " + ", ".join(f"{d}={v:.2f}" for d, v in rank))
    print(f"        tratamento associado: {trat}")
    return diag, trat

def demo():
    shutil.copy(BASE, "casos_demo.json"); path = "casos_demo.json"; casos = carregar(path)
    print(f"Base: {len(casos)} casos, {len(set(c['diagnostico'] for c in casos))} doenças")
    consultas = [
      {"sintomas": ["febre_alta","dor_atras_dos_olhos","dor_muscular","manchas_na_pele"], "idade": 30, "dias": 3},
      {"sintomas": ["febre","tosse_seca","perda_olfato_paladar","fadiga"], "idade": 40, "dias": 4},
      {"sintomas": ["coriza","espirros","coceira_nos_olhos"], "idade": 22, "dias": 7},
      {"sintomas": ["febre","tosse","dor_de_cabeca"], "idade": 35, "dias": 2},   # caso ambíguo
    ]
    for q in consultas:
        diag, trat = relatorio(q, casos)
    print("\n--- Ciclo Revise/Retain no caso ambíguo ---")
    q = consultas[3]; diag, trat = relatorio(q, casos)
    print("REVISE — médico corrige o diagnóstico para 'Gripe' após exame clínico.")
    d, t, corr = revisar(diag, "Gripe", "Repouso, hidratação e antitérmico", trat)
    novo = reter(casos, q, d, t, corr, path)
    print(f"RETAIN — caso {novo['id']} salvo (base agora com {len(casos)} casos).")
    print("Reconsulta após aprendizado:"); relatorio(q, casos)
    # leave-one-out
    ok = 0; orig = casos[:-1]          # só os casos originais (sem o C19 retido), tanto como consulta quanto como base de referência
    for i, c in enumerate(orig):
        q = {k: c[k] for k in ("sintomas", "idade", "dias")}
        v = recuperar(q, orig[:i] + orig[i+1:], 3); ok += reutilizar(v)[0] == c["diagnostico"]
    print(f"\nLeave-one-out nos {len(casos)-1} casos originais: {ok}/{len(casos)-1} = {ok/(len(casos)-1):.0%}")
    os.remove(path)

def menu():
    casos = carregar()
    while True:
        print("\n1) Novo diagnóstico  2) Listar casos  0) Sair")
        op = input("> ").strip()
        if op == "0": break
        if op == "2":
            for c in casos: print(c["id"], c["diagnostico"], c["sintomas"])
        if op == "1":
            print("Sintomas disponíveis:", ", ".join(SINTOMAS))
            s = [x.strip() for x in input("Sintomas (separados por vírgula): ").split(",") if x.strip() in SINTOMAS]
            q = {"sintomas": s, "idade": int(input("Idade: ") or 30), "dias": int(input("Dias de sintomas: ") or 3)}
            diag, trat = relatorio(q, casos)
            r = input("REVISE — confirma o diagnóstico? (Enter=sim, ou digite o diagnóstico correto): ").strip()
            d, t, corr = revisar(diag, r or None, None, trat)
            if input("RETAIN — salvar como novo caso? (s/n): ").lower() == "s":
                print("Salvo:", reter(casos, q, d, t, corr)["id"])

if __name__ == "__main__":
    demo() if "--demo" in sys.argv else menu()
