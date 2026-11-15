# Questão 14 — Grafos de Conhecimento: representação, inferência e aprendizagem

Arquivos: `kg_saude.py` (KG + inferência por regras + TransE), `neo4j_saude.cypher` (equivalente em Cypher; a mesma saída, obtida em Python, está em `resultados.txt`; o script Cypher foi executado no Neo4j 5 e a saída está em `Q14_neo4j.txt`), `resultados.txt`.

## 1. Representação de conhecimento
Um **Grafo de Conhecimento (KG)** representa fatos como **triplas** `(sujeito, relação, objeto)` ou, em *property graphs* (Neo4j), como **nós rotulados** e **arestas tipadas** com propriedades. Alguns elementos:
* **Entidades** (Dengue, Febre, Paciente1) e **relações** (`TEM_SINTOMA`, `TRATA`, `SUBCLASSE_DE`).
* **Esquema/ontologia** (opcional): tipos, hierarquias, domínios e restrições. Modelos: **RDF/RDFS/OWL + SPARQL** (semântica formal, interoperável) e **property graph + Cypher** (flexível, rápido, ótimo para aplicações).
* Vantagens: integra fontes heterogêneas, é extensível (novos tipos de aresta sem migrar esquema), e se presta a consultas por caminhos.

## 2. Inferência
1. **Por travessia/consulta de caminhos:** `Dengue -[:SUBCLASSE_DE*]-> Classe` calcula o **fechamento transitivo** (resultado: Arbovirose, DoencaInfecciosa).
2. **Por regras** (SWRL/Datalog/SHACL ou consultas): `toma(P,M) ∧ contraindicado_em(M,D) ∧ suspeita(P,D) ⇒ alerta(P,M)` gera fatos novos (alertas).
3. **Por raciocinadores de ontologia** (OWL): classificação e consistência (ver Questões 9 e 15).
4. **Por similaridade/estatística:** pontuação de doenças por sintomas em comum (Jaccard) ou algoritmos de grafo (PageRank, *community detection*).
5. **Por embeddings (aprendizagem):** inferência indutiva e aproximada (seção 3).

## 3. Aprendizagem
* **Construção/enriquecimento:** extração de entidades e relações de texto (NER, extração de relações, LLMs), ligação de entidades e fusão.
* **Embeddings de KG (TransE, DistMult, RotatE):** cada entidade/relação vira um vetor; em **TransE**, `h + r ≈ t`. Treino minimiza a margem entre triplas verdadeiras e “negativas” corrompidas. Serve para **completar o grafo** (*link prediction*) e classificar entidades.
* **Redes neurais em grafos (GNNs)** e **GraphRAG** (KG como memória factual para LLMs, reduzindo alucinações).
* Limitação: modelos aprendidos são **probabilísticos**; sugerem, não provam fatos.

## 4. Aplicação: apoio à decisão clínica sobre arboviroses (`kg_saude.py`)
KG com 26 triplas (3 arboviroses + gripe, sintomas, medicamentos, um paciente).

**Inferências realizadas (de `resultados.txt`):**
1. *Taxonomia:* `Dengue ⊑ Arbovirose, DoencaInfecciosa`.
2. *Diagnóstico por subgrafo:* Paciente1 (febre, manchas, dor ocular) → **Dengue (Jaccard 0,75)**, Zika e Chikungunya (0,50), Gripe (0,20).
3. *Regra de segurança:* Paciente1 toma **Ibuprofeno**, contraindicado em Dengue → **alerta** (fato novo inferido que não estava no grafo).
4. *Aprendizagem (TransE)* — escondi a tripla `(Zika, tem_sintoma, Febre)` e treinei com as outras: no ranking de candidatos para `(Zika, tem_sintoma, ?)`, “Febre” ficou em **3º entre 17** entidades. Resultado modesto e esperado: o grafo é minúsculo; com dados reais e mais triplas o ganho seria maior. Como um único experimento com uma só semente não permite generalizar, o item 5 repete a avaliação de forma sistemática.

5. *Avaliação mais robusta do TransE* (`kg_saude.py`, item 5): ocultei **cada** tripla `tem_sintoma` (uma por vez), treinei 5 vezes com sementes diferentes e medi a posição do objeto correto entre os candidatos (ranking filtrado, descartando fatos já conhecidos; triplas cujo objeto só existia nelas não são avaliáveis): **50 previsões, posição média 2,20 e Hits@3 = 82%**, bem acima do acaso (cerca de metade dos ~16 candidatos). Conclusão: mesmo em um KG minúsculo, o embedding recupera a maior parte dos sintomas omitidos; com KGs reais o ganho e a dificuldade crescem. Limite: o conjunto é pequeno e os sintomas são muito compartilhados (Febre, Manchas), o que facilita o acerto.

**Neo4j:** o arquivo `neo4j_saude.cypher` cria o grafo e traz as 3 consultas (travessia, diagnóstico, alerta). Passos: instalar Neo4j Desktop/Aura → colar o script no Browser → executar as consultas e ver o grafo.

**Execução no Neo4j (realizada):** `neo4j_saude.cypher` foi executado no **Neo4j 5** (imagem Docker `neo4j:5`) com `cypher-shell`; a saída está em `Q14_neo4j.txt`. Resultados: (1) travessia → `Arbovirose`, `DoencaInfecciosa`; (2) diagnóstico → Dengue 3 sintomas em comum, Chikungunya 2, Zika 2, Gripe 1; (3) alerta → `Paciente1`, `Ibuprofeno`, `Dengue`. Coincidem com os itens 1–3 obtidos em Python (`kg_saude.py`). Comando: `Get-Content .\neo4j_saude.cypher -Raw | docker exec -i neo4j-saude cypher-shell -u neo4j -p <senha> --format plain`.