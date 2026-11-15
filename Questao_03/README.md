# Questão 3 — ELIZA (Weizenbaum, 1966)

Arquivos: `eliza.py` (implementação em português com *trace*), `dialogo_trace.txt` (saída). Execute `python eliza.py` (demo com trace) ou `python eliza.py --chat` (conversa).

## 1. Resumo
ELIZA foi escrita por Joseph Weizenbaum (MIT, 1966). O script mais famoso, **DOCTOR**, imita um psicoterapeuta **rogeriano**, que devolve ao paciente o que ele disse, sem trazer conhecimento próprio. Não entende linguagem natural: faz **casamento de padrões e substituição de texto**. Principais funcionalidades:
* **Palavras-chave com prioridade (rank)**: escolhe a de maior rank na frase.
* **Regras de decomposição/remontagem**: padrão (ex.: `* eu me sinto *`) e modelos de resposta (`Por que você se sente (2)?`), usados em **rodízio** para não repetir.
* **Reflexão de pronomes** (eu↔você, meu↔seu).
* **Memória**: guarda frases com “meu/minha” para reutilizar depois.
* **Respostas genéricas** quando nada casa (“Por favor, continue.”).
* Separação da linguagem (script editável) e do motor (independência de domínio).

## 2. Como funciona (algoritmo)
```
repita:
  1. lê a frase; converte para minúsculas e corta na primeira pontuação que já tenha palavra-chave
  2. procura palavras-chave; ordena por rank; pega a de maior rank (K)
  3. para cada regra de decomposição de K, em ordem:
        se a frase casa com o padrão -> captura os fragmentos
  4. reflete os pronomes no fragmento capturado (eu->você ...)
  5. escolhe a próxima remontagem (rodízio) e substitui {1} pelo fragmento
  6. se K = "meu/minha": guarda uma frase na MEMÓRIA
  7. se nenhuma palavra-chave casou: se há memória, usa uma frase guardada; senão responde NENHUMA (genérica)
```
Regras de exemplo (`eliza.py`): `me sinto` (rank 4): padrão `.*me sinto (.*)` → `Por que você se sente {1}?`; `computador` (rank 50); `meu` (rank 2) com memória.

## 3. Diálogo com explicação de cada resposta (saída real do programa)

| # | Usuário → ELIZA | Regra disparada | Avaliação técnica |
|---|---|---|---|
| 1 | “Olá, estou muito cansado ultimamente.” → “Há quanto tempo você está muito cansado ultimamente?” | chave `estou` (rank 3), decomposição `.*estou (.*)`, fragmento “muito cansado ultimamente” | ✅ **Boa**: o padrão de estado + a remontagem funcionam; “olá” é ignorado (sem palavra-chave) |
| 2 | “Eu me sinto sozinho no trabalho.” → “Por que você se sente sozinho no trabalho?” | chave `me sinto` (rank 4) | ✅ **Boa**: troca “eu me sinto” por “você se sente” via modelo |
| 3 | “Meu chefe não me escuta.” → “Por que você diz que seu chefe não **você** escuta?” | chave `meu` (rank 2); reflexão trocou `me`→`você` | ❌ **Falha**: a reflexão de pronomes é mecânica e quebra a gramática (“não me escuta”) |
| 4 | “Eu odeio meu chefe” → “Seu chefe é importante para você?” | `meu`, remontagem #2 | ⚠️ **Fraca**: ignora o verbo “odeio” (o sentimento); responde ao objeto |
| 5 | “Eu lembro da minha infância no interior.” → “Você costuma pensar em **da** sua infância no interior?” | chave `lembro` (rank 5) | ❌ **Falha**: o recorte do fragmento não removeu a preposição “da” |
| 6 | “Sonhei com minha mãe ontem.” → “Fale mais sobre sua família.” | chave `mãe` (rank 5) ganha de `sonho` (rank 4, aliás “sonhei” nem casa) | ⚠️ **Interessante/falha**: o ranking produz o gancho “família” (comportamento típico do DOCTOR), mas descarta o sonho |
| 7 | “O tempo está bonito hoje.” → “Antes você disse que meu chefe não me escuta. Isso tem a ver…?” | nenhuma chave → **MEMÓRIA** | ✅/⚠️ **Mecanismo bom** (retomada de assunto) mas o texto guardado **não foi refletido** (“meu chefe… me”) |
| 8 | “Você é um robô?” → “Estamos falando de você, não de mim.” | chave `você` (rank 1) | ✅ Desvia como um terapeuta; ❌ nunca responde a pergunta |
| 9 | “Não estou triste, estou irritado.” → “Você veio aqui porque está **triste**?” | cortou na vírgula; casou `estou triste` | ❌ **Falha grave**: ignora a **negação** e a correção do usuário (sem semântica) |
| 10 | “Não consigo dormir.” → “Você acha mesmo que não consegue dormir?” | `não consigo` (rank 3) | ✅ **Boa** (conjugação já embutida no modelo) |
| 11 | “Eu estou lendo sobre computador e IA.” → “Os computadores te preocupam?” | `computador` (rank 50) vence `estou` | ⚠️ Prioridade correta pelo script, mas ignora “lendo”: sem contexto |
| 12 | “Qual é o sentido da vida?” → memória reaproveitada fora de contexto | nenhuma chave | ❌ A resposta de memória é sem relação com a pergunta |

