# Questão 7 — Sistema de apoio ao diagnóstico baseado em casos (CBR)

Arquivos: `cbr_medico.py` (código), `avaliacao.py`/`avaliacao.txt` (validação), `casos.json` (base), `resultados.txt` (saída da demonstração). Uso: `python cbr_medico.py` (menu) ou `python cbr_medico.py --demo`.
> Casos **fictícios**, só para fins educacionais; não é ferramenta clínica.

## 1. Base de casos
18 casos, **6 doenças** (Dengue, COVID-19, Gripe, Pneumonia, Gastroenterite, Rinite alérgica), 3 casos por doença.

## 2. Representação dos casos
```json
{"id":"C01","sintomas":["febre_alta","dor_atras_dos_olhos","dor_muscular","manchas_na_pele","dor_de_cabeca"],
 "idade":28,"dias":4,"diagnostico":"Dengue","tratamento":"Hidratação oral..."}
```
Problema = (sintomas, idade, dias de sintomas); solução = (diagnóstico, tratamento). 22 sintomas possíveis.

## 3. Similaridade
`sim(q,c) = 0,85·Jaccard_ponderado(sintomas) + 0,10·sim_idade + 0,05·sim_duração`
* **Jaccard ponderado:** `Σ peso(s ∈ A∩B) / Σ peso(s ∈ A∪B)`, com **peso IDF** `ln((N+1)/(1+n_s))+1`: sintomas raros (perda de olfato, manchas) valem mais que febre.
* `sim_idade = 1 − min(|Δidade|,60)/60`; `sim_duração = 1 − min(|Δdias|,10)/10`.

## 4. Ciclo CBR
* **Retrieve:** `recuperar()` ordena os casos por similaridade e devolve os k=3 mais próximos.
* **Reuse:** `reutilizar()` faz voto ponderado por `sim²` e copia o tratamento do melhor caso da doença vencedora; mostra o ranking e a “confiança relativa” (participação no voto, **não é probabilidade calibrada**).
* **Revise:** `revisar()` — o médico confirma ou corrige diagnóstico/tratamento.
* **Retain:** `reter()` — grava o caso (com a marca `corrigido_na_revisao`) em `casos.json`.

## 5. Consultas de exemplo (de `resultados.txt`)

| Consulta | Melhor caso (sim) | Sugestão |
|---|---|---|
| febre alta, dor atrás dos olhos, dor muscular, manchas (30 anos, 3 d) | C01 (0,837) | **Dengue** (100%) |
| febre, tosse seca, perda de olfato/paladar, fadiga (40, 4 d) | C04 (0,832) | **COVID-19** (100%) |
| coriza, espirros, coceira nos olhos (22, 7 d) | C18 (0,933) | **Rinite alérgica** (100%) |
| febre, tosse, dor de cabeça (35, 2 d) — **ambígua** | C04 (0,374) | COVID-19 (68%) vs Gripe (32%) |

**Ciclo Revise/Retain:** no caso ambíguo o médico corrige para **Gripe**; o caso é retido como C19. Ao repetir a consulta, o sistema recupera C19 (sim = 1,0) e sugere **Gripe** (79%) com o tratamento aprendido — o aprendizado incremental do CBR.

## 6. Análise
* Casos com sintomas **típicos e específicos** (dengue, COVID, rinite) são recuperados com folga (sim ≥ 0,83).
* Com sintomas **inespecíficos** (febre+tosse+cefaleia) as similaridades ficam próximas (≈0,36–0,37) e a sugestão é instável, o que é desejável que o sistema reconheça como incerteza (confiança de 68%), e é aí que **Revise** importa.
* **Leave-one-out nos 18 casos originais** (`avaliacao.py`, `avaliacao.txt`; varredura de pesos e de k):

| Pesos (sintomas, idade, duração) | k=1 | k=3 | k=5 |
|---|---:|---:|---:|
| 0,85 / 0,10 / 0,05 (adotado) | 66,7% | 66,7% | 72,2% |
| 1,0 / 0 / 0 (só sintomas) | 72,2% | 72,2% | 77,8% |
| 0,9 / 0,1 / 0 | 72,2% | 72,2% | 72,2% |
| 0,7 / 0,2 / 0,1 | 61,1% | 66,7% | 72,2% |
| 0,6 / 0,3 / 0,1 | 61,1% | 66,7% | 72,2% |

**Leitura:** idade e duração **não ajudam** nesta base fictícia (os casos foram gerados a partir dos sintomas); o melhor resultado usa só sintomas (77,8% com k=5). Com apenas 3 casos por doença, tirar um deixa 2 de referência, e há sobreposição real de sintomas (gripe × COVID × dengue), então 70–78% é o teto razoável. O sistema funciona bem para casos típicos (sim ≥ 0,83) e sinaliza incerteza nos ambíguos, que é o comportamento desejado. Os pesos 0,85/0,10/0,05 foram mantidos como padrão porque, em casos reais, idade e duração dos sintomas costumam ser relevantes (por exemplo, para pneumonia e gastroenterite); nesta base fictícia, porém, a validação favorece usar só sintomas (77,8% com k=5). `avaliacao.py` permite trocar os pesos e repetir a medição.
* Limitações: base pequena e fictícia; sintomas binários (sem gravidade); sem sinais vitais/exames; peso fixo 0,85/0,10/0,05 não calibrado; retenção sem critério (pode duplicar casos). Melhorias: sintomas graduados, exames, política de retenção (só casos novos/úteis), ajuste de pesos por validação.
