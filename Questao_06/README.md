# Questão 6 — Sistema fuzzy de Mamdani: risco de crédito

Arquivos: `fuzzy_credito.py`, `fuzzy_skfuzzy.py`, `resultados.txt`, `funcoes_pertinencia.png`, `agregacao_defuzz.png`, `superficie.png`.
**Ferramentas:** (1) `fuzzy_credito.py` — Mamdani em **NumPy** com as mesmas operações do scikit-fuzzy (`trimf`, `trapmf`, `interp_membership`, centroide); **executado**, gera `resultados.txt` e as figuras. (2) `fuzzy_skfuzzy.py` — o **mesmo sistema com scikit-fuzzy** (`fuzz` + `ctrl.ControlSystemSimulation`), reaproveitando a base de regras e comparando com o NumPy. **Este segundo script foi executado** (scikit-fuzzy 0.5.0; saída em `skfuzzy_real.txt`) e os centroides coincidem com os do NumPy (A: 14,8 × 15,0; B: 50,0 × 50,0; C: 86,8 × 86,7; D: 50,0 × 50,0; E: 33,3 × 33,4 — diferença ≤ 0,2 por discretização do universo).

## 1. Aplicação e modelagem
Continuidade da Lista 1: estimar o **risco de crédito** de um cliente (0–100) a partir de três variáveis de entrada.

| Variável | Tipo | Universo | Termos linguísticos (função de pertinência) |
|---|---|---|---|
| Renda (mil R$/mês) | entrada | [0, 40] | baixa (trapezoidal 0,0,8,16), média (triangular 10,22,34), alta (trapezoidal 28,35,40,40) |
| Comprometimento (% da renda em dívidas) | entrada | [0, 100] | baixo (0,0,15,35), médio (25,45,65), alto (55,75,100,100) |
| Histórico de crédito (score) | entrada | [0, 10] | ruim (0,0,2,4.5), regular (3,5.5,8), bom (6.5,8.5,10,10) |
| Risco | saída | [0, 100] | baixo (0,0,15,35), moderado (25,50,75), alto (65,85,100,100) |

Funções triangulares/trapezoidais por simplicidade e interpretabilidade; **sobreposição** entre termos vizinhos (ex.: renda 10–16) garante a transição gradual. Veja `funcoes_pertinencia.png`.

## 2. Base de regras (15 regras; AND = mínimo)
| # | Renda | Compr. | Hist. | → Risco | | # | Renda | Compr. | Hist. | → Risco |
|--:|---|---|---|---|---|--:|---|---|---|---|
| R1 | alta | – | bom | baixo | | R9 | média | alto | regular | alto |
| R2 | alta | baixo | – | baixo | | R10 | média | alto | **bom** | **moderado** |
| R3 | média | baixo | bom | baixo | | R11 | alta | alto | bom | moderado |
| R4 | média | médio | regular | moderado | | R12 | baixa | alto | – | alto |
| R5 | média | baixo | regular | moderado | | R13 | baixa | – | ruim | alto |
| R6 | alta | alto | regular | moderado | | R14 | – | – | ruim | alto |
| R7 | baixa | baixo | bom | moderado | | R15 | baixa | médio | – | alto |
| R8 | – | médio | bom | moderado | | | | | | |

"–" = antecedente ignorado (grau 1). **Correção em relação à versão anterior:** a antiga R9 ("renda média E comprometimento alto ⇒ alto") ignorava o histórico e classificava como risco alto o cliente D, que tem bom histórico. Ela foi restringida a histórico regular e foram acrescentadas **R10 e R11**, em que o bom histórico atenua o endividamento alto. Regras por *senso de especialista*: com a Lista 1 (dados categóricos) não há como calibrá-las numericamente; ver limitações.

## 3. Inferência de Mamdani (passo a passo)
1. **Fuzzificação:** valores nítidos → graus de pertinência (`interp_membership`).
2. **Avaliação dos antecedentes:** conectivo E = **mínimo**; antecedente ausente = 1.
3. **Implicação:** corta (mínimo) a função de pertinência do consequente na força da regra.
4. **Agregação:** união (**máximo**) dos consequentes cortados.
5. **Defuzzificação:** **centroide** `z* = Σ z·μ(z) / Σ μ(z)` (comparado com bisetriz e média dos máximos).

**Exemplo (Cliente B: renda 20k, comprometimento 45%, histórico 5):** renda → média 0,83; comprometimento → médio 1,0; histórico → regular 0,8. Só R4 dispara com w = min(0,83; 1; 0,8) = **0,80**; o consequente "moderado" é cortado em 0,8 e o centroide dá **50,0 → MODERADO**.

**Exemplo (Cliente D: 22k, 70%, histórico 8):** comprometimento → alto 0,75; histórico → bom 0,75; renda → média 1,0. Dispara **R10** com w = 0,75 ("moderado" cortado em 0,75), centroide = **50,0 → MODERADO**. Com a base antiga (R9 sem histórico) o resultado era 85,8 (ALTO): a correção muda a decisão.

## 4. Resultados (de `resultados.txt`)
| Cliente | Renda | Compr. | Hist. | Regras ativas | Centroide | Bisetriz | M. máx. | Classe |
|---|---:|---:|---:|---|---:|---:|---:|---|
| A | 32 | 12% | 9 | R1, R2, R3 | 15,0 | 15,0 | 12,0 | Baixo |
| B | 20 | 45% | 5 | R4 | 50,0 | 50,0 | 50,0 | Moderado |
| C | 6 | 80% | 1,5 | R12, R13, R14 | 86,7 | 87,5 | 92,2 | Alto |
| D | 22 | 70% | 8 | R10 | 50,0 | 50,0 | 50,0 | Moderado |
| E | 36 | 70% | 8 | R1 e R11 (conflito) | 33,4 | 35,0 | 25,5 | Moderado (fronteira com Baixo) |

Figuras: `funcoes_pertinencia.png` (fuzzificação), `agregacao_defuzz.png` (agregação + centroide de cada cliente), `superficie.png` (risco × renda × comprometimento, histórico = 5).

## 5. Discussão
* Saídas **graduais** e interpretáveis; o cliente E mostra duas regras em conflito (R1 pede "baixo", R11 pede "moderado") e o centroide devolve um valor intermediário na fronteira — comportamento típico de Mamdani.
* **Escolha do defuzzificador:** centroide, bisetriz e média dos máximos concordam nos casos de uma só regra; divergem quando há regras conflitantes (cliente E: 33,4 / 35,0 / 25,5). A média dos máximos é descontínua e pouco estável; o centroide é suave, por isso foi o escolhido.
* O centroide com termos saturados **nunca chega a exatamente 0 ou 100** (A = 15,0; C = 86,7), efeito conhecido.
* **Limitações:** funções e regras definidas por conhecimento especialista (não aprendidas); universos e quebras (ex.: 15k, 35k) vêm da discretização da Lista 1. Melhoria: calibrar pertinências com dados reais (ANFIS ou otimização por algoritmo genético) e validar com especialista de crédito.