**Limitações estruturais:** sem compreensão semântica, sem estado do diálogo além da memória, sem tratamento de negação, concordância verbal e ambiguidade; depende de palavras literais; dá a **ilusão** de compreensão (“efeito ELIZA”).

## 4. Evolução: ELIZA (1966) → PARRY (1972) → AIML/ALICE (anos 1990-2000)

| | **ELIZA (1966)** | **PARRY (1972)** | **AIML / ALICE (1995–2001+)** |
|---|---|---|---|
| Autor | J. Weizenbaum, MIT | K. Colby, Stanford | R. Wallace (Alicebot/ALICE) |
| Papel simulado | Psicoterapeuta rogeriano | **Paciente** com esquizofrenia paranoide | Conversa geral |
| Mecanismo | Palavras-chave, decomposição/remontagem, memória simples | Padrões + **modelo de estado interno** (variáveis afetivas como medo, raiva, desconfiança que variam durante a conversa), delírios e tópicos preferidos | **Categorias** `<pattern>/<template>` em XML (AIML); uso de `<srai>` (redução simbólica/recursão), `<that>` (resposta anterior), `<topic>`, variáveis `<set>/<get>`; dezenas de milhares de categorias |
| Estado | Quase nenhum | Sim (emoções, crenças, histórico) | Predicados e contexto limitados (topic/that) |
| Conhecimento | Nenhum | Delírios/“mafioso”, hospital, apostas | Grande base manual de respostas |
| Avaliação | Efeito ELIZA | Teste do tipo Turing: psiquiatras tiveram dificuldade de distinguir transcrições de PARRY e de pacientes reais | Concursos tipo Loebner (ALICE venceu várias edições) |
| Ganho | Mostrou o poder da ilusão | Introduziu **personalidade/estado afetivo** | **Padronização, escala e comunidade** (linguagem aberta e reutilizável) |
| Limite | Sem entendimento | Domínio restrito, regras manuais | Ainda reativo; sem aprendizado nem raciocínio |

Fio condutor: ELIZA (reativo, sem estado) → PARRY (**com estado interno**, “agente baseado em modelo”) → AIML (**escala/padronização**) → chatbots neurais e LLMs (aprendizagem de dados). 

## 5. Pesquisa complementar (fontes conferidas)

### 5.1 Como o ELIZA original representava as regras
O programa original foi escrito em **MAD-SLIP** no MIT e descrito em Weizenbaum, *CACM* 9(1), 1966, pp. 36–45. A ideia central é separar o **motor** do **script** (dados). Cada palavra-chave tem um **rank** e uma lista de regras do tipo *decomposição → remontagem*, escritas com um padrão em que `0` casa com qualquer sequência de palavras e os números nas remontagens indicam qual fragmento reinserir. O exemplo clássico do artigo:
```
decomposição:  (0 YOU 0 ME)          "It seems that you hate me"
remontagem:    (WHAT MAKES YOU THINK I 3 YOU)   ->  "What makes you think I hate you"
```
Aqui `0 YOU 0 ME` divide a frase em 4 partes (1 = antes de YOU, 2 = YOU, 3 = entre YOU e ME, 4 = ME); a remontagem usa a parte 3 ("hate"). A `eliza.py` deste trabalho reproduz a mesma lógica com expressões regulares e grupos `{1}`.

### 5.2 PARRY (1972) e o encontro ELIZA × PARRY
* **PARRY** foi escrito em 1972 pelo psiquiatra **Kenneth Colby** (Stanford), em MLisp; se o ELIZA era uma imitação irônica de um terapeuta rogeriano, o PARRY simulava um **paciente com esquizofrenia paranoide**, e era descrito como "ELIZA com atitude". Tem um **modelo interno de estado afetivo** (variáveis como medo, raiva e desconfiança) que sobe ou desce conforme o que o interlocutor diz, e uma estratégia de conversa própria (desvia para os seus delírios, p. ex., apostas e a "máfia").
* **Validação:** Colby et al. (1972) fizeram testes do tipo Turing: psiquiatras que liam transcrições de pacientes reais e do PARRY não conseguiam distingui-los acima do acaso (fontes secundárias citam cerca de 48% de acerto).
* **Encontro:** os dois programas conversaram pela ARPANET. Há a transcrição da sessão de **18/09/1972** publicada por Vint Cerf como **RFC 439** ("PARRY Encounters the DOCTOR") e a demonstração pública na ICCC, em Washington, em outubro de 1972. Um detalhe histórico: o "DOCTOR" dessa conversa era provavelmente uma versão posterior em Lisp (BBN, de Bernie Cosell), e não o ELIZA original em MAD-SLIP. A conversa mostra bem os limites: o PARRY diz "People get on my nerves" e o ELIZA responde com perguntas genéricas ("I am not sure I understand you"), sem compreensão de nenhum lado.

