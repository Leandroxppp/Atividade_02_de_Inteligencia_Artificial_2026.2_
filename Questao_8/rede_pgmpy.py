"""Questão 8 — A MESMA rede, construída com pgmpy (inferência por Eliminação de Variáveis) e conferida contra a enumeração própria.
pip install pgmpy   |   USO: python rede_pgmpy.py
NÃO foi executado no ambiente de geração (sem rede para instalar pgmpy): rode e confira que as probabilidades coincidem com resultados.txt (diferença < 1e-6)."""
import itertools
from rede_bayesiana import NET, ORDEM, inferir
try:
    from pgmpy.models import DiscreteBayesianNetwork as BN      # pgmpy >= 1.0
except ImportError:
    from pgmpy.models import BayesianNetwork as BN              # versões antigas
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination

modelo = BN([(p, v) for v in ORDEM for p in NET[v][0]])
for v in ORDEM:
    pais, t = NET[v]
    colunas = list(itertools.product([True, False], repeat=len(pais)))           # 1º pai varia mais devagar (convenção do pgmpy)
    p_sim = [t[c] for c in colunas]
    modelo.add_cpds(TabularCPD(v, 2, [p_sim, [1 - p for p in p_sim]], evidence=list(pais) or None,
                               evidence_card=[2] * len(pais) or None, state_names={x: ["Sim", "Nao"] for x in [v, *pais]}))
assert modelo.check_model()
inf = VariableElimination(modelo)
casos = [{}, {"Febre": "Sim"}, {"Febre": "Sim", "Tosse": "Sim"}, {"Febre": "Sim", "Tosse": "Sim", "Dispneia": "Sim"},
         {"Febre": "Sim", "Tosse": "Sim", "Dispneia": "Sim", "RaioX": "Sim"}, {"Tosse": "Sim", "Fumante": "Sim"}, {"RaioX": "Nao", "Febre": "Sim", "Tosse": "Sim"}]
for ev in casos:
    p_pg = inf.query(["Pneumonia"], evidence=ev, show_progress=False).get_value(Pneumonia="Sim")
    p_me = inferir("Pneumonia", {k: v == "Sim" for k, v in ev.items()})
    print(f"{str(ev):<75} pgmpy={p_pg:.4f}  enumeração={p_me:.4f}  {'OK' if abs(p_pg-p_me) < 1e-6 else 'DIVERGE'}")
