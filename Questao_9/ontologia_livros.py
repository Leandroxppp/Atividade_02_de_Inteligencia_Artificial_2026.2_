"""Questão 9 — Sistema de recomendação de livros baseado em ontologia OWL 2.
1) Gera livros.owl (abra no Protégé e rode HermiT/Pellet para conferir).
2) Mini-reasoner em Python (subclasses, inversas, transitividade, classes definidas, consistência) p/ rodar sem Java.
3) Recomendador com justificativa. Títulos/autores são fictícios."""
import re, sys
from owlgen import build, restr, inter

BASE = "http://example.org/livros"
# ----------------------------- TBox -----------------------------
CLASSES = {
 "Pessoa": {}, "Autor": {"sub": ["Pessoa"]}, "Leitor": {"sub": ["Pessoa"]},
 "Livro": {}, "LivroTecnico": {"sub": ["Livro"]}, "LivroFiccao": {"sub": ["Livro"]}, "LivroDidatico": {"sub": ["LivroTecnico"]},
 "Editora": {}, "Genero": {}, "Tema": {}, "Nivel": {}, "Idioma": {},
 # classes definidas (inferência automática de classificação)
 "LivroCurto":       {"equiv": ["Livro", restr("dmax", "numPaginas", 250, "integer")], "comment": "Livros com até 250 páginas"},
 "LivroIniciante":   {"equiv": ["Livro", restr("has", "temNivel", "Iniciante")]},
 "LivroDeIA":        {"equiv": ["Livro", restr("has", "abordaTema", "InteligenciaArtificial")]},
 "LivroBemAvaliado": {"equiv": ["Livro", restr("dmin", "nota", 4.5, "decimal")], "comment": "nota >= 4.5"},
 "LeituraRapidaParaIniciante": {"equiv": ["LivroCurto", "LivroIniciante"]},
 "LeitorIniciante":  {"equiv": ["Leitor", restr("has", "temNivelLeitura", "Iniciante")]},
}
OBJ = {
 "escritoPor": dict(dom="Livro", ran="Autor", inv="escreveu"), "escreveu": dict(dom="Autor", ran="Livro", inv="escritoPor"),
 "publicadoPor": dict(dom="Livro", ran="Editora", func=True), "temGenero": dict(dom="Livro", ran="Genero"),
 "abordaTema": dict(dom="Livro", ran="Tema"), "temNivel": dict(dom="Livro", ran="Nivel", func=True),
 "escritoEmIdioma": dict(dom="Livro", ran="Idioma", func=True), "ehPrerequisitoDe": dict(dom="Livro", ran="Livro", trans=True),
 "interessadoEm": dict(dom="Leitor", ran="Tema"), "prefereIdioma": dict(dom="Leitor", ran="Idioma"),
 "temNivelLeitura": dict(dom="Leitor", ran="Nivel", func=True), "jaLeu": dict(dom="Leitor", ran="Livro"),
}
DATA = {"titulo": dict(dom="Livro", ran="string"), "numPaginas": dict(dom="Livro", ran="integer"), "anoPublicacao": dict(dom="Livro", ran="integer"),
        "nota": dict(dom="Livro", ran="decimal"), "nome": dict(dom="Pessoa", ran="string"), "preco": dict(dom="Livro", ran="decimal")}
DISJ = [["LivroTecnico", "LivroFiccao"], ["Livro", "Pessoa", "Editora", "Genero", "Tema", "Nivel", "Idioma"]]

# ----------------------------- ABox -----------------------------
def L(id_, tit, tipo, pag, ano, nota, preco, autor, ed, gen, temas, nivel, idioma="Portugues", prereq=()):
    return id_, dict(types=[tipo], obj=dict(escritoPor=[autor], publicadoPor=[ed], temGenero=[gen], abordaTema=temas, temNivel=[nivel],
           escritoEmIdioma=[idioma], ehPrerequisitoDe=list(prereq)),
           data=dict(titulo=(tit, "string"), numPaginas=(pag, "integer"), anoPublicacao=(ano, "integer"), nota=(nota, "decimal"), preco=(preco, "decimal")))
