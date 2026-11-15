# Questão 9 — Sistema de recomendação de livros baseado em ontologia OWL 2

Arquivos: `livros.owl` (ontologia), `rodar_reasoner.py` (**HermiT real** via Owlready2, para rodar localmente), `owlgen.py` (gerador RDF/XML), `ontologia_livros.py` (ontologia + reasoner mínimo + recomendador), `resultados.txt`. Execute `python ontologia_livros.py`.

> **Validação com reasoner real (HermiT).** `livros.owl` foi carregado e classificado pelo **HermiT 1.4 via Owlready2** (`python rodar_reasoner.py`; saída completa em `hermit_real.txt`). Resultado: ontologia **consistente**; `LivroCurto` = L04, L05, L07, L09, L12; `LeituraRapidaParaIniciante` = L04, L05, L07, L12; `LivroBemAvaliado` = L01, L03, L04, L07, L09, L10; `LeitorIniciante` = Ana, Carla; inversas inferidas (`AutorSilva escreveu L01` etc.) e transitividade de `ehPrerequisitoDe` (L04→L03). **Teste de inconsistência:** um indivíduo `LX` em `LivroTecnico ⊓ LivroFiccao` (classes disjuntas) faz o HermiT acusar a ontologia como inconsistente. Essas classificações **coincidem** com as do reasoner mínimo em Python (`ontologia_livros.py`), usado no recomendador para gerar as justificativas. *Reprodução no Protégé:* abrir `livros.owl`, Reasoner → HermiT → Start reasoner e consultar *Inferred class hierarchy* e *Individuals by type*.

## 1. Domínio
Recomendação de **livros de computação/IA** para leitores, segundo interesses, nível, idioma e histórico (livros fictícios).

## 2. Modelagem (requisitos: ≥10 classes, ≥15 propriedades)
**18 classes:** Pessoa ⊒ {Autor, Leitor}; Livro ⊒ {LivroTecnico ⊒ LivroDidatico, LivroFiccao}; Editora, Genero, Tema, Nivel, Idioma; classes **definidas**: LivroCurto, LivroIniciante, LivroDeIA, LivroBemAvaliado, LeituraRapidaParaIniciante, LeitorIniciante.
**18 propriedades:** 12 de objeto (`escritoPor`↔`escreveu`, `publicadoPor` (funcional), `temGenero`, `abordaTema`, `temNivel` (funcional), `escritoEmIdioma` (funcional), `ehPrerequisitoDe` (**transitiva**), `interessadoEm`, `prefereIdioma`, `temNivelLeitura` (funcional), `jaLeu`) e 6 de dados (`titulo`, `numPaginas`, `anoPublicacao`, `nota`, `preco`, `nome`).
**Axiomas:** domínios/imagens, hierarquia, disjunção (`LivroTecnico ⊥ LivroFiccao`; Livro, Pessoa, Editora… mutuamente disjuntas), inversa, transitividade, funcionalidade e **equivalências**:
```
LivroCurto       ≡ Livro ⊓ ∃numPaginas.(xsd:integer[≤ 250])
LivroIniciante   ≡ Livro ⊓ temNivel value Iniciante
LivroBemAvaliado ≡ Livro ⊓ ∃nota.(xsd:decimal[≥ 4.5])
LeituraRapidaParaIniciante ≡ LivroCurto ⊓ LivroIniciante
```
**42 indivíduos:** 12 livros, 6 autores, 3 editoras, 4 gêneros, 9 temas, 3 níveis, 2 idiomas, 3 leitores (Ana, Bruno, Carla).

## 3. Inferências demonstradas (`resultados.txt`)
* **Classificação automática:** `LivroCurto` = L04, L05, L07, L09, L12; `LeituraRapidaParaIniciante` = L04, L05, L07, L12; `LivroBemAvaliado` = L01, L03, L04, L07, L09, L10; `LeitorIniciante` = Ana, Carla.
* **Relações implícitas:** `AutorSilva escreveu L01` (inversa); `L04 ehPrerequisitoDe L03` (L04→L02→L03, transitividade); `L01 : LivroTecnico` (LivroDidatico ⊑ LivroTecnico).
* **Consistência:** a base é consistente; ao declarar `LX : LivroTecnico ⊓ LivroFiccao` o reasoner detecta violação de disjunção.

