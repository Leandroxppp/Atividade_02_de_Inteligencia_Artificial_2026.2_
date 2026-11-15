# Questão 1 — Ontologias × Grafos de Conhecimento (com mapeamento)

**Aplicação escolhida:** apoio ao diagnóstico de doenças transmitidas por mosquitos (dengue, zika, chikungunya) e prescrição segura de medicamentos.

## 1. Comparativo

| Critério | Sistemas baseados em **Ontologias** (OWL 2 / Lógica de Descrição) | Sistemas baseados em **Grafos de Conhecimento** (RDF ou *property graph*, ex.: Neo4j) |
|---|---|---|
| Foco | Modelo **conceitual** formal e compartilhado do domínio (TBox): conceitos, relações, axiomas | **Dados** interligados em larga escala (ABox): entidades e fatos; esquema opcional/leve |
| Formalismo | Lógica de Descrição (decidível); semântica formal | Triplas (s,p,o) ou nós/arestas com propriedades; semântica formal só se usar RDF(S)/OWL |
| Suposição de mundo | **Mundo aberto** (ausência de fato ≠ falsidade) | Normalmente **mundo fechado** em consultas (Cypher/SQL-like); em RDF+OWL é aberto |
| Inferência | Dedutiva por *reasoner* (HermiT, Pellet): classificação, consistência, realização, herança | Travessia/consulta de caminhos, regras (SHACL/Datalog/SWRL), algoritmos de grafos, **embeddings/GNNs** (inferência estatística) |
| Expressividade | Alta: restrições (∃, ∀, cardinalidade), classes definidas, disjunção, propriedades transitivas/inversas | Alta flexibilidade de modelagem; axiomas fracos ou ausentes (restrições via SHACL/constraints) |
| Escalabilidade | Raciocínio completo é caro (OWL 2 DL é N2EXPTIME-completo no pior caso; os perfis EL/QL/RL são tratáveis) → ontologias de milhares de classes e poucos milhões de indivíduos | Bilhões de arestas; ótimo para consulta e analítica |
| Qualidade/validação | Verifica **consistência** logicamente | Valida com restrições de integridade; ruído e inconsistência são toleráveis |
| Construção | Manual/especialistas, engenharia de ontologias (METHONTOLOGY, 101) | Semi-automática: extração de texto, ETL, ligação de entidades; muito dado “sujo” |
| Aprendizagem | Aprendizagem de ontologias (difícil) | Natural: completar grafos (TransE, RotatE), GNN, extração por PLN/LLM |
| Exemplos | OBO/SNOMED CT, Gene Ontology | Google KG, Wikidata, DBpedia, KGs corporativos em Neo4j |
| Pontos fortes | Rigor, explicabilidade lógica, interoperabilidade semântica | Escala, desempenho, integração de fontes, uso com ML/LLM (GraphRAG) |
| Limitações | Frágil a dados incompletos, custo de manutenção, raciocínio lento em escala | Semântica menos formal, risco de inconsistência silenciosa |

**Relação entre elas:** não são excludentes. A ontologia é o *esquema semântico* (o “vocabulário com lógica”) e o KG é a *instanciação em escala*: **KG = ontologia + dados**. Na prática usa-se a ontologia para governar o KG (tipos, restrições, regras) e o KG para escalar e alimentar aprendizado.

## 1.1 O comparativo aplicado ao exemplo (diagnóstico de arboviroses e prescrição segura)
| Necessidade da aplicação | Com **ontologia (OWL)** | Com **grafo de conhecimento** |
|---|---|---|
| Definir o que é "Arbovirose", "Dengue" e "Paciente em risco" de forma não ambígua e compartilhável entre hospitais | **Ponto forte:** classes, hierarquia e classes definidas (ex.: `PacienteEmRisco ≡ Paciente ⊓ toma some (…)`) com semântica formal | Possível por rótulos/nós-meta, mas sem axiomas formais (só convenção) |
| Classificar automaticamente um paciente novo e **detectar inconsistências** (ex.: medicamento declarado como seguro e contraindicado) | **Reasoner** (HermiT/Pellet) deduz classes e acusa inconsistência | Exige consultas/regras explícitas e constraints; inconsistência passa despercebida se ninguém consultar |
| Armazenar milhões de prontuários, interações medicamentosas e literatura, e consultar em milissegundos (`MATCH (p)-[:TOMA]->…`) | O raciocínio completo não escala bem a esse volume de indivíduos | **Ponto forte:** bancos de grafo (Neo4j) escalam e indexam relacionamentos |
| Sugerir doenças prováveis para sintomas incompletos e completar relações faltantes | Dedução lógica não "adivinha"; só conclui o que os axiomas permitem | **Embeddings/GNN** fazem inferência estatística (link prediction) e podem alimentar um LLM (GraphRAG) |
| Explicar a decisão ao médico | Prova lógica (quais axiomas levaram à conclusão) | Caminho no grafo que sustenta o alerta (`paciente → medicamento → doença`) |

