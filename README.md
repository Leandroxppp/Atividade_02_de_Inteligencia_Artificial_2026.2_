# Lista 2 — Inteligência Artificial (PPGI 2026.2) — respostas e código

Cada pasta `Questao_N/` tem um `README.md` com o relatório e, quando aplicável, o código, os dados e as saídas (`resultados.txt`).

| Q | Conteúdo | Código executável |
|---|---|---|
| 1 | Ontologias × KGs + mapeamento | — |
| 2 | KNN na base de 30 instâncias da Lista 1 | `knn.py` |
| 3 | ELIZA, análise de diálogo, PARRY, AIML/ALICE | `eliza.py` |
| 4 | Taxonomia de agentes com PEAS | — |
| 5 | Resumo do vídeo de inferência de LLM (IBM) | — |
| 6 | Sistema fuzzy de Mamdani (risco de crédito) | `fuzzy_credito.py`, `fuzzy_skfuzzy.py` |
| 7 | CBR de diagnóstico médico (Retrieve/Reuse/Revise/Retain) | `cbr_medico.py` |
| 8 | Rede Bayesiana de pneumonia | `rede_bayesiana.py`, `rede_pgmpy.py`, `pneumonia.bif` |
| 9 | Recomendação de livros com ontologia OWL | `ontologia_livros.py`, `livros.owl` |
| 10 | Buscas BFS/DFS/UCS/A* e versão com D e F | `busca.py` |
| 11 | Agente clássico × agente LLM (planejamento) | `planejador_classico.py` |
| 12 | Assistente acadêmico baseado em LLM | `agente_llm.py` |
| 13 | Ensaio sobre Transformers + exemplo numérico | `transformer_demo.py` |
| 14 | Knowledge Graph, Cypher/Neo4j, TransE | `kg_saude.py`, `neo4j_saude.cypher` |
| 15 | Ontologia OWL de crédito | `ontologia_credito.py`, `credito.owl` |

## Execução e validações
Todos os scripts foram executados e as saídas estão guardadas (`resultados.txt`, `dialogo_trace.txt` e o consolidado `saida_teste.txt` (consolidado), em UTF-8).

| Item | Validação | Arquivo |
|---|---|---|
| Q9 e Q15 | **HermiT** (Owlready2 + Java): consistência, classificação automática, inversas/transitivas e teste de inconsistência; coincide com o reasoner mínimo em Python | `Questao_9/hermit_real.txt`, `Questao_15/hermit_real.txt` |
| Q6 | Versão **scikit-fuzzy** executada; centroides iguais aos do NumPy (±0,2) | `Questao_6/skfuzzy_real.txt` |
| Q8 | Versão **pgmpy** executada; `OK` em todas as consultas. Também exportada e validada no **GeNIe Trial** (`rede_pneumonia.xdsl`, prints em `Questao_8/prints/`) | `Questao_8/pgmpy_real.txt`, `rede_pneumonia.xdsl` |
| Q12 | Caminho LLM testado com **LLM local via Ollama** (`llama3.2` e `qwen2.5:7b`): verificador, nova tentativa com feedback e alternativa offline; também com servidor simulado | `Questao_12/Q12_llm_ollama.txt`, `Q12_llm_qwen.txt`, `llm_stub_test.txt` |
| Q14 | Script Cypher executado no **Neo4j 5** (Docker + `cypher-shell`); respostas iguais às do `kg_saude.py` | `Questao_14/Q14_neo4j.txt` |

## Limitações conhecidas
* **Q12:** testado com LLM local via Ollama (`llama3.2` 3B e `qwen2.5:7b`) em duas rodadas (seções 6 e 9 do README da Q12). Rodada 2: o LLM produziu o plano final em 1 de 6 execuções. Rodada 3 (15/11/2026, com as melhorias da seção 7): 5 de 6 planos vieram do LLM e passaram no verificador, 1 veio da alternativa offline e nenhuma execução ficou sem plano; porém esses planos apresentam divergências semânticas que o verificador não detecta (tarefa omitida, prioridade invertida), documentadas na seção 9. Não foi testado com a API da Anthropic. <!-- rodada3-ollama -->
* **Q14:** o script Cypher foi executado no Neo4j 5 (Docker, `cypher-shell`); saída em `Questao_14/Q14_neo4j.txt`, com as mesmas respostas do `kg_saude.py`.
* **Q9 e Q15:** o reasoner foi executado por código (HermiT via Owlready2) e também no **Protégé** com HermiT 1.4.3.456; os prints estão em `Questao_9/prints/` e `Questao_15/prints/` (com `LEIAME.md` descrevendo cada um). <!-- evidencia-protege -->
* Bases de casos, CPTs, pesos e funções de pertinência são **fictícios/educacionais** (justificados nos relatórios), não calibrados com dados reais.

## Dependências e execução
Python 3, `numpy`, `matplotlib`, `networkx`. Extras: `scikit-fuzzy`, `pgmpy`, `owlready2` (+ Java para o HermiT). Rodar: `cd Questao_N && python <script>.py` (no Windows: `set PYTHONIOENCODING=utf-8` antes, para os acentos).

**Demonstração:** vídeo `demo_lista2.mp4` (≈1min40s, execução no terminal dos scripts das Q7 [CBR], Q8 [rede bayesiana] e Q9 [ontologia + reasoner]).
