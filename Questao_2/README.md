# Questão 2 — KNN sobre a base de 30 instâncias (risco de crédito, Lista 1)

Arquivos: `knn.py` (código), `risco_credito_ampliado.csv` (base), `resultados.txt` (saída). Execução: `python knn.py`.

## Como o KNN funciona
KNN é um **aprendizado baseado em instâncias (preguiçoso)**: não constrói modelo; guarda os exemplos e, para classificar um novo caso `x`:
1. mede a **distância** de `x` a todos os exemplos;
2. seleciona os **k mais próximos**;
3. a classe prevista é a **votação** dos vizinhos (aqui ponderada por `1/(1+d)`).

**Distância usada:** todos os 6 atributos são categóricos, então uso a **distância de sobreposição (Hamming)**: `d(x,y) = nº de atributos em que x e y diferem` (0 = idênticos, 6 = totalmente diferentes). Variante: **Hamming ponderada pelo ganho de informação** de cada atributo (calculado na Lista 1: Patrimônio 1,263; Renda 0,973; Emprego 0,948; Histórico 0,328; Garantia 0,288; Dívida 0,154).

## Exemplo trabalhado (k = 3)
Novo cliente: `Historia=Boa, Divida=Alta, Garantia=Nenhuma, Renda=15-35k, Emprego=Estavel, Patrimonio=Medio`.

| Vizinho | Distância | Classe |
|---|---|---|
| E12 | 0 | Moderado |
| E30 | 0 | Moderado |
| E18 | 1 (Dívida: Baixa×Alta) | Moderado |

Votos: Moderado = 1 + 1 + 0,5 = 2,5 → **Risco previsto = Moderado**. (Os seguintes, a distância 2, seriam E13 Baixo, E22 Moderado, E26 Alto, E3 Moderado.)

Segundo caso: `Ruim, Baixa, Adequada, >35k, Estavel, Medio` → vizinhos E24 (0, Moderado), E8 (0, Moderado), E19 (1, Baixo) → **Moderado** (votos 2,0 contra 0,5). O caso difere de E19 (Baixo) **apenas no histórico** (Ruim × Boa), o que mostra o peso do histórico: com histórico ruim, o voto vai para Moderado.

**Atenção:** os dois casos acima têm cópia (quase) exata na base (E12/E30 e E8/E24), então são exemplos fáceis. O caso seguinte **não existe na base**.

## Terceiro caso (sem cópia na base), com as 30 distâncias
Novo cliente: `Boa, Baixa, Adequada, 15-35k, Instavel, Medio`. Distâncias de overlap às 30 instâncias (ordenadas; lista completa em `resultados.txt`):

| Posição | ID | Dist. | Classe |
|---:|---|---:|---|
| 1 | E22 | 1 | Moderado |
| 2–5 | E17, E18, E19, E29 | 2 | Moderado, Moderado, **Baixo**, Moderado |
| 6–11 | E12, E15, E24, E26, E3, E30 | 3 | Moderado, Baixo, Moderado, Alto, Moderado, Moderado |
| … | demais (E10…E7) | 3–6 | – |

Com **k=3** os vizinhos são E22 (d=1), E17 e E18 (d=2; E19 e E29 também têm d=2 e ficam de fora pelo critério de desempate por ID) → votos Moderado = 0,5 + 0,333 + 0,333 = 1,167 → **Moderado**. Mudando k (1, 3, 5, 7) a previsão não muda.
**Discussão:** pelas árvores da Lista 1 (ID3, C4.5 e CART) este cliente (emprego instável) seria **Alto**. O KNN com Hamming simples discorda porque Emprego é apenas 1 dos 6 atributos e os outros 5 casam com clientes Moderado. Com a variante **ponderada pelo ganho de informação**, k=1 já prevê **Alto** (o vizinho mais próximo passa a ser influenciado por Emprego e Patrimônio), mas k≥3 volta a Moderado. Isso mostra a diferença de natureza: a árvore seleciona atributos; o KNN compara instâncias inteiras.

## Avaliação (Leave-One-Out nas 30 instâncias)

| k | Hamming | Hamming ponderado |
|---:|---:|---:|
| 1 | 100,0% | 93,3% |
| 3 | 96,7% | 93,3% |
| 5 | 96,7% | 93,3% |
| 7 | 96,7% | 93,3% |
| 9 | 96,7% | 93,3% |

## Observações
* O k=1 chegou a 100% porque a base tem **instâncias duplicadas** (ex.: E12 e E30; E8 e E24): cada uma “encontra” sua cópia. Esse número é otimista; k=3 (96,7%) é mais realista.
* A ponderação por ganho de informação **não melhorou** aqui: Patrimônio, Renda e Emprego já dominam e são correlacionados; pesos grandes demais deixam Dívida/Garantia quase irrelevantes.
* **Escolha de k:** k pequeno → sensível a ruído; k grande → suaviza demais (com 10 exemplos por classe, k≥10 já misturaria classes). Em empates de distância, desempatei pelo ID.
* **Custo:** O(n·d) por consulta e nenhum treino; sofre com alta dimensionalidade e exige normalização em atributos numéricos (não é o caso aqui).
* **Relação com a Lista 1:** a árvore de decisão gera regras explícitas; o KNN “explica” por exemplos semelhantes.