### 5.3 AIML e A.L.I.C.E.
* **A.L.I.C.E.** (*Artificial Linguistic Internet Computer Entity*) foi criada por **Richard Wallace** e entrou "em operação" em 23/11/1995; reescrita em Java a partir de 1998. Ganhou o **Prêmio Loebner em 2000, 2001 e 2004**. Wallace a descreve como um ELIZA fortemente ampliado e baseado em milhares de regras.
* **AIML** (*Artificial Intelligence Markup Language*) é um dialeto de XML desenvolvido por Wallace e uma comunidade de software livre (mais de 500 colaboradores) entre 1995 e ~2002; versão estável **1.0.1**. A unidade de conhecimento é a `<category>` com um `<pattern>` (entrada, com curingas `*` e `_`) e um `<template>` (resposta):
```xml
<category><pattern>MEU NOME É *</pattern>
  <template>Prazer, <set name="nome"><star/></set>!</template></category>
<category><pattern>QUAL É O MEU NOME</pattern>
  <template>Seu nome é <get name="nome"/>.</template></category>
<category><pattern>COMO VOCÊ SE CHAMA</pattern>
  <template><srai>QUAL É O SEU NOME</srai></template></category>   <!-- sinonímia por redução simbólica -->
```
* Recursos que o ELIZA não tinha: `<srai>` (**redução simbólica**: reescreve a entrada para outra já conhecida, o que permite sinônimos e recursão), `<that>` (considera a **última resposta do bot** no casamento), `<topic>` (**contexto de assunto**), `<set>/<get>` (variáveis que lembram dados do usuário) e condicionais `<condition>`. O casamento de padrões usa uma árvore (*Graphmaster*) que torna a busca rápida mesmo com dezenas de milhares de categorias. Servidores como o **Pandorabots** (2002) hospedam bots AIML.

### 5.4 Quadro-resumo das evoluções de funcionalidade
| Funcionalidade | ELIZA 1966 | PARRY 1972 | AIML/ALICE 1995+ |
|---|---|---|---|
| Papel | terapeuta rogeriano | paciente paranoide | conversação geral |
| Entendimento | nenhum (padrões) | nenhum, mas com **modelo de crenças/emoções** | nenhum (padrões em larga escala) |
| Estado interno | memória simples de frases | **variáveis afetivas** e delírios que mudam com o diálogo | variáveis (`set/get`), `that`, `topic` |
| Reescrita/sinônimos | não | limitada | **`<srai>`** (recursiva) |
| Representação do conhecimento | script em MAD-SLIP/LISP | regras + estratégia em MLisp | **XML aberto e reutilizável** |
| Escala | dezenas de regras | centenas de regras/padrões | dezenas de milhares de categorias |
| Aprendizagem automática | nenhuma | nenhuma | nenhuma (curadoria manual pela comunidade) |
| Avaliação | efeito ELIZA | teste tipo Turing com psiquiatras | Prêmio Loebner |

**Fio condutor:** ELIZA mostrou que a *ilusão* de compreensão basta em certos contextos; PARRY acrescentou **estado interno e personalidade**; AIML/ALICE trouxe **padronização, escala e comunidade**; só com modelos neurais e LLMs surge a **aprendizagem a partir de dados**, que nenhum dos três tinha.

**Referências:** Weizenbaum, J. (1966), *ELIZA — a computer program for the study of natural language communication between man and machine*, CACM 9(1):36–45. · Colby, K. M.; Hilf, F. D.; Weber, S.; Kraemer, H. (1972), *Turing-like indistinguishability tests for the validation of a computer simulation of paranoid processes*, Artificial Intelligence 3. · Cerf, V. (1973), *PARRY Encounters the DOCTOR*, RFC 439. · Wallace, R. S. (2009), *The Anatomy of A.L.I.C.E.*, in Epstein et al. (eds.), *Parsing the Turing Test*, Springer, pp. 181–210. · Páginas da Wikipédia (PARRY, A.L.I.C.E., AIML) e do projeto ELIZAGEN, usadas só para conferir datas.