IND = dict([
 L("L01","Introdução à Inteligência Artificial","LivroDidatico",320,2021,4.6,89.9,"AutorSilva","EditoraNova","Computacao",["InteligenciaArtificial","Algoritmos"],"Iniciante",prereq=["L02","L05"]),
 L("L02","Aprendizado de Máquina na Prática","LivroTecnico",280,2022,4.4,95.0,"AutorSilva","EditoraNova","Computacao",["InteligenciaArtificial","CienciaDeDados"],"Intermediario",prereq=["L03"]),
 L("L03","Redes Neurais Profundas","LivroTecnico",410,2023,4.8,120.0,"AutorLima","EditoraAlfa","Computacao",["InteligenciaArtificial","RedesNeurais"],"Avancado"),
 L("L04","Python para Iniciantes","LivroDidatico",210,2020,4.5,59.9,"AutorCosta","EditoraNova","Computacao",["Programacao"],"Iniciante",prereq=["L02"]),
 L("L05","Estruturas de Dados Essenciais","LivroDidatico",240,2019,4.2,70.0,"AutorCosta","EditoraAlfa","Computacao",["Algoritmos","Programacao"],"Iniciante"),
 L("L06","Estatística para Ciência de Dados","LivroTecnico",350,2021,4.3,99.0,"AutorMendes","EditoraAlfa","Matematica",["CienciaDeDados","Estatistica"],"Intermediario"),
 L("L07","IA em Quadrinhos: Uma Aventura","LivroTecnico",120,2022,4.7,45.0,"AutorLima","EditoraBeta","Computacao",["InteligenciaArtificial"],"Iniciante"),
 L("L08","O Último Algoritmo","LivroFiccao",300,2018,4.1,49.9,"AutorRocha","EditoraBeta","FiccaoCientifica",["InteligenciaArtificial"],"Iniciante"),
 L("L09","Inteligência Artificial Ética","LivroTecnico",190,2024,4.6,65.0,"AutorMendes","EditoraBeta","Filosofia",["InteligenciaArtificial","Etica"],"Intermediario"),
 L("L10","Machine Learning Fundamentals (EN)","LivroTecnico",260,2020,4.5,110.0,"AutorWang","EditoraAlfa","Computacao",["InteligenciaArtificial","CienciaDeDados"],"Intermediario",idioma="Ingles"),
 L("L11","Bancos de Dados Relacionais","LivroDidatico",380,2017,4.0,80.0,"AutorCosta","EditoraNova","Computacao",["BancosDeDados"],"Intermediario"),
 L("L12","Fundamentos de Lógica","LivroDidatico",150,2016,3.9,40.0,"AutorMendes","EditoraNova","Matematica",["Logica","Algoritmos"],"Iniciante"),
])
for n in ["AutorSilva","AutorLima","AutorCosta","AutorMendes","AutorRocha","AutorWang"]: IND[n] = dict(types=["Autor"], data=dict(nome=(n[5:], "string")))
for n in ["EditoraNova","EditoraAlfa","EditoraBeta"]: IND[n] = dict(types=["Editora"])
for n in ["Computacao","Matematica","FiccaoCientifica","Filosofia"]: IND[n] = dict(types=["Genero"])
for n in ["InteligenciaArtificial","Algoritmos","CienciaDeDados","RedesNeurais","Programacao","Estatistica","Etica","BancosDeDados","Logica"]: IND[n] = dict(types=["Tema"])
for n in ["Iniciante","Intermediario","Avancado"]: IND[n] = dict(types=["Nivel"])
for n in ["Portugues","Ingles"]: IND[n] = dict(types=["Idioma"])
IND["Ana"]   = dict(types=["Leitor"], obj=dict(interessadoEm=["InteligenciaArtificial","Programacao"], prefereIdioma=["Portugues"], temNivelLeitura=["Iniciante"], jaLeu=["L04"]), data=dict(nome=("Ana","string")))
IND["Bruno"] = dict(types=["Leitor"], obj=dict(interessadoEm=["CienciaDeDados","InteligenciaArtificial"], prefereIdioma=["Portugues","Ingles"], temNivelLeitura=["Intermediario"], jaLeu=["L01","L05"]), data=dict(nome=("Bruno","string")))
IND["Carla"] = dict(types=["Leitor"], obj=dict(interessadoEm=["Etica","Logica"], prefereIdioma=["Portugues"], temNivelLeitura=["Iniciante"]), data=dict(nome=("Carla","string")))