## 4. Mecanismo de recomendação (`recomendar()`)
Para o leitor R, um livro L é candidato se (i) L ∉ `jaLeu(R)`, (ii) `abordaTema(L) ∩ interessadoEm(R) ≠ ∅`, (iii) idioma(L) ∈ `prefereIdioma(R)`, (iv) nível(L) ≤ nível(R)+1. Pontuação = `3·|temas em comum| + nota + 1 (mesmo nível) + 0,5 (LivroCurto) − 1,5 (um nível acima)`. A **justificativa** lista os temas casados, o nível, a nota, as **classes inferidas pelo reasoner** e avisos de **pré-requisitos** (propriedade transitiva) ainda não lidos.

Exemplo (Ana: IA e Programação, iniciante, já leu L04): 1º **L07 – IA em Quadrinhos** (9,20; LivroCurto, LeituraRapidaParaIniciante, LivroBemAvaliado), 2º L05 (8,70; ⚠ pré-requisito L01 não lido), 3º L01 (8,60). Bruno (EN aceito) recebe L10 em inglês, L02 (⚠ pré-requisito L04) e L09; Carla: L12 e L09.

## 5. Análise crítica
**Vantagens:** conhecimento explícito e reutilizável; justificativas por construção; inferência de classificação e pré-requisitos sem código; validação de consistência.
**Limitações:** OWL não expressa pontuação/ranking nem preferências fracas (a recomendação tem uma camada procedural em Python); mundo aberto (ausência de `jaLeu` ≠ não leu); sem aprendizado de gosto do usuário; **cold-start** resolvido só por perfil declarado; base pequena. Poderia usar **SWRL/SPARQL** para a regra de recomendação.

<!-- evidencia-protege -->
## Evidência no Protégé (HermiT 1.4.3.456)
Além da execução por código (`rodar_reasoner.py`), a ontologia `livros.owl` foi aberta no **Protégé** com o reasoner **HermiT 1.4.3.456**. Os prints estão em `prints/` (legenda completa em `prints/LEIAME.md`):

* **Requisitos mínimos** — `01_metricas_ontologia.png`: 18 classes, 18 propriedades (12 de objeto + 6 de dados) e 42 indivíduos.
* **Hierarquia e classes definidas** — `02_hierarquia_declarada_asserted.png` e `03_hierarquia_inferida_HermiT.png`.
* **Classificação automática** — `05_LeituraRapidaParaIniciante_L04_L05_L07_L12.png`, `06_LivroBemAvaliado_6_instancias.png` e `11_dlquery_LeitorIniciante_Ana_Carla.png` (Ana e Carla).
* **Reasoner** — `07_menu_reasoner_HermiT_1.4.3.456.png`.
* **Consultas semânticas (DL Query)** — `08_dlquery_LivroCurto_5_instancias.png` (L04, L05, L07, L09, L12) e `09_dlquery_recomendacao_nivel_iniciante.png` (`Livro and (temNivel value Iniciante)` → L01, L04, L05, L07, L08, L12), base da recomendação.
* **Consistência** — `10_inconsistencia_explicacao_HermiT.png`: um indivíduo temporário `LX` declarado em `LivroTecnico` e `LivroFiccao` (classes disjuntas) faz o HermiT acusar a inconsistência e explicá-la; `LX` foi removido e o `.owl` não foi alterado.

*Observação:* a aba *Instances* da classe `LivroCurto` mostra só as instâncias **diretas** (`04_LivroCurto_instancia_direta_L09.png`, apenas L09); as demais pertencem à subclasse `LeituraRapidaParaIniciante`. A DL Query (print 08) mostra as cinco. Os resultados coincidem com `hermit_real.txt`.
