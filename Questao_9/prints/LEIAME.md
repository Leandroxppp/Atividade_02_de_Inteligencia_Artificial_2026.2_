# Evidências no Protégé (HermiT 1.4.3.456) — Questão 9 (`livros.owl`)

| Arquivo | O que comprova |
|---|---|
| 01_metricas_ontologia.png | 18 classes, 12 propriedades de objeto, 6 de dados, 42 indivíduos (mínimos do enunciado: 10 classes, 15 propriedades) |
| 02_hierarquia_declarada_asserted.png | Hierarquia declarada; classes definidas (ícone ≡): LivroCurto, LivroIniciante, LivroDeIA, LivroBemAvaliado, LeituraRapidaParaIniciante |
| 03_hierarquia_inferida_HermiT.png | Mesma hierarquia na visão *Inferred* (reasoner ativo) |
| 04_LivroCurto_instancia_direta_L09.png | Aba *Instances* mostra só as instâncias **diretas** (L09); as demais são instâncias de LeituraRapidaParaIniciante, subclasse de LivroCurto — ver print 08 |
| 05_LeituraRapidaParaIniciante_L04_L05_L07_L12.png | Classificação automática: definição (numPaginas ≤ 250 e temNivel Iniciante) e instâncias inferidas |
| 06_LivroBemAvaliado_6_instancias.png | Classificação automática por nota ≥ 4,5: L01, L03, L04, L07, L09, L10 |
| 07_menu_reasoner_HermiT_1.4.3.456.png | Reasoner OWL 2 utilizado: HermiT, em execução |
| 08_dlquery_LivroCurto_5_instancias.png | Consulta semântica (DL Query): L04, L05, L07, L09, L12 (diretas + indiretas) |
| 09_dlquery_recomendacao_nivel_iniciante.png | Base da recomendação: `Livro and (temNivel value Iniciante)` → L01, L04, L05, L07, L08, L12 |
| 10_inconsistencia_explicacao_HermiT.png | Teste de consistência: indivíduo temporário LX em LivroTecnico e LivroFiccao (disjuntas) → HermiT acusa inconsistência e explica (`owl:Thing SubClassOf owl:Nothing`). LX foi removido; o `.owl` não foi alterado |
| 11_dlquery_LeitorIniciante_Ana_Carla.png | Classificação automática de **pessoas**: `LeitorIniciante` → Ana e Carla |

Os resultados coincidem com `../hermit_real.txt` (HermiT via Owlready2).
