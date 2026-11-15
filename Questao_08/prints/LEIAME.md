# Evidências no GeNIe (versão Trial) — Questão 8 (`rede_pneumonia.xdsl`)

A rede foi aberta no GeNIe (*File → Open Network*) e as evidências foram inseridas em sequência (botão direito no nó → *Set Evidence → Sim*). O valor lido em *Node properties: Pneumonia → Value* foi comparado com a enumeração exata do `rede_bayesiana.py` e com o `pgmpy`.

| Print | Evidência acumulada | P(Pneumonia = Sim) no GeNIe | Enumeração / pgmpy |
|---|---|---|---|
| 01_rede_aberta_GeNIe.png | — (estrutura da rede: 7 nós, 6 arcos de dependência + Fumante→Tosse) | — | — |
| 02_priori_Pneumonia_0.0579.png | nenhuma | 0,057875 | 0,0579 |
| 03_Febre_0.3430.png | Febre = Sim | 0,3430377 | 0,3430 |
| 04_Febre_Tosse_0.7708.png | + Tosse = Sim | 0,77077251 | 0,7708 |
| 05_Febre_Tosse_Dispneia_0.9792.png | + Dispneia = Sim | 0,97919904 | 0,9792 |
| 06_Febre_Tosse_Dispneia_RaioX_0.9993.png | + RaioX = Sim | 0,99929241 | 0,9993 |

Os cinco valores coincidem até a 4ª casa decimal. A marca-d\'água "Evaluation Use Only" é da versão Trial. O print 01 foi tirado quando o arquivo ainda se chamava `pneumonia.xdsl` (por isso o título da janela); o conteúdo é o mesmo.

**Correção feita durante a validação:** a primeira versão do `.xdsl` usava o mesmo identificador (`Pneumonia`) para a rede e para o nó, e o GeNIe acusava *"Identifier is not unique"* ao confirmar as propriedades do nó. O identificador da rede passou a ser `RedePneumonia` e o arquivo foi renomeado para `rede_pneumonia.xdsl`.
