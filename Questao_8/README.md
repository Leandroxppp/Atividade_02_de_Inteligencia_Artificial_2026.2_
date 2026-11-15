# Questão 8 — Diagnóstico de pneumonia com Rede Bayesiana

Arquivos: `rede_bayesiana.py` (modelo + inferência exata), `pneumonia.bif` (**arquivo do projeto** em formato BIF, gerado pelo código) e `rede_pneumonia.xdsl` (mesma rede no formato do **GeNIe**: File → Open Network; **aberto e validado no GeNIe Trial**, com prints e tabela em `prints/LEIAME.md`: P(Pneumonia) = 0,0579 → 0,3430 → 0,7708 → 0,9792 → 0,9993, iguais à enumeração e ao pgmpy; o identificador da rede foi corrigido para `RedePneumonia` após o GeNIe acusar "Identifier is not unique"), `rede_pgmpy.py` (mesma rede em **pgmpy**; executado, ver `pgmpy_real.txt`), `rede.png` (grafo), `resultados.txt`.
**Ferramenta:** a inferência foi executada com **enumeração exata** da distribuição conjunta (correta e verificável para 7 variáveis binárias). `rede_pgmpy.py` reconstrói a rede em **pgmpy** (`TabularCPD`, `VariableElimination`) e compara cada probabilidade com a enumeração; esse script **foi executado** (pgmpy 1.1.2; saída em `pgmpy_real.txt`) e o resultado é `OK` em todas as linhas (diferença nula na 4ª casa decimal com a enumeração). O arquivo `pneumonia.bif` pode ser lido com `pgmpy.readwrite.BIFReader`.

## 1. Domínio e variáveis
Doença: **pneumonia**. Todas binárias (Sim/Não).

| Variável | Papel | Significado |
|---|---|---|
| Fumante | fator de risco | Tabagismo atual |
| Contato | fator de risco | Contato recente com pessoa com infecção respiratória |
| **Pneumonia** | doença (alvo) | Diagnóstico a estimar |
| Febre, Tosse, Dispneia | sintomas | Observáveis |
| RaioX | exame | Raio-X com infiltrado pulmonar |

## 2. Estrutura (ver `rede.png`)
`Fumante → Pneumonia ← Contato`; `Pneumonia → Febre`, `Pneumonia → Dispneia`, `Pneumonia → RaioX`; `Pneumonia → Tosse ← Fumante`.
* Justificativa: fumar e exposição elevam o risco; a doença causa os sintomas/exame (modelo causal).
* **Fumante → Tosse**: fumantes têm tosse crônica mesmo sem pneumonia — gera o *explaining away*.
* **Independências condicionais:** Febre ⟂ Tosse ⟂ Dispneia ⟂ RaioX | Pneumonia; Fumante ⟂ Contato (a priori); Febre ⟂ Fumante, Contato | Pneumonia. Verificado numericamente: P(Febre|Pneumonia, Tosse) = P(Febre|Pneumonia) = 0,85, mas P(Febre|Tosse) = 0,313 ≠ P(Febre) = 0,143.

## 3. CPTs e justificativa das probabilidades
**Hipóteses do modelo:** (H1) população-alvo = pessoas que procuram atendimento com queixa respiratória (por isso o prior de pneumonia, 5,8%, é maior que na população geral); (H2) sintomas e exame são condicionalmente independentes dados a doença (exceto Tosse, que também depende de Fumante); (H3) uma única doença-alvo, variáveis binárias.

**Justificativa (valores educacionais, de ordem de grandeza compatível com o que a literatura clínica descreve; não foram extraídos de um estudo específico; por isso são tratados como hipóteses do modelo, e não como estimativas epidemiológicas):**
* *P(Fumante)=0,25 e P(Contato)=0,15:* prevalências plausíveis de tabagismo atual e de exposição recente a infecção respiratória em adultos que procuram atendimento.
* *P(Pneumonia | Fumante, Contato):* parte de uma base de 2% (sem fatores) e cresce com cada fator de risco; fumar (≈4×) e contato (≈7×) elevam o risco, e juntos o efeito é menor que o produto (0,30), refletindo que parte do risco é compartilhada.
* *Febre 0,85 / 0,10:* febre é sintoma frequente, mas inespecífico (virose, outras infecções) → alta sensibilidade, especificidade moderada.
* *Dispneia 0,70 / 0,05:* menos sensível que febre, porém mais específica (rara sem comprometimento respiratório).
* *RaioX alterado 0,90 / 0,03:* o infiltrado é o exame de referência para confirmar: alta sensibilidade e alta especificidade (falso-positivos raros, atelectasias etc.).
* *Tosse | Pneumonia, Fumante:* quase universal na pneumonia (0,90–0,95); em quem não tem pneumonia, o fumante tem tosse crônica (0,35) muito mais que o não fumante (0,08). É essa aresta Fumante → Tosse que cria o efeito discutido no Exp. 2.
* **Análise de sensibilidade (executada):** perturbando todas as CPTs aleatoriamente em ±20% (500 simulações, semente 7), a ordem de poder diagnóstico RaioX > Dispneia > Febre (razão de verossimilhança) se manteve em 98,6% dos casos, e P(Pneumonia | Febre, Tosse) variou entre 0,65 e 0,85 (valor base 0,77). Ou seja, as conclusões qualitativas são robustas, mas os números exatos dependem das CPTs. Com dados reais, estime-as por MLE/EM.

