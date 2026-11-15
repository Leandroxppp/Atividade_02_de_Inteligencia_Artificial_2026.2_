"""Questão 10 — Rotas de entrega: BFS, DFS, UCS, A* e versão com D e F obrigatórios."""
import heapq
from collections import deque

EDGES = {("A","B"):4,("A","D"):3,("B","C"):5,("B","E"):2,("C","F"):2,("D","E"):4,
         ("D","G"):6,("E","F"):3,("E","H"):5,("F","I"):4,("G","H"):3,("H","I"):2}
G = {}
for (u, v), c in EDGES.items():
    G.setdefault(u, {})[v] = c; G.setdefault(v, {})[u] = c
G = {k: dict(sorted(v.items())) for k, v in sorted(G.items())}          # ordem alfabética
H = dict(A=10,B=8,C=6,D=9,E=6,F=4,G=5,H=2,I=0)
START, GOAL = "A", "I"

def custo(path): return sum(G[a][b] for a, b in zip(path, path[1:]))

def bfs():
    fr, vis, exp = deque([[START]]), {START}, []
    while fr:
        p = fr.popleft(); n = p[-1]; exp.append(n)
        if n == GOAL: return p, exp
        for m in G[n]:
            if m not in vis: vis.add(m); fr.append(p + [m])

def dfs():
    fr, vis, exp = [[START]], set(), []
    while fr:
        p = fr.pop(); n = p[-1]
        if n in vis: continue
        vis.add(n); exp.append(n)
        if n == GOAL: return p, exp
        for m in reversed(list(G[n])):          # empilha ao contrário -> expande em ordem alfabética
            if m not in vis: fr.append(p + [m])

def ucs(trace=False):
    fr, best, exp, c = [(0, START, [START])], {}, [], 0
    while fr:
        g, n, p = heapq.heappop(fr)
        if n in best: continue
        best[n] = g; exp.append(n)
        if trace: print(f"  expande {n}  g={g}")
        if n == GOAL: return p, exp, g
        for m, w in G[n].items():
            if m not in best: heapq.heappush(fr, (g + w, m, p + [m]))

def astar(trace=False):
    fr, best, exp = [(H[START], 0, START, [START])], {}, []
    while fr:
        f, g, n, p = heapq.heappop(fr)
        if n in best and best[n] <= g: continue
        best[n] = g; exp.append(n)
        if trace: print(f"  expande {n}: g={g:>2} h={H[n]:>2} f={f:>2}")
        if n == GOAL: return p, exp, g
        for m, w in G[n].items():
            if m not in best or best[m] > g + w:
                heapq.heappush(fr, (g + w + H[m], g + w, m, p + [m]))
        if trace: print("      fronteira (n:g+h=f):", ", ".join(f"{x[2]}:{x[1]}+{H[x[2]]}={x[0]}" for x in sorted(fr) if x[2] not in best))

def ucs_estendido(must=("D","F"), h=None, trace=False):
    """Estado = (local, frozenset(obrigatórios já visitados)). Objetivo: local==I e visitados==must."""
    h = h or (lambda s: 0)
    ini = (START, frozenset(x for x in must if x == START))
    fr, best, exp = [(h(ini), 0, ini, [START])], {}, []
    while fr:
        f, g, s, p = heapq.heappop(fr)
        if s in best: continue
        best[s] = g; exp.append((s[0], "".join(sorted(s[1]))))
        if trace: print(f"  expande ({s[0]},{{{','.join(sorted(s[1]))}}}) g={g} h={h(s)} f={g + h(s)}")
        if s[0] == GOAL and s[1] == frozenset(must): return p, exp, g
        for m, w in G[s[0]].items():
            ns = (m, s[1] | ({m} & set(must)))
            if ns not in best: heapq.heappush(fr, (g + w + h(ns), g + w, ns, p + [m]))

def heuristica_est(s, must=("D","F")):
    """h(local) original continua admissível e consistente no espaço estendido: faltar D/F só pode aumentar o custo real até o objetivo."""
    return H[s[0]]

if __name__ == "__main__":
    print("Admissibilidade/consistência de h:")
    # custo ótimo real a partir de cada nó (Dijkstra reverso)
    dist = {n: float("inf") for n in G}; dist[GOAL] = 0; pq = [(0, GOAL)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]: continue
        for v, w in G[u].items():
            if d + w < dist[v]: dist[v] = d + w; heapq.heappush(pq, (d + w, v))
    print("  h*(n):", dist)
    print("  admissível:", all(H[n] <= dist[n] for n in G))
    print("  violações de consistência h(n)<=c(n,m)+h(m):",
          [(u, v) for u in G for v, w in G[u].items() if H[u] > w + H[v]])
    p, e = bfs();  print(f"\nBFS : expansão={e}\n      rota={'-'.join(p)} custo={custo(p)}")
    p, e = dfs();  print(f"DFS : expansão={e}\n      rota={'-'.join(p)} custo={custo(p)}")
    print("\nUCS:"); p, e, g = ucs(True); print(f"  rota={'-'.join(p)} custo={g} nós expandidos={len(e)}")
    print("\nA*:");  p, e, g = astar(True); print(f"  rota={'-'.join(p)} custo={g} nós expandidos={len(e)}")
    print("\nVersão com D e F obrigatórios (UCS no espaço estendido):")
    p, e, g = ucs_estendido(trace=False)
    print(f"  rota={'-'.join(p)} custo={g} estados expandidos={len(e)}")
    print("\nA* no espaço estendido (estado = (local, {obrigatórios visitados})):")
    p2, e2, g2 = ucs_estendido(h=heuristica_est, trace=True)
    print(f"  A* c/ h(local): rota={'-'.join(p2)} custo={g2} estados expandidos={len(e2)}")