**Conclusão para a aplicação:** a ontologia garante o **significado e a correção** do conhecimento clínico (o que é uma arbovirose, quando um medicamento é contraindicado); o grafo garante **escala e integração** dos dados reais dos pacientes. O desenho mais realista usa as duas: a ontologia como esquema do grafo (e fonte de regras), e o grafo como repositório de dados e de aprendizagem.

## 2. Mapeamento de uma ontologia em um grafo de conhecimento (exemplo)

### 2.1 Fragmento da ontologia (OWL/Manchester)
```
Class: Doenca            Class: Arbovirose  SubClassOf: Doenca
Class: Dengue            SubClassOf: Arbovirose
Class: Sintoma           Class: Medicamento      Class: Paciente
ObjectProperty: temSintoma        Domain: Doenca or Paciente   Range: Sintoma
ObjectProperty: trata             Domain: Medicamento          Range: Sintoma or Doenca
ObjectProperty: contraindicadoEm  Domain: Medicamento          Range: Doenca
ObjectProperty: toma              Domain: Paciente             Range: Medicamento
DataProperty:   dose_mg           Domain: Medicamento          Range: xsd:integer
Class: PacienteEmRisco EquivalentTo: Paciente and (toma some (Medicamento and contraindicadoEm some {dengue})) and (suspeitaDe value dengue)
Individuals: dengue : Dengue ;   (aqui `dengue` é o indivíduo que representa a doença no exemplo; `Dengue` é a classe — o mesmo nome em maiúscula/minúscula é *punning* controlado, evitável com nomes distintos)
   febre : Sintoma ; ibuprofeno : Medicamento ; p1 : Paciente
Facts: dengue temSintoma febre ; ibuprofeno contraindicadoEm dengue ; p1 toma ibuprofeno
```

### 2.2 Regras de mapeamento

| Elemento OWL | Elemento no KG (property graph) | Elemento no KG (RDF) |
|---|---|---|
| Classe `C` | **Rótulo** de nó `:C` (e/ou nó-meta `(:Classe {nome})`) | `:C rdf:type owl:Class` |
| `C1 SubClassOf C2` | Aresta `(:C1)-[:SUBCLASSE_DE]->(:C2)` entre nós-meta *ou* rótulos múltiplos (`:Dengue:Arbovirose:Doenca`) | `:C1 rdfs:subClassOf :C2` |
| Indivíduo `a : C` | Nó `(:C {id:'a'})` | `:a rdf:type :C` |
| ObjectProperty `p` | **Tipo de relacionamento** `[:P]` | `:p rdf:type owl:ObjectProperty` |
| Fato `a p b` | Aresta `(a)-[:P]->(b)` | tripla `:a :p :b` |
| DataProperty `d` | **Propriedade do nó** `{d: valor}` | `:a :d "valor"^^xsd:integer` |
| `inverseOf`, `transitive`, equivalência de classes | Regra/consulta (`*1..`), aresta materializada, ou *constraint* | axiomas OWL |
| Domain/Range, cardinalidades | Constraints (Neo4j) ou SHACL | `rdfs:domain/range`, SHACL |

### 2.3 Resultado do mapeamento (Cypher)
```cypher
// TBox (nós-meta)
CREATE (doenca:Classe {nome:'Doenca'}), (arbo:Classe {nome:'Arbovirose'}), (cDengue:Classe {nome:'Dengue'})
CREATE (cDengue)-[:SUBCLASSE_DE]->(arbo)-[:SUBCLASSE_DE]->(doenca)
// ABox (instâncias; os rótulos refletem a classe)
CREATE (d:Doenca:Arbovirose:Dengue {id:'dengue'}), (f:Sintoma {id:'febre'}),
       (i:Medicamento {id:'ibuprofeno', dose_mg:400}), (p:Paciente {id:'p1'})
CREATE (d)-[:TEM_SINTOMA]->(f), (i)-[:CONTRAINDICADO_EM]->(d), (p)-[:TOMA]->(i), (p)-[:SUSPEITA_DE]->(d)
```
Em triplas: `(dengue, rdf:type, Dengue)`, `(Dengue, subClassOf, Arbovirose)`, `(dengue, temSintoma, febre)`, `(ibuprofeno, contraindicadoEm, dengue)`, `(p1, toma, ibuprofeno)`.

### 2.4 O que muda na inferência após o mapeamento
* **Na ontologia**: o *reasoner* infere sozinho que `p1 : PacienteEmRisco` (classe definida) e que `dengue : Doenca` (herança).
* **No KG**: a mesma dedução vira consulta/regra explícita:
```cypher
MATCH (p:Paciente)-[:TOMA]->(m:Medicamento)-[:CONTRAINDICADO_EM]->(d:Doenca)<-[:SUSPEITA_DE]-(p)
RETURN p.id AS paciente, m.id AS medicamento, d.id AS doenca   // alerta: p1, ibuprofeno, dengue
```
Perde-se a inferência automática por axioma (precisa-se materializar ou escrever consulta), ganha-se desempenho e a possibilidade de aplicar embeddings sobre o mesmo grafo. Os exemplos executáveis estão nas Questões 14 e 15 (`kg_saude.py`, `ontologia_credito.py`).
