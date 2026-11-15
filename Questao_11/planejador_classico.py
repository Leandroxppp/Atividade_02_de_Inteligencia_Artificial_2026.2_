"""Questão 11 — Agente clássico baseado em utilidade para planejar atividades (busca exaustiva em grade de 30 min).
Estado: atribuição de cada slot livre a {A,B,D,ocioso}. Compromisso fixo: C 16h-17h.
Utilidade = Σ (peso_prioridade × fator_urgência) das tarefas concluídas + crédito proporcional ao progresso em tarefas com prazo próximo."""
import itertools, json

SLOT = 30
INICIO, FIM = 14*60, 18*60
TAREFAS = {  # min, prioridade, prazo ('hoje','amanha','semana'), fixa=(início,fim) opcional
 "A": dict(nome="Preparar aula de IA", min=90,  prio="Alta",  prazo="hoje"),
 "B": dict(nome="Corrigir trabalhos",   min=120, prio="Média", prazo="amanha"),
 "C": dict(nome="Reunião de pesquisa",  min=60,  prio="Alta",  prazo="hoje", fixa=(16*60, 17*60)),
 "D": dict(nome="Revisar artigo",       min=60,  prio="Baixa", prazo="semana"),
}
PESO = {"Alta": 10, "Média": 5, "Baixa": 2}; URG = {"hoje": 3, "amanha": 2, "semana": 1}
def valor(t): return PESO[t["prio"]] * URG[t["prazo"]]
hhmm = lambda m: f"{m//60:02d}:{m%60:02d}"

def planejar(tarefas=TAREFAS, permitir_divisao=True, capacidade_amanha_min=240):
    slots = list(range(INICIO, FIM, SLOT))
    fixas = {k: t["fixa"] for k, t in tarefas.items() if "fixa" in t}
    ocupados = {s for a, b in fixas.values() for s in range(a, b, SLOT)}
    livres = [s for s in slots if s not in ocupados]
    moveis = [k for k in tarefas if k not in fixas]
    melhor = None
    for atrib in itertools.product(moveis + [None], repeat=len(livres)):
        por = {k: [s for s, a in zip(livres, atrib) if a == k] for k in moveis}
        ok, u = True, sum(valor(tarefas[k]) for k in fixas)
        for k in moveis:
            t = tarefas[k]; n = len(por[k]); need = t["min"] // SLOT
            if n == 0: continue
            contiguo = all(b - a == SLOT for a, b in zip(por[k], por[k][1:]))
            if not permitir_divisao and not (n == need and contiguo): ok = False; break   # tarefa iniciada deve ser concluída, sem divisão
            if n > need: ok = False; break
            if n == need: u += valor(t)
            else:
                if t["prazo"] == "hoje": ok = False; break                                  # prazo hoje não admite conclusão parcial
                resta = (need - n) * SLOT
                if t["prazo"] == "amanha" and resta > capacidade_amanha_min: ok = False; break
                u += valor(t) * n / need                                                      # crédito proporcional ao progresso
        if not ok: continue
        # desempate: 1º menos tarefas fragmentadas em blocos separados no tempo; 2º menos trocas de tarefa
        frag = sum(1 + sum(1 for a, b in zip(ss, ss[1:]) if b - a != SLOT) - 1 for ss in por.values() if ss)
        trocas = sum(1 for a, b in zip(atrib, atrib[1:]) if a != b)
        chave = (u, -frag, -trocas)
        if melhor is None or chave > melhor[0]: melhor = (chave, por)
    (u, _, _), por = melhor
    agenda = [(a, b, k) for k, (a, b) in fixas.items()]
    for k, ss in por.items():
        i = 0
        while i < len(ss):                                   # junta slots contíguos em blocos
            j = i
            while j + 1 < len(ss) and ss[j+1] - ss[j] == SLOT: j += 1
            agenda.append((ss[i], ss[j] + SLOT, k)); i = j + 1
    agenda.sort()
    return dict(utilidade=u, agenda=agenda, por=por)

def justificar(res, tarefas=TAREFAS):
    linhas = []
    for k, t in tarefas.items():
        feito = sum(b - a for a, b, kk in res["agenda"] if kk == k)
        if feito >= t["min"]: continue
        if feito: linhas.append(f"{k} ({t['nome']}): {feito} de {t['min']} min hoje; restantes {t['min']-feito} min ficam para amanhã (prazo: {t['prazo']}).")
        elif t["prazo"] == "semana": linhas.append(f"{k} ({t['nome']}): adiado — prioridade {t['prio']} e prazo na próxima semana; todo o tempo útil de hoje foi usado em tarefas com prazo mais curto.")
        else: linhas.append(f"{k} ({t['nome']}): não cabe hoje sem violar restrições; reagendar antes de '{t['prazo']}'.")
    return linhas

def mostrar(res, tarefas=TAREFAS):
    for a, b, k in res["agenda"]: print(f"  {hhmm(a)}–{hhmm(b)}  {k} — {tarefas[k]['nome']}")
    print(f"  utilidade = {res['utilidade']:.1f}")
    for l in justificar(res, tarefas): print("  •", l)

if __name__ == "__main__":
    print("Plano SEM divisão de tarefas:"); r1 = planejar(permitir_divisao=False); mostrar(r1)
    print("\nPlano COM divisão permitida (B pode ser feita em partes; capacidade amanhã=240min):"); r2 = planejar(permitir_divisao=True); mostrar(r2)
