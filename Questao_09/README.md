# Questão 9 — Sistema de recomendação de livros baseado em ontologia OWL 2

Arquivos: `livros.owl` (ontologia), `ontologia_livros.py` (ontologia + reasoner mínimo + recomendador), `rodar_reasoner.py` (**HermiT real** via Owlready2), `owlgen.py` (gerador RDF/XML), `resultados.txt`, `hermit_real.txt` e `prints/` (evidências no Protégé, com `prints/LEIAME.md`).
Execução: `python ontologia_livros.py` (demonstração com Ana, Bruno e Carla) ou `python ontologia_livros.py --usuario` (o usuário informa o próprio perfil; seção 6).

> **Validação com reasoner real (HermiT).** `livros.owl` foi classificado pelo **HermiT via Owlready2** (`python rodar_reasoner.py`; saída em `hermit_real.txt`) e também no **Protégé com HermiT 1.4.3.456** (prints em `prints/`). Resultado: ontologia **consistente**; `LivroCurto` = L04, L05, L07, L09, L12; `LeituraRapidaParaIniciante` = L04, L05, L07, L12; `LivroBemAvaliado` = L01, L03, L04, L07, L09, L10; `LeitorIniciante` = Ana, Carla; inversas inferidas (`AutorSilva escreveu L01` etc.) e transitividade de `ehPrerequisitoDe` (L04→L03). **Teste de inconsistência:** um indivíduo `LX` em `LivroTecnico ⊓ LivroFiccao` (classes disjuntas) faz o HermiT acusar a ontologia como inconsistente. Essas classificações **coincidem** com as do reasoner mínimo em Python, usado no recomendador para gerar as justificativas.

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

### 2.1 Justificativa das principais classes e propriedades
* **Livro, Pessoa, Editora, Genero, Tema, Nivel e Idioma são classes disjuntas, e não textos soltos.** Tema, Nivel e Idioma são classes de indivíduos para que o perfil do leitor e as características do livro sejam ligados por propriedades de objeto (`interessadoEm` e `abordaTema`, `prefereIdioma` e `escritoEmIdioma`, `temNivelLeitura` e `temNivel`). A disjunção permite ao reasoner detectar erros de modelagem, como no teste de inconsistência.
* **Autor e Leitor são subclasses de Pessoa**, porque são papéis diferentes da mesma entidade. **LivroDidatico ⊑ LivroTecnico**, e **LivroTecnico é disjunta de LivroFiccao**; assim o reasoner infere que um livro didático também é técnico e que nenhum livro pode ser técnico e ficção ao mesmo tempo.
* **As classes definidas (LivroCurto, LivroIniciante, LivroDeIA, LivroBemAvaliado, LeituraRapidaParaIniciante e LeitorIniciante) levam os critérios de recomendação para dentro da ontologia.** Por exemplo, "curto" é `numPaginas ≤ 250` e "bem avaliado" é `nota ≥ 4,5`. Assim o reasoner classifica os indivíduos automaticamente e as justificativas citam classes inferidas, e não condições escritas em código.
* **`escritoPor` e `escreveu` são inversas**, o que permite descobrir relações implícitas (por exemplo, `AutorSilva escreveu L01`) sem declará-las. **`ehPrerequisitoDe` é transitiva**, e por isso o sistema avisa quando um pré-requisito indireto ainda não foi lido. **`publicadoPor`, `temNivel`, `escritoEmIdioma` e `temNivelLeitura` são funcionais**, pois cada livro ou leitor tem um único valor.
* **`interessadoEm`, `prefereIdioma`, `temNivelLeitura` e `jaLeu` descrevem o perfil do usuário** e são o ponto de contato com o recomendador. **As propriedades de dados** (`titulo`, `numPaginas`, `anoPublicacao`, `nota`, `preco`, `nome`) permitem restrições de faixa nas classes definidas.

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

## 6. Modo interativo: o usuário informa o perfil (`--usuario`)
`python ontologia_livros.py --usuario` pergunta nome, temas de interesse, nível de leitura, idiomas e livros já lidos; **insere o perfil como um novo indivíduo da classe `Leitor`** na base de conhecimento, executa o reasoner (consistência e classificação, por exemplo `LeitorIniciante`) e exibe as recomendações com justificativas. É o mesmo mecanismo da seção 4, agora com entrada dinâmica, e mostra que a ontologia aceita novos indivíduos sem alterar o `.owl`.
Exemplo de teste (interesses: Algoritmos e BancosDeDados; nível Iniciante; lê português e inglês; já leu L04): o reasoner classifica o perfil como `LeitorIniciante` e recomenda **L05 – Estruturas de Dados Essenciais** (8,70; aborda Algoritmos, nível Iniciante, nota 4,2, `LivroCurto`).

## 7. Evidências no Protégé (HermiT 1.4.3.456)
Os prints estão em `prints/` e cada um é descrito em `prints/LEIAME.md`. Resumo:
| Item do enunciado | Print |
|---|---|
| Tamanho da ontologia (18 classes, 12 propriedades de objeto, 6 de dados, 42 indivíduos) | `01_metricas_ontologia.png` |
| Hierarquia de classes declarada e inferida (classes definidas ≡) | `02_…asserted.png`, `03_…HermiT.png` |
| Reasoner OWL 2 em execução | `07_menu_reasoner_HermiT_1.4.3.456.png` |
| Classificação automática de indivíduos | `04`, `05`, `06`, `11` (LivroCurto, LeituraRapidaParaIniciante, LivroBemAvaliado, LeitorIniciante) |
| Consultas semânticas (DL Query) e base da recomendação | `08`, `09` |
| Verificação de consistência (inconsistência explicada pelo HermiT) | `10_inconsistencia_explicacao_HermiT.png` |

**Demonstração em vídeo:** `../demo_lista2_final.mp4` (execução no terminal e no Protégé; inclui a Q9, com o modo interativo).


