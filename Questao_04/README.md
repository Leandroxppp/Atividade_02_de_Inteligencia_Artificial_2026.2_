# Questão 4 — Taxonomia de agentes (Russell & Norvig, cap. 2) com PEAS

Convenção das propriedades: **Obs.** = totalmente (T) ou parcialmente (P) observável · **Det.** = determinístico (D), estocástico (E) · **Epis.** = episódico (Ep) ou sequencial (Seq) · **Est.** = estático (Es), dinâmico (Din), semi-dinâmico (Sd) · **Disc.** = discreto (Dc) ou contínuo (Ct) · **Ag.** = um agente (1) ou multiagente (M).

## 1) Agente reativo simples (regras condição→ação, sem memória; decide só pela percepção atual)

| | **Termostato on/off** | **Filtro de spam por palavras-chave** |
|---|---|---|
| **P** | Manter temperatura próxima do alvo; baixo consumo | Bloquear spam, minimizar falsos positivos |
| **E** | Cômodo, clima, usuário | Caixa de entrada, remetentes, spammers |
| **A** | Ligar/desligar aquecedor/AC | Mover mensagem para spam / deixar passar |
| **S** | Sensor de temperatura | Texto do e-mail, cabeçalho |
| Propriedades | Obs. T (da variável medida) · Det. E (ruído) · Epis. Seq (fraco) · Est. Din · Disc. Ct · Ag. 1 | Obs. T (texto) · Det. D · **Epis. Ep** · Est. Es (por mensagem) · Disc. Dc · Ag. M (adversarial: spammers) |
| Regra | SE T < alvo−1 ENTÃO ligar | SE contém “prêmio grátis” ∧ remetente desconhecido ENTÃO spam |

## 2) Agente baseado em modelo (mantém estado interno/modelo do mundo para lidar com observabilidade parcial)

| | **Robô aspirador com mapa** | **Assistente de permanência em faixa/ACC** |
|---|---|---|
| **P** | Cobertura limpa do ambiente, bateria, evitar quedas | Segurança, conforto, velocidade desejada |
| **E** | Casa, móveis, pessoas, pets | Rodovia, veículos, sinalização |
| **A** | Rodas, escova, sucção, retorno à base | Direção, acelerador, freio |
| **S** | Choque, infravermelho, odometria, LIDAR | Câmera, radar, velocímetro |
| Estado interno | Mapa (células limpas/obstáculos), posição estimada | Posição/velocidade estimada dos veículos vizinhos, inclusive os temporariamente ocultos |
| Propriedades | Obs. P · Det. E · Seq · Din · Ct (mapa discretizado) · Ag. 1 | Obs. P · Det. E · Seq · Din · Ct · Ag. M |

## 3) Agente baseado em objetivo (escolhe ações que levam a um estado-meta; usa busca/planejamento)

| | **Navegação GPS** | **Robô de armazém (separação de itens)** |
|---|---|---|
| **P** | Chegar ao destino (e, secundariamente, tempo) | Entregar todos os itens do pedido |
| **E** | Malha viária, tráfego, regras de trânsito | Prateleiras, outros robôs, pedidos |
| **A** | Instruções de rota/virar | Mover, pegar, depositar |
| **S** | GPS, mapa, informações de tráfego | Câmera, QR no chão, inventário |
| Objetivo | Estar em `destino` | Pedido completo na estação de embalagem |
| Propriedades | Obs. T (mapa) / P (tráfego) · Det. E · Seq · Din · Disc. (grafo) · Ag. M | Obs. P · Det. E · Seq · Din · Disc. (grade) · Ag. M |

## 4) Agente baseado em utilidade (maximiza utilidade esperada quando há objetivos conflitantes ou incerteza)

| | **Roteirizador de entregas (tempo, custo, risco)** | **Gestor de carteira de investimentos** |
|---|---|---|
| **P** | Maximizar utilidade = f(prazo, custo, risco de atraso) | Maximizar retorno ajustado ao risco da pessoa |
| **E** | Cidade, trânsito, clientes, frota | Mercado, notícias, taxas, regras fiscais |
| **A** | Atribuir entregas/rotas, replanejar | Comprar/vender/rebalancear |
| **S** | GPS, tráfego, pedidos | Cotações, indicadores |
| Utilidade | U = −w₁·tempo − w₂·custo − w₃·P(atraso) | E[U(riqueza)] com aversão a risco (função côncava) |
| Propriedades | Obs. P · Det. E · Seq · Din · Ct · Ag. M | Obs. P · Det. **E** · Seq · Din · Ct · Ag. M |

## 5) Agente adaptativo (com aprendizagem: elemento de desempenho, crítico, elemento de aprendizagem, gerador de problemas)

| | **Recomendador de conteúdo (streaming)** | **Agente jogador de xadrez/Go por RL (tipo AlphaZero)** |
|---|---|---|
| **P** | Engajamento/satisfação de longo prazo do usuário | Vencer partidas |
| **E** | Usuários, catálogo | Tabuleiro, adversário |
| **A** | Exibir/ordenar recomendações | Jogar um lance |
| **S** | Cliques, tempo de exibição, avaliações | Posição do tabuleiro |
| Aprendizagem | Crítico = feedback implícito; atualiza o modelo; explora conteúdos novos (gerador de problemas) | Crítico = resultado final; atualiza rede de política/valor por *self-play* |
| Propriedades | Obs. P (intenção do usuário oculta) · Det. E · Seq · Din · Disc. · Ag. M | Obs. T · Det. D (regras) · Seq · Est. (turno) · Disc. · Ag. M (2 jogadores, soma zero) |

**Observação:** as categorias são cumulativas — um agente de utilidade geralmente também tem modelo e objetivo; e qualquer um dos tipos pode ser tornado adaptativo acrescentando um componente de aprendizagem.

## Complementos
**Propriedade "conhecido × desconhecido" (R&N):** refere-se ao conhecimento do agente sobre as "leis" do ambiente. Termostato, filtro de spam, xadrez/Go e GPS (mapa) são ambientes **conhecidos** (regras/mapa dados); aspirador sem mapa prévio, ACC em rodovia nova, carteira de investimentos e recomendador são **parcialmente desconhecidos**: o agente precisa explorar ou aprender o modelo de transição, o que reforça a necessidade de modelo e de aprendizagem nesses casos.

**Estrutura de cada categoria (esquemas):**
```
Reativo simples:  percepção ──► [regras condição→ação] ──► ação
Baseado em modelo: percepção ──► [atualiza estado com modelo do mundo] ──► [regras] ──► ação
Baseado em objetivo: estado + modelo ──► [simula "se eu fizer a, o que acontece?"] ──► busca/planejamento até a meta ──► ação
Baseado em utilidade: estado + modelo ──► [prevê resultados] ──► [utilidade esperada U(s)] ──► ação de maior U esperada
Adaptativo: elemento de desempenho (um dos acima) + crítico (feedback) + elemento de aprendizagem + gerador de problemas
```
**Por que cada exemplo está na sua categoria:** o termostato e o filtro decidem só com a percepção atual (sem estado); o aspirador e o ACC **precisam de estado** porque não veem tudo ao mesmo tempo; o GPS e o robô de armazém têm um **estado-meta** explícito e buscam um caminho até ele; o roteirizador e o gestor de carteira escolhem entre resultados que **conflitam** (tempo × custo × risco; retorno × risco), logo exigem utilidade; o recomendador e o AlphaZero **melhoram com a experiência** (aprendem).
