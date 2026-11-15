# Questão 10 — Planejamento de rotas para entregas urbanas

Arquivos: `busca.py` (BFS, DFS, UCS, A* e versão estendida), `resultados.txt`. Convenção: vizinhos em ordem alfabética; teste de objetivo na **expansão** (para UCS/A*). *O enunciado diz “Busca em Profundidade (BFS)”: pela sigla e pelo contexto (comparação com UCS), executei **BFS (largura)** e também a **DFS (profundidade)**.*

## 1. Formulação
* **Estados:** localidades {A,B,C,D,E,F,G,H,I} (posição do entregador).
* **Estado inicial:** A. **Teste de objetivo:** estado = I.
* **Ações:** `ir(n)` para cada vizinho n adjacente ao estado atual (grafo não direcionado).
* **Transição:** `resultado(s, ir(n)) = n`. **Custo:** peso da aresta (min); custo do caminho = soma.

## 2. Busca não informada
| Algoritmo | Ordem de expansão | Rota | Custo |
|---|---|---|---:|
| **BFS** | A, B, D, C, E, G, F, H, I | A–B–C–F–I | **15** (4 arestas) |
| **DFS** | A, B, C, F, E, D, G, H, I | A–B–C–F–E–D–G–H–I | **29** |
| **UCS** | A(0), D(3), B(4), E(6), C(9), F(9), G(9), H(11), I(13) | A–B–E–F–I | **13** |

## 3. Busca informada — A*
`f = g + h` (h: A10 B8 C6 D9 E6 F4 G5 H2 I0). Expansões:

| Nó | g | h | f |
|---|---:|---:|---:|
| A | 0 | 10 | 10 |
| D | 3 | 9 | 12 |
| B | 4 | 8 | 12 |
| E | 6 | 6 | 12 |
| F | 9 | 4 | 13 |
| H | 11 | 2 | 13 |
| I | 13 | 0 | 13 |

Fronteira (lista aberta) após cada expansão, formato `nó: g+h=f` (entradas repetidas do mesmo nó são versões antigas, descartadas ao serem retiradas — *lazy deletion*):

| Expandido | Fronteira depois da expansão |
|---|---|
| A | D:3+9=12, B:4+8=12 |
| D | B:4+8=12, E:7+6=13, G:9+5=14 |
| B | E:6+6=12 (melhor caminho a E, via B), E:7+6=13 (via D), G:9+5=14, C:9+6=15 |
| E | F:9+4=13, H:11+2=13, G:9+5=14, C:9+6=15 |
| F | H:11+2=13, I:13+0=13, G:9+5=14, C:9+6=15 |
| H | I:13+0=13, G:9+5=14, C:9+6=15 |
| I | objetivo (f = 13 = custo ótimo) |

Rota: **A–B–E–F–I, custo 13**, com **7 nós expandidos** (a rota A–B–E–H–I também custa 13: há duas rotas ótimas empatadas, e a ordem alfabética de desempate escolhe a primeira) (C e G nunca foram expandidos). Verifiquei que **h é admissível** (h(n) ≤ custo ótimo real: A 13, B 9, C 6, D 11, E 7, F 4, G 5, H 2, I 0) e **consistente** (nenhuma violação).

## 4. Comparação
| | BFS | DFS | UCS | A* |
|---|---|---|---|---|
| Custo da solução | 15 | 29 | **13** | **13** |
| Nós expandidos | 9 | 9 | 9 | **7** |
| Completa? | Sim (finito) | Sim em grafo finito com lista de visitados (não em árvore com ciclos) | Sim (custos > 0) | Sim |
| Ótima? | Só se custos iguais (aqui **não**: 15 > 13) | **Não** | **Sim** | **Sim** (h admissível+consistente) |
| Memória/tempo | O(b^d) | Memória O(b·m) | O(b^(1+C*/ε)) | Menos nós com h boa |

A BFS minimiza **número de arestas** e não o tempo; a DFS devolve um caminho longo (29). A* mantém a otimalidade do UCS expandindo menos nós graças a h.

## 5. Visitar obrigatoriamente D e F antes de I
**Novo estado:** `(local, visitados ⊆ {D,F})`. Inicial `(A, ∅)`. Ações: ir a vizinho; transição atualiza o conjunto se o novo local for D ou F. **Objetivo:** `(I, {D,F})`. Custo: o mesmo.
O espaço passa de 9 a 9×4 = 36 estados. **Rota ótima: A–D–E–F–I, custo 14** (3+4+3+4). A rota ótima sem restrição (A–B–E–F–I, 13) não passa por D; passar por D custa +1 min. O UCS no espaço estendido expandiu 24 estados; o **A\* com h(local)** (continua admissível e consistente, pois exigir paradas obrigatórias só pode aumentar o custo restante) expandiu **14 estados**, com a mesma rota. A representação precisa do conjunto de visitados porque `(E,{D})` e `(E,∅)` são estados diferentes (mesma localidade, mas o que falta cumprir é distinto).

### Trace do A* no espaço estendido (`resultados.txt`)
| # | Estado expandido | g | h | f |
|--:|---|--:|--:|--:|
| 1 | (A,∅) | 0 | 10 | 10 |
| 2 | (D,{D}) | 3 | 9 | 12 |
| 3 | (B,∅) | 4 | 8 | 12 |
| 4 | (E,∅) | 6 | 6 | 12 |
| 5 | (E,{D}) | 7 | 6 | 13 |
| 6 | (F,{F}) | 9 | 4 | 13 |
| 7 | (H,∅) | 11 | 2 | 13 |
| 8 | (I,∅) e (I,{F}) | 13 | 0 | 13 |
| 9 | (G,{D}), (F,{D,F}), (H,{D}) | 9–12 | 5/4/2 | 14 |
| 10 | (I,{D}) e **(I,{D,F}) = objetivo** | 14 | 0 | 14 |

Os estados (I,∅), (I,{F}) e (I,{D}) chegam a I mas **não são objetivo** (faltam D e/ou F), por isso a busca continua com f = 13 → 14. O primeiro estado-objetivo retirado da fronteira é (I,{D,F}) com **f = g = 14**, que é ótimo. Caminho: A→D→E→F→I.

**Observação sobre o enunciado ("Busca em Profundidade (BFS)"):** BFS é largura e DFS é profundidade; foram executadas as duas, e na comparação aparece a DFS como "profundidade". Se o professor quis apenas uma delas, a linha correspondente da tabela vale.
**Teste de objetivo:** BFS testa na expansão, como UCS e A*. Se testasse na geração, a BFS pararia ao gerar I durante a expansão de F (7 expansões em vez de 9: A, B, D, C, E, G, F), sem mudar a rota.
