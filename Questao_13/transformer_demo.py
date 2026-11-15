"""Questão 13 — Passo a passo numérico de UM bloco Transformer (encoder) em NumPy, para a frase 'o gato dorme' (3 tokens).
Mostra: embeddings + posição -> Q,K,V -> scores QK^T/sqrt(dk) -> softmax -> saída ponderada -> residual+LayerNorm -> FFN.
Pesos aleatórios (sem treino): o objetivo é a mecânica, não o significado."""
import numpy as np
np.set_printoptions(precision=3, suppress=True)
rng = np.random.default_rng(7)
tokens = ["o", "gato", "dorme"]; V = {"o": 0, "gato": 1, "dorme": 2}; d, h, dk = 8, 2, 4
E = rng.normal(0, 1, (3, d))                                         # tabela de embeddings (vocab=3, d=8)
def pos(n, d):
    p = np.zeros((n, d))
    for i in range(n):
        for j in range(0, d, 2):
            p[i, j] = np.sin(i / 10000 ** (j / d)); p[i, j+1] = np.cos(i / 10000 ** (j / d))
    return p
X = E[[V[t] for t in tokens]] + pos(3, d)
print("1) Embedding + codificação posicional X (3x8):\n", X)
def softmax(z): z = z - z.max(-1, keepdims=True); e = np.exp(z); return e / e.sum(-1, keepdims=True)
heads = []
for i in range(h):
    Wq, Wk, Wv = (rng.normal(0, .5, (d, dk)) for _ in range(3))
    Q, K, Vv = X @ Wq, X @ Wk, X @ Wv
    S = Q @ K.T / np.sqrt(dk); A = softmax(S)
    print(f"\n2) Cabeça {i+1}: scores QKᵀ/√dk:\n{S}\n   atenção (softmax por linha; cada linha soma 1):\n{A}")
    heads.append(A @ Vv)
Wo = rng.normal(0, .5, (h*dk, d)); MHA = np.concatenate(heads, -1) @ Wo
def ln(z): return (z - z.mean(-1, keepdims=True)) / (z.std(-1, keepdims=True) + 1e-6)
Y = ln(X + MHA); print("\n3) Saída da atenção multi-cabeça + residual + LayerNorm:\n", Y)
W1, W2 = rng.normal(0, .5, (d, 4*d)), rng.normal(0, .5, (4*d, d))
Z = ln(Y + np.maximum(0, Y @ W1) @ W2); print("\n4) Saída do bloco (após FFN com ReLU + residual + LayerNorm):\n", Z)
# máscara causal (decoder): token i não enxerga o futuro
S = (X @ rng.normal(0, .5, (d, dk))) @ (X @ rng.normal(0, .5, (d, dk))).T / np.sqrt(dk)
S[np.triu_indices(3, 1)] = -1e9; print("\n5) Atenção com máscara causal (decoder):\n", softmax(S))

# =====================================================================================================
# PARTE B — Exemplo INTERPRETÁVEL: pesos desenhados à mão para mostrar o que uma cabeça treinada aprenderia
# =====================================================================================================
print("\n" + "=" * 78 + "\nPARTE B — codificação posicional (d=8) e atenção com pesos desenhados à mão\n" + "=" * 78)
def pos_enc(n, d):
    pe = np.zeros((n, d))
    for pos in range(n):
        for i in range(0, d, 2):
            pe[pos, i] = np.sin(pos / 10000 ** (i / d)); pe[pos, i + 1] = np.cos(pos / 10000 ** (i / d))
    return pe
np.set_printoptions(precision=3, suppress=True)
print("PE(pos, 2i)=sin(pos/10000^(2i/d)), PE(pos, 2i+1)=cos(...)  [linhas = posições 0,1,2 de 'o gato dorme']:\n", pos_enc(3, 8))

# Embeddings de 4 dimensões, legíveis: [é_artigo, é_substantivo, é_verbo, viés]
tokens = ["o", "gato", "dorme"]
X = np.array([[1, 0, 0, 1], [0, 1, 0, 1], [0, 0, 1, 1]], float)
# Cabeça "sujeito": a Query de um VERBO procura um SUBSTANTIVO; a Key de um substantivo anuncia "sou substantivo"
Wq = np.zeros((4, 2)); Wq[2, 0] = 4.0                 # verbo -> pergunta na dimensão 0 ("procuro substantivo")
Wk = np.zeros((4, 2)); Wk[1, 0] = 1.0; Wk[0, 1] = 1.0 # substantivo -> oferece na dimensão 0; artigo -> oferece na dimensão 1
Wv = np.eye(4)[:, :2] + 0                             # valor: copia [artigo, substantivo]
Wv = np.array([[1, 0], [0, 1], [0, 0], [0, 0]], float)
Q, K, V = X @ Wq, X @ Wk, X @ Wv
S = Q @ K.T / np.sqrt(2)
def softmax(z): e = np.exp(z - z.max(axis=-1, keepdims=True)); return e / e.sum(axis=-1, keepdims=True)
A = softmax(S)
print("\nScores QKᵀ/√d_k (linhas = quem pergunta; colunas = quem responde) — ordem:", tokens, "\n", S)
print("Pesos de atenção (softmax por linha):\n", A)
print("→ a linha de 'dorme' dá peso %.0f%% a 'gato': o verbo 'encontra' o seu sujeito. 'o' e 'gato' (sem verbo) ficam ~uniformes." % (100 * A[2, 1]))
print("Saída da cabeça A·V (cada linha é uma mistura dos Values):\n", A @ V)
M = np.tril(np.ones((3, 3)))
Ac = softmax(np.where(M == 1, S, -1e9))
print("Com máscara causal (decoder), 'dorme' não vê o futuro, mas vê o passado:\n", Ac)

# =====================================================================================================
# PARTE C — O exemplo numérico da "analogia da biblioteca" (vídeo indicado): 1 Query, 2 Keys, 2 Values
# =====================================================================================================
print("\n" + "=" * 78 + "\nPARTE C — exemplo do vídeo (Query=1; scores 1 e 0; Values [2,0] e [0,2])\n" + "=" * 78)
q = np.array([1.0]); K2 = np.array([[1.0], [0.0]]); V2 = np.array([[2.0, 0.0], [0.0, 2.0]])
sc = (K2 @ q); esc = sc / np.sqrt(2)                       # dimensão d_k = 2 no exemplo do vídeo -> divide por raiz de 2 ≈ 1,41
w = softmax(esc)
print("produtos escalares:", sc, "| divididos por √2:", esc.round(2), "| softmax:", w.round(2), "| soma:", w.sum().round(2))
print("saída = Σ peso·Value =", (w @ V2).round(2))
