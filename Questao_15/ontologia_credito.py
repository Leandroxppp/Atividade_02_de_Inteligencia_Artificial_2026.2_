"""Questão 15 — Ontologia OWL 2 de risco de crédito (a árvore C4.5 da Lista 1 como axiomas) + raciocínio.
Gera credito.owl para abrir no Protégé (Reasoner > HermiT > Start reasoner). O mini-reasoner abaixo reproduz a classificação para conferência."""
import csv
from owlgen import build, restr

BASE = "http://example.org/credito"
VAL = lambda p, v: restr("has", p, v)
# Classes definidas: nome -> (superclasse, {propriedade: valor})
INV = {"temPatrimonio": "ehPatrimonioDe", "temEmprego": "ehEmpregoDe", "temRenda": "ehRendaDe", "temHistorico": "ehHistoricoDe", "temGarantia": "ehGarantiaDe", "temDivida": "ehDividaDe"}
RULES = {   # base de regras do C4.5 (a ESCOLHIDA na Questão 1 da Lista 1: 5 regras, raiz = Emprego)
 "ClienteEmpregoInstavel":        ("ClienteRiscoAlto",     {"temEmprego": "EmpregoInstavel"}),
 "ClienteEstavelPatrimonioAlto":  ("ClienteRiscoBaixo",    {"temEmprego": "EmpregoEstavel", "temPatrimonio": "PatrimonioAlto"}),
 "ClienteEstavelMedioRendaMedia": ("ClienteRiscoModerado", {"temEmprego": "EmpregoEstavel", "temPatrimonio": "PatrimonioMedio", "temRenda": "Renda15a35k"}),
 "ClienteEstavelMedioRendaAltaHistRuim": ("ClienteRiscoModerado", {"temEmprego": "EmpregoEstavel", "temPatrimonio": "PatrimonioMedio", "temRenda": "RendaMaior35k", "temHistorico": "HistoriaRuim"}),
 "ClienteEstavelMedioRendaAltaBoaHist":  ("ClienteRiscoBaixo",    {"temEmprego": "EmpregoEstavel", "temPatrimonio": "PatrimonioMedio", "temRenda": "RendaMaior35k", "temHistorico": "HistoriaBoa"}),
}
CLASSES = {"Cliente": {}, "ClienteRiscoAlto": {"sub": ["Cliente"]}, "ClienteRiscoModerado": {"sub": ["Cliente", "ClienteElegivel"]}, "ClienteRiscoBaixo": {"sub": ["Cliente", "ClienteElegivel"]},
           "ClienteElegivel": {"sub": ["Cliente"], "comment": "Cliente com risco baixo ou moderado: pode receber crédito (com condições)."},
           "Patrimonio": {}, "Emprego": {}, "Renda": {}, "HistoriaCredito": {}, "Garantia": {}, "Divida": {}}
for n, (sup, cond) in RULES.items():
    CLASSES[n] = {"sub": [sup], "equiv": ["Cliente"] + [VAL(p, v) for p, v in cond.items()]}
OBJ = {p: dict(dom="Cliente", ran=r, func=True, inv=INV[p]) for p, r in
       [("temPatrimonio","Patrimonio"),("temEmprego","Emprego"),("temRenda","Renda"),("temHistorico","HistoriaCredito"),("temGarantia","Garantia"),("temDivida","Divida")]}
for _p, _inv in INV.items():   # propriedades inversas (permitem descobrir relações implícitas: PatrimonioBaixo ehPatrimonioDe E1)
    OBJ[_inv] = dict(dom=OBJ[_p]["ran"], ran="Cliente", inv=_p)
DATA = {"identificador": dict(dom="Cliente", ran="string")}
DISJ = [["ClienteRiscoAlto", "ClienteRiscoModerado", "ClienteRiscoBaixo"], ["Patrimonio", "Emprego", "Renda", "HistoriaCredito", "Garantia", "Divida"]]

MAP = {"Historia_Credito": ("temHistorico", {"Boa": "HistoriaBoa", "Ruim": "HistoriaRuim", "Desconhecida": "HistoriaDesconhecida"}),
       "Divida": ("temDivida", {"Alta": "DividaAlta", "Baixa": "DividaBaixa"}), "Garantia": ("temGarantia", {"Nenhuma": "GarantiaNenhuma", "Adequada": "GarantiaAdequada"}),
       "Renda": ("temRenda", {"0-15k": "Renda0a15k", "15-35k": "Renda15a35k", ">35k": "RendaMaior35k"}),
       "Emprego": ("temEmprego", {"Estavel": "EmpregoEstavel", "Instavel": "EmpregoInstavel"}), "Patrimonio": ("temPatrimonio", {"Baixo": "PatrimonioBaixo", "Medio": "PatrimonioMedio", "Alto": "PatrimonioAlto"})}
