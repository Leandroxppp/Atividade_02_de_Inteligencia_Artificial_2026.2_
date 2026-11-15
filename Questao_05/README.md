# Questão 5 — Resumo estendido: “What is LLM Inference? How AI Models Generate Responses” (IBM Technology, Grace Ableidinger)

> **Fonte:** vídeo "What Is LLM Inference? How AI Models Generate Responses" (IBM Technology, ≈7 min; https://www.youtube.com/watch?v=615-yWyS1n0). O resumo segue a ordem do vídeo (00:00 o que é inferência; 01:15 motores de inferência; 01:43 do API ao modelo; 02:15 tokenização; 02:59 roteamento para GPU; 03:30 *continuous batching*; 04:23 *prefill* e KV cache; 05:24 *decode*; 06:18 métricas TTFT e ITL; 06:59 pipeline completo), com base no conteúdo do vídeo e em complementos técnicos identificados nas seções 9–11. Extensão: ≈1.450 palavras (cerca de 3 páginas; limite: 6).

## 1. O que é inferência de LLM
Treinar um LLM de fronteira custa centenas de milhões de dólares e leva meses, e produz apenas um conjunto estático de **pesos** (números na memória): o modelo, por si só, não faz nada. **Inferência** é o processo de usar esses pesos para, dado um *prompt*, gerar uma resposta em tempo real. Toda resposta começa com bem mais do que o prompt: há tokenização, filas, agendamento em GPU, cache e geração token a token. O treinamento acontece uma vez; a inferência acontece **a cada mensagem enviada**, por isso, ao longo do tempo, ela costuma custar mais que o treinamento, e otimizar a velocidade e a eficiência do atendimento é essencial. O vídeo mostra como pesos estáticos viram respostas em tempo real.

## 2. Motores de inferência
Um **inference engine/serving system** (o vídeo cita vLLM, Ollama e llama.cpp; também TensorRT-LLM e TGI) fica entre a API e o modelo. Ele carrega os pesos, gerencia memória da GPU, recebe muitas requisições simultâneas, organiza em lotes, executa o modelo e devolve os tokens (geralmente em *streaming*). Geralmente expõe um **endpoint compatível com a API da OpenAI**, o que permite trocar o modelo sem reescrever a aplicação. Seu objetivo é equilibrar **latência** (rapidez para um usuário) e **vazão/throughput** (quantos usuários por GPU, custo).

## 3. Da requisição ao modelo
1. O cliente chama a **API** (prompt + parâmetros: temperatura, `max_tokens`, etc.).
2. Ao chegar ao data center, a requisição é **autenticada** (chave de API ou token) e passa por limites e **fila**.
3. Um **roteador de inferência** avalia o tamanho e o conteúdo do prompt e o envia ao hardware (GPU) mais adequado e disponível naquele momento; o **scheduler** decide quando ela roda.
4. O modelo gera os tokens, que voltam ao cliente.

## 4. Tokenização
O texto é quebrado em **tokens** (subpalavras, via BPE ou similar) e cada token vira um **ID inteiro** do vocabulário; em seguida vira vetor (*embedding*). O modelo só “enxerga” IDs. Consequências práticas: a cobrança e o limite de contexto são medidos em tokens, então a tokenização determina o custo do prompt; vocabulários maiores usam menos tokens por mensagem, mas exigem mais capacidade computacional no treinamento; e a mesma frase gera números diferentes de tokens em idiomas diferentes.

## 5. Roteamento para GPU e *continuous batching*
LLMs são grandes (bilhões de parâmetros) e a GPU é eficiente com muito paralelismo. Processar uma requisição por vez desperdiça hardware. O **batching estático** espera um lote completo e sofre com requisições de tamanhos diferentes (as curtas esperam as longas). O ***continuous (in-flight) batching*** admite novas requisições e libera as terminadas **a cada passo de geração**, mantendo a GPU sempre ocupada e aumentando muito o throughput.

## 6. Duas fases: *prefill* e *decode*
**Prefill:** o modelo processa **todo o prompt em paralelo**, calcula os estados da atenção e produz o primeiro token. É limitado por **computação** (compute-bound). Aqui nasce o **KV cache**: os vetores *Key* e *Value* de cada token em cada camada são guardados.

**KV cache:** como a atenção de cada novo token precisa de K e V de todos os anteriores, recalculá-los a cada passo seria quadrático. Com o cache, reaproveita-se tudo e calcula-se só o novo token. O custo é **memória** (cresce com o contexto, nº de camadas e de requisições simultâneas), o que limita o tamanho do lote e do contexto.

**Decode:** geração **autorregressiva**: a cada passo o modelo calcula uma distribuição de probabilidade sobre o vocabulário para o próximo token, escolhe um (por *greedy*, ou amostragem com temperatura/top-k/top-p), anexa à sequência, atualiza o KV cache e repete até um token de fim ou `max_tokens`. É limitado pela **largura de banda de memória** (memory-bound), pois cada passo lê todos os pesos para gerar um único token por sequência.

## 7. Métricas de latência
* **TTFT (Time To First Token):** tempo até o primeiro token; dominado por fila + *prefill*; cresce com prompts longos.
* **ITL (Inter-Token Latency)** (ou TPOT): intervalo entre tokens seguintes; dominado pelo *decode*; define a “velocidade de digitação” percebida.
* **Latência total ≈ TTFT + (nº de tokens − 1) × ITL**; e **throughput** (tokens/s do sistema).
Há *trade-off*: lotes maiores aumentam o throughput, mas podem elevar TTFT/ITL individuais.

## 8. Pipeline completo
Prompt → API/fila → tokenização → roteamento/agendamento (continuous batching) → **prefill** (gera KV cache e 1º token) → **decode** iterativo (um token por passo, reutilizando o cache) → detokenização e *streaming* ao usuário. Otimizações comuns: quantização, PagedAttention, *prefix caching*, *speculative decoding*, paralelismo de tensores.

## 9. Exemplos numéricos (ordens de grandeza, feitos por mim para ilustrar; não são falas do vídeo)
**9.1 Tamanho do KV cache.** Para um modelo estilo "7B" (32 camadas, `d_model=4096`, precisão fp16 = 2 bytes), cada token guarda K e V em cada camada: `2 × 32 × 4096 × 2 B = 524 288 B ≈ 0,5 MB por token`. Um contexto de 4 096 tokens ocupa ≈ **2 GiB por sequência**. Em uma GPU de 80 GB, descontando ≈ 14 GB de pesos (7 B × 2 B), sobram ≈ 66 GB, ou seja, cerca de **30 sequências simultâneas** de 4 k tokens. Por isso o KV cache, e não a computação, costuma limitar o tamanho do lote.

**9.2 Por que o decode é limitado por memória.** A cada token gerado a GPU lê todos os pesos (≈ 14 GB). Com ≈ 2 TB/s de largura de banda, só ler os pesos leva ≈ 7 ms, ou seja, no máximo ≈ 140 tokens/s por sequência com lote 1, mesmo que o cálculo seja instantâneo. Atender várias requisições no mesmo passo **reaproveita a mesma leitura de pesos**, e daí vem o ganho do batching. Já o *prefill* processa o prompt inteiro em paralelo: ≈ `2 × 7 B = 14 GFLOP` por token, então um prompt de 1 000 tokens custa ≈ 14 TFLOP, que ocupa bem as unidades de cálculo (*compute-bound*).

**9.3 Batching estático × contínuo.** Três requisições geram 10, 50 e 200 tokens. No lote **estático**, o lote só termina quando a de 200 tokens acaba: são 3 × 200 = 600 "posições-passo" reservadas para 260 úteis → **43% de utilização**. No lote **contínuo**, a posição liberada aos 10 e aos 50 passos é preenchida por novas requisições, e a utilização se aproxima de 100%.

**9.4 Latência total.** `latência ≈ TTFT + (n − 1) × ITL`. Com TTFT = 0,4 s, ITL = 25 ms e 200 tokens: 0,4 + 199 × 0,025 ≈ **5,4 s**. Reduzir o prompt melhora o TTFT; reduzir a carga do servidor ou o tamanho do modelo melhora o ITL; o usuário percebe o ITL como "velocidade de digitação".

## 10. Parâmetros de geração (decode)
| Parâmetro | Efeito |
|---|---|
| *greedy* | escolhe sempre o token mais provável; determinístico, pode repetir |
| `temperature` | divide os *logits* antes do softmax; < 1 deixa a distribuição mais concentrada, > 1 mais aleatória |
| `top-k` / `top-p` | restringe a amostragem aos k tokens mais prováveis ou ao menor conjunto com probabilidade acumulada p |
| `max_tokens` / token de fim | critérios de parada |

## 11. Principais otimizações de inferência
| Técnica | Ideia | Ganho |
|---|---|---|
| Continuous batching | admitir/liberar requisições a cada passo | throughput |
| PagedAttention | KV cache em blocos (como memória virtual) | menos fragmentação, mais requisições simultâneas |
| Prefix caching | reaproveitar o KV cache de prompts com prefixo comum | menor TTFT |
| Quantização (int8/int4) | pesos com menos bits | menos memória e leitura por token |
| Speculative decoding | um modelo pequeno propõe vários tokens e o grande os verifica de uma vez | menor ITL sem mudar a distribuição de saída |
| Paralelismo de tensores/pipeline | dividir o modelo entre GPUs | permite modelos grandes |

## 12. Conclusão
A inferência é um problema de **engenharia de sistemas** tanto quanto de IA: a qualidade vem dos pesos, mas custo, velocidade e escala vêm de tokenização eficiente, batching contínuo, gestão de KV cache e escolha cuidadosa das métricas TTFT/ITL.
