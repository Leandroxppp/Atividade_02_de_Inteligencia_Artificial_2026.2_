# Evidências no Protégé (HermiT 1.4.3.456) — Questão 15 (`credito.owl`)

| Arquivo | O que comprova |
|---|---|
| 01_metricas_ontologia.png | 16 classes, 12 propriedades de objeto, 1 de dados, 45 indivíduos; 5 classes equivalentes (definidas) e 2 axiomas de disjunção |
| 02_menu_reasoner_HermiT_em_execucao.png | HermiT 1.4.3.456 selecionado e **em execução** ("Stop reasoner" ativo, rodapé "Reasoner active") |
| 03_E1_tipo_inferido_ClienteEmpregoInstavel.png | Cliente E1 (emprego instável, dívida alta, patrimônio baixo) classificado automaticamente (tipo inferido em amarelo) |
| 04_E5_tipo_inferido_ClienteEstavelPatrimonioAlto.png | Cliente E5 (emprego estável, patrimônio alto) classificado automaticamente |
| 05_dlquery_ClienteElegivel_19_instancias.png | Inferência em cadeia: condições → classe definida → risco → ClienteElegivel; 19 instâncias e 7 subclasses |
| 06_dlquery_ClienteElegivel_lista_final.png | Restante da lista: E3, E5, E6, E8, E9, E10, E12, E13, E15, E17, E18, E19, E22, E23, E24, E25, E27, E29, E30 |

Os resultados coincidem com `../hermit_real.txt` (HermiT via Owlready2): 19 elegíveis e 11 de risco alto não elegíveis.