IND, ROT = {}, {}
for attr, (prop, m) in MAP.items():
    cls = {"Historia_Credito": "HistoriaCredito"}.get(attr, attr)
    for v in m.values(): IND[v] = dict(types=[cls])
for r in csv.DictReader(open("risco_credito_ampliado.csv", encoding="utf-8")):
    IND[r["Exemplo"]] = dict(types=["Cliente"], obj={MAP[a][0]: [MAP[a][1][r[a]]] for a in MAP}, data=dict(identificador=(r["Exemplo"], "string")))
    ROT[r["Exemplo"]] = "ClienteRisco" + {"Alto": "Alto", "Moderado": "Moderado", "Baixo": "Baixo"}[r["Risco"]]

def classificar(ind):
    """Para cada Cliente, devolve as classes de risco inferidas (via classes definidas + subclasse)."""
    out = {}
    for n, i in ind.items():
        if "Cliente" not in i["types"]: continue
        got = {sup for _, (sup, cond) in RULES.items() if all(v in i["obj"].get(p, []) for p, v in cond.items())}
        out[n] = got
    return out

if __name__ == "__main__":
    open("credito.owl", "w", encoding="utf-8").write(build(BASE, CLASSES, OBJ, DATA, IND, DISJ))
    res = classificar(IND)
    ok = sum(res[n] == {ROT[n]} for n in res); nc = [n for n in res if not res[n]]; mult = [n for n in res if len(res[n]) > 1]
    print(f"credito.owl gerado: {len(CLASSES)} classes, {len(OBJ)+len(DATA)} propriedades, {len(IND)} indivíduos")
    print(f"Classificação correta: {ok}/{len(res)} | não classificados (mundo aberto): {nc} | classificações múltiplas (inconsistência): {mult}")
    for n in res:
        if res[n] != {ROT[n]}: print("  divergência", n, "inferido:", res[n], "esperado:", ROT[n])
    # Demonstração de inconsistência: cliente com Patrimonio Baixo declarado também como RiscoBaixo
    bad = dict(IND); bad["EX"] = dict(types=["Cliente", "ClienteRiscoBaixo"], obj=dict(temEmprego=["EmpregoInstavel"]))
    r = classificar(bad)["EX"]
    print("\nCliente EX asserido ClienteRiscoBaixo com EmpregoInstavel -> inferido também", r, "=> classes disjuntas => INCONSISTENTE (HermiT acusaria)")
    # Novo cliente (inferência de uma instância nova)
    # Inferência em cadeia: classe definida -> classe de risco -> ClienteElegivel (subclasse) ; e relações inversas
    elegiveis = sorted(n for n, c in res.items() if c & {"ClienteRiscoBaixo", "ClienteRiscoModerado"})
    print(f"\nInferência em cadeia (definida -> risco -> ClienteElegivel): {len(elegiveis)} elegíveis de {len(res)}; não elegíveis (RiscoAlto): {sorted(set(res)-set(elegiveis))}")
    inv = {}
    for n, i in IND.items():
        for pr, vs in i.get("obj", {}).items():
            for v in vs: inv.setdefault((v, INV[pr]), []).append(n)
    print("Relação implícita via inversa: EmpregoInstavel ehEmpregoDe", inv[("EmpregoInstavel", "ehEmpregoDe")])
    novo = dict(IND); novo["NOVO"] = dict(types=["Cliente"], obj=dict(temPatrimonio=["PatrimonioMedio"], temEmprego=["EmpregoEstavel"], temRenda=["Renda15a35k"], temHistorico=["HistoriaRuim"]))
    print("NOVO (Medio, Estavel, 15-35k, Ruim) ->", classificar(novo)["NOVO"])
    novo["N2"] = dict(types=["Cliente"], obj=dict(temPatrimonio=["PatrimonioMedio"], temEmprego=["EmpregoEstavel"], temRenda=["RendaMaior35k"], temHistorico=["HistoriaDesconhecida"]))
    print("N2 (Medio, Estavel, >35k, Desconhecida) ->", classificar(novo)["N2"] or "nenhuma classe inferida (mundo aberto: a ontologia não afirma nada)")
    novo["N3"] = dict(types=["Cliente"], obj=dict(temPatrimonio=["PatrimonioBaixo"], temEmprego=["EmpregoEstavel"], temRenda=["Renda15a35k"], temHistorico=["HistoriaBoa"]))
    print("N3 (Baixo, Estavel, 15-35k, Boa) ->", classificar(novo)["N3"] or "nenhuma classe inferida (a base da Lista 1 não tem Estável+Patrimônio Baixo: a árvore C4.5 não cobre este caso)")