# ----------------------------- Reasoner mínimo -----------------------------
NIVEL = {"Iniciante": 0, "Intermediario": 1, "Avancado": 2}
def raciocinar(ind, verbose=True):
    log, ind = [], {k: {"types": set(v.get("types", [])), "obj": {p: set(x) for p, x in v.get("obj", {}).items()}, "data": v.get("data", {})} for k, v in ind.items()}
    sup = {c: set(d.get("sub", [])) for c, d in CLASSES.items()}
    def ancestors(c, seen=None):
        seen = seen or set()
        for p in sup.get(c, ()):
            if p not in seen: seen.add(p); ancestors(p, seen)
        return seen
    # 1) subclasses
    for n, i in ind.items():
        for t in list(i["types"]):
            for a in ancestors(t):
                if a not in i["types"]: i["types"].add(a); log.append(f"{n} : {a}   (subclasse: {t} ⊑ {a})")
    # 2) inversas
    for n, i in ind.items():
        for p, vs in list(i["obj"].items()):
            inv = OBJ[p].get("inv")
            if inv:
                for v in vs:
                    if n not in ind[v]["obj"].setdefault(inv, set()): ind[v]["obj"][inv].add(n); log.append(f"{v} {inv} {n}   (inversa de {p})")
    # 3) transitividade de ehPrerequisitoDe
    ch = True
    while ch:
        ch = False
        for n, i in ind.items():
            for m in list(i["obj"].get("ehPrerequisitoDe", ())):
                for k in ind[m]["obj"].get("ehPrerequisitoDe", ()):
                    if k not in i["obj"]["ehPrerequisitoDe"]: i["obj"]["ehPrerequisitoDe"].add(k); ch = True; log.append(f"{n} ehPrerequisitoDe {k}   (transitividade via {m})")
    # 4) classes definidas
    def has(i, p, v): return v in i["obj"].get(p, ())
    for n, i in ind.items():
        t = i["types"]
        if "Livro" in t:
            if i["data"]["numPaginas"][0] <= 250: i["types"].add("LivroCurto"); log.append(f"{n} : LivroCurto   (numPaginas={i['data']['numPaginas'][0]} ≤ 250)")
            if has(i, "temNivel", "Iniciante"): i["types"].add("LivroIniciante"); log.append(f"{n} : LivroIniciante")
            if has(i, "abordaTema", "InteligenciaArtificial"): i["types"].add("LivroDeIA"); log.append(f"{n} : LivroDeIA")
            if float(i["data"]["nota"][0]) >= 4.5: i["types"].add("LivroBemAvaliado"); log.append(f"{n} : LivroBemAvaliado   (nota={i['data']['nota'][0]})")
            if {"LivroCurto", "LivroIniciante"} <= i["types"]: i["types"].add("LeituraRapidaParaIniciante"); log.append(f"{n} : LeituraRapidaParaIniciante")
        if "Leitor" in t and has(i, "temNivelLeitura", "Iniciante"): i["types"].add("LeitorIniciante"); log.append(f"{n} : LeitorIniciante")
    # 5) consistência
    erros = []
    for n, i in ind.items():
        for a, b in [DISJ[0]]:
            if a in i["types"] and b in i["types"]: erros.append(f"{n} pertence a classes disjuntas {a} e {b}")
        for p, d in OBJ.items():
            if d.get("func") and len(i["obj"].get(p, ())) > 1: erros.append(f"{n}: propriedade funcional {p} com {len(i['obj'][p])} valores")
    return ind, log, erros

