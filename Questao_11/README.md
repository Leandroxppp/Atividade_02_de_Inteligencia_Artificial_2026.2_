# Questão 11 — Agente clássico (AIMA, cap. 2) × agente baseado em LLM: planejamento de atividades

Arquivos: `planejador_classico.py` (agente baseado em utilidade), `resultados.txt`. A parte LLM está implementada em `../Questao_12/agente_llm.py`.

## 1. O problema
Professor com 14h–18h; atividades A (aula, 90 min, Alta, hoje), B (correção, 120 min, Média, amanhã), C (reunião, 60 min, Alta, **fixa 16h–17h**), D (artigo, 60 min, Baixa, próxima semana). Sem sobreposição; atividade iniciada deve ser concluída salvo divisão explícita; justificar o que não foi feito.

## 2. Solução clássica (agente baseado em utilidade)
**PEAS:** P = maximizar utilidade das tarefas concluídas respeitando restrições; E = agenda de 8 slots de 30 min; A = alocar/mover blocos; S = lista de tarefas e restrições. Ambiente: totalmente observável, determinístico, estático, discreto, agente único.
**Representação:** a cada slot livre (6 slots, pois C ocupa os de 16h) atribui-se A, B, D ou ocioso. **Busca exaustiva** (4⁶ = 4096 combinações) com restrições rígidas: A e C hoje, C fixa, sem sobreposição, sem divisão (variante 1) ou com divisão (variante 2).
**Utilidade:** `valor(t) = peso(prioridade: Alta 10, Média 5, Baixa 2) × urgência(hoje 3, amanhã 2, semana 1)`; tarefa concluída soma `valor`; progresso parcial em tarefa de prazo amanhã soma proporcional (se o restante couber amanhã).

**Resultados:**

| Variante | Plano | Utilidade |
|---|---|---:|
| Sem divisão | 14:00–15:30 **A** · 16:00–17:00 **C** · 17:00–18:00 **D** · B não cabe (120 contíguos) | 62,0 |
| Com divisão | 14:00–15:30 **A** · 15:30–16:00 **B** · 16:00–17:00 **C** · 17:00–18:00 **B** (B 90/120; restam 30 min p/ amanhã) | **67,5** |

Justificativas: **D** adiado (baixa prioridade, prazo semana que vem); **B** parcialmente feito hoje porque o prazo é amanhã e a divisão é permitida. A escolha de pesos é uma **decisão de modelagem**: com outros pesos, D poderia entrar.

## 3. Solução com agente LLM
O LLM recebe o texto livre, **extrai as tarefas em JSON** (duração, prioridade, prazo, compromisso fixo), propõe um plano e o explica; chama ferramentas (calendário, validador). Em `agente_llm.py` a arquitetura é **neuro-simbólica**: LLM interpreta/explica; **verificador** valida o JSON; **planejador clássico** decide; **validador** confere o plano (sem sobreposição, tarefas “hoje” completas, fixa respeitada).

## 4. Comparação

| Dimensão | Agente clássico (AIMA) | Agente baseado em LLM |
|---|---|---|
| Entrada | Estruturada (tarefas, durações, restrições formalizadas) | **Linguagem natural** livre, ambígua, incompleta |
| Representação | Estados, ações, utilidade explícitos | Implícita nos pesos; contexto do *prompt* |
| Raciocínio | Busca/otimização com **garantias** (completude, otimalidade) | Gera texto plausível por padrões; sem garantia formal |
| Restrições rígidas | Impostas por construção | “Seguidas” por instrução; podem ser violadas (sobreposição, aritmética de horários) |
| Utilidade/prioridades | Função explícita, auditável | Preferências implícitas; instáveis entre execuções |
| Adaptação a novos casos | Exige reprogramar/modelar | Generaliza com poucos exemplos; flexível |
| Explicabilidade | Trace de busca, decisões verificáveis | Explicações fluentes mas **post hoc** (podem não refletir o processo real) |
| Determinismo/custo | Determinístico, barato | Estocástico, mais caro e lento |
| Interação | Interface rígida | Diálogo, esclarecimentos, tom natural |

## 5. Em que situações o LLM oferece vantagens?
* **Interpretar pedidos em linguagem natural**: no cenário, “urgente”, “até amanhã”, “só na próxima semana” viram parâmetros sem formulário.
* **Lidar com informação incompleta/ambígua** (“reunião de pesquisa” sem horário) pedindo esclarecimento.
* **Conhecimento de senso comum** (“preparar aula” costuma exigir mais tempo que “revisar artigo”; evitar agendar correção após reunião cansativa).
* **Flexibilidade de ferramentas**: chamar calendário, e-mail, planilhas via *function calling*.
* **Explicar e negociar** o plano em linguagem natural; replanejar quando o usuário muda de ideia.
* **Prototipação rápida** sem modelar todo o domínio.

## 6. O que ainda depende de raciocínio/planejamento/verificação explícitos?
* **Garantia de restrições rígidas** (compromissos fixos, sem sobreposição, prazos): exige **verificador/solver** (CSP, busca, SMT).
* **Otimização** (maximizar utilidade): LLMs podem sugerir planos razoáveis, mas não provam otimalidade.
* **Aritmética e tempo** (somar durações, janelas): erros frequentes sem ferramenta.
* **Consistência e reprodutibilidade** (auditoria, conformidade): usar utilidade explícita e logs.
* **Planejamento de longo horizonte e replanejamento sob falhas**: requer representação de estado, memória e monitoramento (ciclo sentir–planejar–agir).
* **Justificativa fiel**: o trace do planejador, não a narrativa do LLM, é a explicação confiável.

**Conclusão:** a melhor prática é **híbrida**: LLM como interface e “tradutor” (linguagem ↔ representação formal) e **mecanismos clássicos** como núcleo de decisão e verificação.
