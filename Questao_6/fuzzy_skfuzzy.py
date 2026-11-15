"""Questão 6 — MESMO sistema Mamdani, agora com scikit-fuzzy (fuzz + ctrl).
pip install scikit-fuzzy matplotlib numpy   |   USO: python fuzzy_skfuzzy.py
NÃO foi executado no ambiente de geração (sem rede para instalar scikit-fuzzy): rode e compare com resultados.txt
(a versão em NumPy de fuzzy_credito.py já foi executada e serve de referência; os valores devem coincidir ~±0,5)."""
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import fuzzy_credito as ref   # reaproveita só a base de regras R para garantir o mesmo conhecimento

renda = ctrl.Antecedent(np.arange(0, 40.01, 0.1), "renda")
comp  = ctrl.Antecedent(np.arange(0, 100.01, 0.5), "comp")
hist  = ctrl.Antecedent(np.arange(0, 10.01, 0.05), "hist")
risco = ctrl.Consequent(np.arange(0, 100.01, 0.5), "risco", defuzzify_method="centroid")

renda["baixa"] = fuzz.trapmf(renda.universe, [0, 0, 8, 16]); renda["media"] = fuzz.trimf(renda.universe, [10, 22, 34]); renda["alta"] = fuzz.trapmf(renda.universe, [28, 35, 40, 40])
comp["baixo"] = fuzz.trapmf(comp.universe, [0, 0, 15, 35]);  comp["medio"] = fuzz.trimf(comp.universe, [25, 45, 65]);   comp["alto"] = fuzz.trapmf(comp.universe, [55, 75, 100, 100])
hist["ruim"] = fuzz.trapmf(hist.universe, [0, 0, 2, 4.5]);   hist["regular"] = fuzz.trimf(hist.universe, [3, 5.5, 8]);   hist["bom"] = fuzz.trapmf(hist.universe, [6.5, 8.5, 10, 10])
risco["baixo"] = fuzz.trapmf(risco.universe, [0, 0, 15, 35]); risco["moderado"] = fuzz.trimf(risco.universe, [25, 50, 75]); risco["alto"] = fuzz.trapmf(risco.universe, [65, 85, 100, 100])

regras = []
for r, c, h, out in ref.R:
    ant = None
    for var, termo in ((renda, r), (comp, c), (hist, h)):
        if termo: ant = var[termo] if ant is None else (ant & var[termo])   # AND = mínimo
    regras.append(ctrl.Rule(ant, risco[out]))

sistema = ctrl.ControlSystemSimulation(ctrl.ControlSystem(regras))
for nome, (a, b, c) in {"A": (32, 12, 9), "B": (20, 45, 5), "C": (6, 80, 1.5), "D": (22, 70, 8), "E": (36, 70, 8)}.items():
    sistema.input["renda"], sistema.input["comp"], sistema.input["hist"] = a, b, c
    sistema.compute()
    print(f"Cliente {nome}: risco(skfuzzy, centroide) = {sistema.output['risco']:.1f}  | NumPy: {ref.inferir(a, b, c)[0]:.1f}")