P(Fumante)=0,25; P(Contato)=0,15.

| Fumante | Contato | P(Pneumonia=Sim) |
|---|---|---:|
| Sim | Sim | 0,30 |
| Sim | Não | 0,08 |
| Não | Sim | 0,15 |
| Não | Não | 0,02 |

| Pneumonia | P(Febre) | P(Dispneia) | P(RaioX alterado) |
|---|---:|---:|---:|
| Sim | 0,85 | 0,70 | 0,90 |
| Não | 0,10 | 0,05 | 0,03 |

| Pneumonia | Fumante | P(Tosse) |
|---|---|---:|
| Sim | Sim | 0,95 |
| Sim | Não | 0,90 |
| Não | Sim | 0,35 |
| Não | Não | 0,08 |

## 4. Experimentos (todas as probabilidades de `resultados.txt`)
**A priori:** P(Pneumonia) = **0,0579**.

**Exp. 1 — atualização sequencial**

| Evidências acumuladas | P(Pneumonia \| e) |
|---|---:|
| nenhuma | 0,0579 |
| Febre | 0,3430 |
| Febre, Tosse | 0,7708 |
| + Dispneia | 0,9792 |
| + RaioX alterado | 0,9993 |

Cada sintoma, com razão de verossimilhança alta, multiplica as chances; febre sozinha (inespecífica, pois 10% dos sem pneumonia a têm) leva de 5,8% a 34%.

**Exp. 2 — comparação de conjuntos de evidência (efeito do fator de risco Fumante sobre a tosse)**

| Evidências | P(Pneumonia \| e) |
|---|---:|
| Tosse | 0,2835 |
| Tosse, Fumante=Sim | 0,2569 |
| Tosse, Fumante=Não | 0,3163 |
| Febre, Tosse | 0,7708 |
| Febre, Tosse, Fumante=Sim | 0,7461 |

Saber que o paciente é fumante **reduz** P(Pneumonia | tosse): o tabagismo é uma causa alternativa da tosse (Pneumonia → Tosse ← Fumante é uma estrutura em V), então a tosse perde valor diagnóstico (razão de verossimilhança ≈ 2,7 em fumantes contra ≈ 11 em não fumantes). Isso lembra o *explaining away*, mas **não é o caso puro**: como Fumante também é pai de Pneumonia, o tabagismo ao mesmo tempo *aumenta* o prior da doença; o resultado líquido (0,2835 → 0,2569) é a soma dos dois efeitos.

**Exp. 3 — fatores de risco e evidências negativas**

| Evidências | P(Pneumonia \| e) |
|---|---:|
| Fumante, Contato | 0,3000 |
| Não fumante, sem contato | 0,0200 |
| Sem febre, sem tosse, sem dispneia | 0,0003 |
| RaioX alterado | 0,6482 |
| RaioX normal, Febre, Tosse | 0,2574 |

Evidência negativa também informa (0,0003); o exame normal derruba a probabilidade mesmo com febre e tosse (0,77 → 0,26).

## 5. Discussão
* **Incerteza:** representada por probabilidades; sintomas são probabilísticos (nunca “regra rígida”); evidências incompletas são aceitas (variáveis não observadas são marginalizadas).
* **Influência das evidências:** RaioX é a mais discriminativa (razão 0,90/0,03 = 30), seguida de dispneia (14), febre (8,5); tosse é afetada pelo tabagismo.
* **Vs. regras:** BN dá graus de crença, atualiza com qualquer subconjunto de evidências, lida com *explaining away* e trata fatores de risco e sintomas no mesmo modelo; regras precisam enumerar combinações e não quantificam incerteza.
* **Limitações:** uma só doença (sem diagnóstico diferencial com gripe/COVID), CPTs inventadas (sem calibração com dados), variáveis binárias (sem gravidade/idade), independência condicional dos sintomas dado a doença (nem sempre real), **não há *noisy-OR***.
* **Melhorias:** nós para outras doenças, idade, comorbidades, gravidade; CPTs estimadas de dados (EM/MLE); nós de decisão/utilidade (diagrama de influência); validação com especialistas.
