# Questão 13 — Ensaio: a arquitetura Transformer

Arquivos: `transformer_demo.py` (exemplo numérico em NumPy: parte A com pesos aleatórios e parte B com pesos desenhados à mão) e `resultados.txt` (saída).

> **Fonte:** o ensaio se apoia no vídeo "Encoders vs Decoders Explained: How Transformers Really Work (With Real Attention Math)" (canal implementitatai; https://youtu.be/bVVm68KTD2M), em "Attention Is All You Need" (Vaswani et al., 2017) e na literatura padrão. As partes que seguem o vídeo estão na seção 9.

## 1. Contexto e motivação
Antes de 2017, modelar sequências (tradução, linguagem) era domínio das **RNNs/LSTMs/GRUs**, que leem um token por vez: (i) o estado oculto precisa carregar toda a informação passada (gargalo), (ii) o treino é **sequencial** no tempo e não aproveita bem GPUs, (iii) dependências distantes se diluem (gradientes que somem). O **Transformer** elimina a recorrência: em vez de passar um estado de token em token, cada token **consulta diretamente todos os outros** por um mecanismo de **atenção**. Consequências: treino paralelo sobre toda a sequência, caminho de comprimento 1 entre quaisquer dois tokens e escalabilidade, que é a base de BERT, GPT, T5 e dos LLMs atuais.

## 2. Visão geral
```
 texto -> tokens -> IDs -> embeddings (+ posição)
   -> [ bloco ] x N       bloco = Multi-Head Self-Attention -> Add&Norm -> FFN -> Add&Norm
   -> camada linear + softmax  -> probabilidade de cada token do vocabulário
```
O artigo original tem **encoder** (lê a entrada inteira, atenção bidirecional) e **decoder** (gera a saída com atenção mascarada + **atenção cruzada** sobre a saída do encoder), para tradução. Variantes: só-encoder (BERT: entende/classifica), só-decoder (GPT, LLMs: geram texto), encoder-decoder (T5, tradução).

## 3. Conceitos e componentes
**3.1 Tokenização e embeddings.** O texto é dividido em *tokens* (subpalavras, via BPE/WordPiece/SentencePiece); cada token é um ID inteiro que indexa uma **tabela de embeddings** (matriz `V × d_model`) aprendida. O vetor resultante representa o token isoladamente, sem contexto.

**3.2 Codificação posicional.** A atenção trata a entrada como um *conjunto*: sem posição, "o gato morde o cão" e "o cão morde o gato" teriam as mesmas representações. Soma-se a cada embedding um vetor de posição. No artigo: `PE(pos,2i)=sin(pos/10000^(2i/d))`, `PE(pos,2i+1)=cos(pos/10000^(2i/d))`. Para d = 8 e as posições 0, 1, 2 de "o gato dorme" (valores calculados em `resultados.txt`):

| pos | dim0 (sin) | dim1 (cos) | dim2 | dim3 | … |
|---:|---:|---:|---:|---:|---|
| 0 | 0,000 | 1,000 | 0,000 | 1,000 | … |
| 1 | 0,841 | 0,540 | 0,100 | 0,995 | … |
| 2 | 0,909 | −0,416 | 0,199 | 0,980 | … |

Dimensões iniciais oscilam rápido (distinguem posições vizinhas) e as finais oscilam devagar (distinguem posições distantes). Alternativas modernas: posições aprendidas, **RoPE** (rotação dos vetores Q/K) e ALiBi.

**3.3 Autoatenção (*scaled dot-product attention*).** Cada token gera três vetores por projeções lineares aprendidas: **Query** `q = xW_Q` ("o que estou procurando"), **Key** `k = xW_K` ("o que ofereço") e **Value** `v = xW_V` ("o conteúdo que entrego"). Em forma matricial:

`Atenção(Q,K,V) = softmax( Q·Kᵀ / √d_k ) · V`

`Q·Kᵀ` é uma matriz `n × n`: a linha *i* contém a similaridade do token *i* com todos os tokens. O softmax por linha transforma essas notas em **pesos que somam 1**, e o resultado é uma média ponderada dos Values. A divisão por `√d_k` evita que os produtos escalares cresçam com a dimensão e saturem o softmax (gradientes quase nulos).

**3.4 Multi-head attention.** Em vez de uma só atenção, executam-se `h` cabeças em paralelo, cada uma com seu `W_Q, W_K, W_V` de dimensão `d_k = d_model/h`. Cada cabeça pode captar um tipo de relação (sujeito–verbo, correferência, posição vizinha, sintaxe…). As saídas são concatenadas e projetadas por `W_O`.

**3.5 Residual + LayerNorm.** Cada subcamada é `LayerNorm(x + Subcamada(x))`. A conexão residual deixa o gradiente fluir por dezenas de camadas; o LayerNorm normaliza cada vetor (média 0, variância 1) e estabiliza o treino. (Modelos recentes usam *pre-norm*, normalizando antes da subcamada.)

**3.6 Rede feed-forward (FFN).** MLP aplicada igualmente a cada posição: `d → 4d → d` com ReLU/GELU. A atenção **mistura informação entre tokens**; a FFN **processa cada token** individualmente (e guarda grande parte do "conhecimento factual").

**3.7 Mascaramento.** No decoder, o token *i* não pode ver tokens futuros: antes do softmax, os scores das posições *j > i* viram −∞ (peso 0). Isso permite treinar a previsão do próximo token em todas as posições em paralelo sem "trapacear". **Atenção cruzada:** no decoder de tradução, Queries vêm do decoder e Keys/Values do encoder.

**3.8 Saída.** Uma projeção linear `d_model → |V|` seguida de softmax dá a distribuição do próximo token.

**3.9 Contagem de parâmetros (ordem de grandeza).** Para o modelo-base do artigo (`d_model=512`, `h=8`, `d_ff=2048`): por camada, atenção ≈ 4·512² ≈ 1,05 M parâmetros; FFN ≈ 2·512·2048 ≈ 2,10 M; total ≈ 3,15 M por camada de encoder. Com N = 6 camadas (+ decoder com atenção cruzada + embeddings) chega-se a dezenas de milhões; os LLMs atuais repetem o mesmo padrão com `d_model` na casa de milhares e dezenas ou centenas de camadas.

## 4. Como funciona, com um exemplo: "o gato dorme"
**Parte A (`transformer_demo.py`, pesos aleatórios):** mostra a mecânica completa de um bloco com `d=8`, 2 cabeças com `d_k=4`: embeddings + posição → `Q,K,V` → scores `QKᵀ/√4` (3×3) → softmax por linha → `A·V` → concatenar cabeças e `W_O` → residual + LayerNorm → FFN → residual + LayerNorm → 3 vetores contextuais. Ex.: na cabeça 1, o token "o" distribui 7,7% / 4,1% / **88,2%** da atenção entre (o, gato, dorme). Como os pesos são aleatórios, **os valores não têm significado linguístico**, só ilustram o cálculo.

**Parte B (pesos desenhados à mão, interpretável).** Embeddings de 4 dimensões `[é_artigo, é_substantivo, é_verbo, viés]`: "o" = (1,0,0,1), "gato" = (0,1,0,1), "dorme" = (0,0,1,1). Define-se uma cabeça "sujeito": a **Query de um verbo** procura um substantivo (`W_Q` converte a feature "é verbo" em uma consulta forte) e a **Key de um substantivo** anuncia "sou substantivo". Resultado (de `resultados.txt`):

| Linha (quem pergunta) | o | gato | dorme |
|---|---:|---:|---:|
| o | 0,333 | 0,333 | 0,333 |
| gato | 0,333 | 0,333 | 0,333 |
| **dorme** | 0,053 | **0,894** | 0,053 |

Conferência à mão: score(dorme→gato) = (4·1)/√2 = 2,828; `e^2,828 ≈ 16,9`; peso = 16,9/(16,9 + 1 + 1) ≈ **0,894**. O verbo "encontra" seu sujeito, e a saída de "dorme" passa a conter principalmente o Value de "gato": é assim que o vetor de "dorme" incorpora contexto. Uma cabeça **treinada** aprende pesos desse tipo sozinha, por retropropagação. Com **máscara causal**, a linha de "gato" fica (0,5; 0,5; 0) e a de "o" (1; 0; 0): cada token só enxerga o passado.

## 5. Treinamento
* **Objetivo:** decoders (GPT) minimizam a entropia cruzada da previsão do próximo token em cada posição (*teacher forcing*: a entrada é a sequência real deslocada); encoders (BERT) preveem tokens mascarados.
* **Otimização:** Adam/AdamW com *warm-up* da taxa de aprendizado e decaimento, dropout, regularização por *weight decay*. Tudo é diferenciável, logo treina-se por retropropagação.
* **Escala:** custo dominado por atenção (O(n²·d)) e FFN (O(n·d²)); por isso paralelismo de dados/tensores/pipeline e precisão mista.

## 6. Inferência autorregressiva
O decoder gera **um token por vez**: calcula a distribuição do próximo token, escolhe um (*greedy*, amostragem com temperatura, top-k/top-p), anexa à entrada e repete. Para não recalcular tudo, guarda-se o **KV cache** (Keys e Values já calculados), o que liga este ensaio à Questão 5 (fases *prefill* e *decode*).

## 7. Complexidade e variantes
* A atenção é **O(n²)** em tempo e memória no comprimento *n* do contexto. Mitigações: **FlashAttention** (mesma conta, menos acessos à memória), atenção esparsa/janelas, **MQA/GQA** (compartilhar K/V entre cabeças para reduzir o KV cache), modelos de contexto longo.
* Além de texto: **ViT** (imagens divididas em *patches* viram tokens), áudio, proteínas e modelos multimodais.

## 8. Limitações
Custo quadrático do contexto; fome de dados e de computação; alucinação (o modelo otimiza plausibilidade, não verdade); dificuldade de garantir raciocínio simbólico e restrições rígidas (por isso agentes combinam LLM com verificadores, como na Questão 12); interpretabilidade parcial (as cabeças nem sempre correspondem a conceitos humanos).

## 9. O que o vídeo acrescenta
**9.1 As três famílias.** *Encoder-only* (BERT): atenção **bidirecional**, cada palavra olha para a esquerda e para a direita; ideal para compreensão (classificação, busca semântica). *Decoder-only* (GPT/ChatGPT): atenção **causal/mascarada**, cada token só vê os anteriores; o prompt também é lido assim antes de gerar token a token; ideal para geração e conversa. *Encoder-decoder* (Transformer original, T5): o encoder lê a origem e o decoder gera o destino consultando o encoder por **atenção cruzada**; usado em tradução e resumo.

**9.2 Preparação dos dados.** Tokenização (IDs) → *embeddings* (palavras de sentido parecido ficam próximas no espaço) → informação posicional, para distinguir "dog bites man" de "man bites dog".

**9.3 Encoder.** Pilha de camadas idênticas (6 no artigo original), cada uma com *self-attention*, *Add & Normalize* (a residual soma a entrada ao resultado para não perder informação; a normalização mantém os valores estáveis) e rede *feed-forward*. A autoatenção ajuda, por exemplo, a saber a qual substantivo o pronome "it" se refere.

**9.4 Analogia da biblioteca.** A **Query** é a sua pergunta, a **Key** é a etiqueta de cada livro e o **Value** é o conteúdo do livro. Os três vêm de matrizes de pesos aprendidas no treinamento.

**9.5 Exemplo numérico do vídeo** (parte C de `transformer_demo.py`): Query = 1, com dois livros de Keys 1 e 0 → produtos escalares **1 e 0**; dividindo por √2 ≈ 1,41 → **0,71 e 0**; softmax → pesos **0,67 e 0,33**; com Values [2, 0] e [0, 2], a saída ponderada é **[1,34; 0,66]**. Conferência: e^0,71 ≈ 2,03; 2,03/(2,03+1) = 0,67. *(Os Values [2,0] e [0,2] foram escolhidos na reconstrução do exemplo; reproduzem o resultado [1,34; 0,66].)*

**9.6 Multi-head e decoder.** O artigo usa 8 cabeças em paralelo para captar relações diferentes ao mesmo tempo. O decoder (no modelo completo) tem três blocos: *masked self-attention*, *cross-attention* (queries do decoder; keys e values do encoder) e *feed-forward*. Na máscara causal, as posições futuras recebem −∞ antes do softmax e ficam com peso zero (o modelo não "espia o futuro"). Modelos só-decoder não têm a atenção cruzada.

**9.7 Treinamento.** *Teacher forcing*: a resposta correta, deslocada uma posição, é a entrada, e todas as posições são previstas em paralelo sob a máscara. Distinção do vídeo: os **pesos de atenção** definem para onde olhar; as **probabilidades de saída** definem qual palavra vem a seguir.

## Referências
Vaswani, A. et al. *Attention Is All You Need*. NeurIPS 2017. · Russell & Norvig, *Artificial Intelligence: A Modern Approach*, 4ª ed. (capítulos sobre redes neurais profundas e PLN). · Alammar, J. *The Illustrated Transformer* (texto introdutório).