# ----------------------------- Recomendador -----------------------------
def recomendar(leitor, ind, top=3):
    L_ = ind[leitor]; res = []
    for n, b in ind.items():
        if "Livro" not in b["types"] or n in L_["obj"].get("jaLeu", ()): continue
        temas = b["obj"]["abordaTema"] & L_["obj"]["interessadoEm"]; idioma_ok = b["obj"]["escritoEmIdioma"] <= L_["obj"]["prefereIdioma"]
        nivel_b = NIVEL[next(iter(b["obj"]["temNivel"]))]; nivel_l = NIVEL[next(iter(L_["obj"]["temNivelLeitura"]))]
        if not temas or not idioma_ok or nivel_b > nivel_l + 1: continue
        sc = 3*len(temas) + float(b["data"]["nota"][0]) + (1.0 if nivel_b == nivel_l else 0) + (0.5 if "LivroCurto" in b["types"] else 0) - (1.5 if nivel_b == nivel_l + 1 else 0)
        just = [f"aborda {', '.join(sorted(temas))} (interesse do leitor)", f"nível {next(iter(b['obj']['temNivel']))}", f"nota {b['data']['nota'][0]}"]
        for c in ("LivroCurto", "LeituraRapidaParaIniciante", "LivroBemAvaliado"):
            if c in b["types"]: just.append(f"classificado pelo reasoner como {c}")
        pre = [p for p, x in ind.items() if "Livro" in x["types"] and n in x["obj"].get("ehPrerequisitoDe", ()) and p not in L_["obj"].get("jaLeu", ())]
        if pre: just.append("⚠ pré-requisito(s) ainda não lidos: " + ", ".join(f"{p} ({ind[p]['data']['titulo'][0]})" for p in pre))
        res.append((sc, n, b["data"]["titulo"][0], just))
    return sorted(res, reverse=True)[:top]

if __name__ == "__main__":
    xml = build(BASE, CLASSES, OBJ, DATA, IND, DISJ)
    open("livros.owl", "w", encoding="utf-8").write(xml)
    print(f"livros.owl gerado: {len(CLASSES)} classes, {len(OBJ)} propriedades de objeto + {len(DATA)} de dados = {len(OBJ)+len(DATA)} propriedades, {len(IND)} indivíduos")
    ind, log, erros = raciocinar(IND)
    print("\n== Consistência ==", "CONSISTENTE" if not erros else erros)
    print(f"\n== {len(log)} fatos inferidos (amostra) ==")
    for l in log[:6] + [x for x in log if "LeituraRapida" in x or "transitividade" in x or "inversa" in x][:8]: print("  ", l)
    print("\n== Classificação automática de indivíduos ==")
    for c in ("LivroCurto", "LeituraRapidaParaIniciante", "LivroBemAvaliado", "LivroDeIA", "LeitorIniciante"):
        print(f"  {c}: {sorted(n for n, i in ind.items() if c in i['types'])}")
    for u in ("Ana", "Bruno", "Carla"):
        print(f"\n== Recomendações para {u} (interesses: {sorted(IND[u]['obj']['interessadoEm'])}; nível: {IND[u]['obj']['temNivelLeitura'][0]}) ==")
        for sc, n, t, j in recomendar(u, ind): print(f"  {sc:5.2f}  {n} {t}\n         - " + "\n         - ".join(j))
    # teste de inconsistência
    bad = dict(IND); bad["LX"] = dict(types=["LivroTecnico", "LivroFiccao"], obj=dict(abordaTema=["Logica"]), data=dict(numPaginas=(100,"integer"), nota=(4.0,"decimal"), titulo=("Teste","string")))
    print("\n== Teste de inconsistência (indivíduo LX ∈ LivroTecnico ⊓ LivroFiccao) ==", raciocinar(bad)[2])
