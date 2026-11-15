// Neo4j (Cypher) — equivalente ao grafo de kg_saude.py. Executado no Neo4j 5 (Docker + cypher-shell); saída em Q14_neo4j.txt.
CREATE (arbo:Classe {nome:'Arbovirose'}), (inf:Classe {nome:'DoencaInfecciosa'})
CREATE (dengue:Doenca {nome:'Dengue'}), (zika:Doenca {nome:'Zika'}), (chik:Doenca {nome:'Chikungunya'}), (gripe:Doenca {nome:'Gripe'})
CREATE (dengue)-[:SUBCLASSE_DE]->(arbo), (zika)-[:SUBCLASSE_DE]->(arbo), (chik)-[:SUBCLASSE_DE]->(arbo),
       (arbo)-[:SUBCLASSE_DE]->(inf), (gripe)-[:SUBCLASSE_DE]->(inf)
CREATE (febre:Sintoma {nome:'Febre'}), (mancha:Sintoma {nome:'Manchas'}), (docu:Sintoma {nome:'DorOcular'}),
       (dmus:Sintoma {nome:'DorMuscular'}), (tosse:Sintoma {nome:'Tosse'}), (conj:Sintoma {nome:'Conjuntivite'}), (dart:Sintoma {nome:'DorArticular'})
CREATE (dengue)-[:TEM_SINTOMA]->(febre), (dengue)-[:TEM_SINTOMA]->(dmus), (dengue)-[:TEM_SINTOMA]->(mancha), (dengue)-[:TEM_SINTOMA]->(docu),
       (zika)-[:TEM_SINTOMA]->(febre), (zika)-[:TEM_SINTOMA]->(mancha), (zika)-[:TEM_SINTOMA]->(conj),
       (chik)-[:TEM_SINTOMA]->(febre), (chik)-[:TEM_SINTOMA]->(dart), (chik)-[:TEM_SINTOMA]->(mancha),
       (gripe)-[:TEM_SINTOMA]->(febre), (gripe)-[:TEM_SINTOMA]->(tosse), (gripe)-[:TEM_SINTOMA]->(dmus)
CREATE (ibu:Medicamento {nome:'Ibuprofeno'}), (par:Medicamento {nome:'Paracetamol'})
CREATE (ibu)-[:TRATA]->(febre), (par)-[:TRATA]->(febre), (ibu)-[:CONTRAINDICADO_EM]->(dengue)
CREATE (p:Paciente {nome:'Paciente1'})
CREATE (p)-[:TEM_SINTOMA]->(febre), (p)-[:TEM_SINTOMA]->(mancha), (p)-[:TEM_SINTOMA]->(docu), (p)-[:TOMA]->(ibu);

// 1) Inferência por travessia: fechamento transitivo da taxonomia
MATCH (:Doenca {nome:'Dengue'})-[:SUBCLASSE_DE*1..]->(c:Classe) RETURN c.nome;

// 2) Diagnóstico candidato: doenças ordenadas pelo nº de sintomas em comum com o paciente
MATCH (p:Paciente {nome:'Paciente1'})-[:TEM_SINTOMA]->(s:Sintoma)<-[:TEM_SINTOMA]-(d:Doenca)
RETURN d.nome AS doenca, count(s) AS sintomas_em_comum, collect(s.nome) AS quais ORDER BY sintomas_em_comum DESC;

// 3) Regra de segurança (inferência de alerta): paciente toma medicamento contraindicado para doença suspeita
MATCH (p:Paciente {nome:'Paciente1'})-[:TOMA]->(m:Medicamento)-[:CONTRAINDICADO_EM]->(d:Doenca)
WHERE EXISTS { (p)-[:TEM_SINTOMA]->(:Sintoma)<-[:TEM_SINTOMA]-(d) }
RETURN p.nome, m.nome AS medicamento, d.nome AS possivel_doenca;
