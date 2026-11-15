# Questão 15 — Aplicação com ontologia OWL 2: risco de crédito (a árvore de decisão da Lista 1 como axiomas)

Arquivos: `credito.owl` (ontologia), `ontologia_credito.py` (gerador + conferência), `rodar_reasoner.py` (**HermiT real** via Owlready2, para rodar localmente), `owlgen.py`, `risco_credito_ampliado.csv`, `resultados.txt`.

> **Validação com reasoner real (HermiT).** `credito.owl` foi carregado e classificado pelo **HermiT via Owlready2** (`python rodar_reasoner.py`; saída em `hermit_real.txt`): ontologia **consistente**, os **30 clientes classificados** (11 `ClienteRiscoAlto`, 9 `ClienteRiscoModerado`, 10 `ClienteRiscoBaixo`), **19 inferidos `ClienteElegivel`** por subclasse (inferência em cadeia: classe definida → risco → elegibilidade), e **teste de inconsistência**: um indivíduo `EX` asserido `ClienteRiscoBaixo` com `temEmprego EmpregoInstavel` (que implica `ClienteRiscoAlto`) torna a ontologia inconsistente segundo o HermiT. O resultado coincide com o do mini-reasoner em Python (`ontologia_credito.py`). *Reprodução no Protégé:* Reasoner → HermiT → Start reasoner; *Individuals by type* em E1 e E5; *Inferred class hierarchy*; criar `EX` e usar *Explain*.

## 1. Ideia
Na Lista 1 (Questão 1) foram construídos ID3, C4.5 e CART sobre a base de 30 clientes e adotada a **base de regras do C4.5** (5 regras, raiz = Emprego, por ser compacta e usar condições categóricas legíveis). Aqui o **mesmo conhecimento vira OWL**: cada regra do C4.5 se torna uma **classe definida** (condições necessárias e suficientes) subclasse de uma classe de risco, e o *reasoner* classifica automaticamente os 30 clientes. A base `risco_credito_ampliado.csv` é a mesma da Lista 1 (conteúdo idêntico).

## 2. Modelagem
* **Classes:** `Cliente` ⊒ {`ClienteRiscoAlto`, `ClienteRiscoModerado`, `ClienteRiscoBaixo`} (**disjuntas**); `Patrimonio`, `Emprego`, `Renda`, `HistoriaCredito`, `Garantia`, `Divida`.
* **Propriedades de objeto (funcionais):** `temPatrimonio`, `temEmprego`, `temRenda`, `temHistorico`, `temGarantia`, `temDivida` (e as inversas `ehPatrimonioDe`, …); de dados: `identificador`.
* **Classes definidas (5) = regras do C4.5 da Lista 1:**

| Regra C4.5 | Classe definida (axioma) | Sub de |
|---|---|---|
| R1 | `ClienteEmpregoInstavel ≡ Cliente ⊓ temEmprego value EmpregoInstavel` | RiscoAlto |
| R2 | `ClienteEstavelPatrimonioAlto ≡ Cliente ⊓ Estável ⊓ Patrimônio Alto` | RiscoBaixo |
| R3 | `ClienteEstavelMedioRendaMedia ≡ Cliente ⊓ Estável ⊓ Patrimônio Médio ⊓ Renda 15–35k` | RiscoModerado |
| R4 | `ClienteEstavelMedioRendaAltaHistRuim ≡ … ⊓ Renda >35k ⊓ História Ruim` | RiscoModerado |
| R5 | `ClienteEstavelMedioRendaAltaBoaHist ≡ … ⊓ Renda >35k ⊓ História Boa` | RiscoBaixo |

* **Indivíduos:** os 30 clientes E1–E30 (valores do CSV) + 15 indivíduos de valores (PatrimonioBaixo, etc.).

### Acréscimos de modelagem
* **`ClienteElegivel`** (superclasse de `ClienteRiscoBaixo` e `ClienteRiscoModerado`): gera **inferência em cadeia** (condições do cliente → classe definida → classe de risco → elegibilidade). Resultado: 19 de 30 clientes elegíveis; os 11 de risco alto não são.
* **Propriedades inversas** (`temPatrimonio` ↔ `ehPatrimonioDe`, etc.): revelam **relações implícitas** (ex.: `EmpregoInstavel ehEmpregoDe E1, E2, E4, E7, E11, E14, E16, E20, E21, E26, E28`).
* **`AllDifferent`** entre todos os indivíduos: OWL não assume nomes únicos; sem isso, propriedades funcionais poderiam "fundir" indivíduos.

## 3. Raciocínio demonstrado
1. **Classificação automática:** o reasoner/mini-reasoner infere a classe de risco de **cada um dos 30 clientes sem que ela seja declarada: 30/30 coincidem** com o rótulo da Lista 1.
2. **Inferência por subclasse e em cadeia:** `ClienteEmpregoInstavel ⊑ ClienteRiscoAlto`; `ClienteRiscoBaixo ⊑ ClienteElegivel`: 19 elegíveis e 11 não elegíveis.
3. **Consistência:** declarar `EX : ClienteRiscoBaixo` com `temEmprego EmpregoInstavel` leva à inferência de `ClienteRiscoAlto` e viola a disjunção → **ontologia inconsistente** (HermiT aponta).
4. **Indivíduo novo:** (Médio, Estável, 15–35k, Ruim) → inferido **Moderado**.
5. **Mundo aberto (dois casos):** (Médio, Estável, >35k, **Desconhecida**) e (Patrimônio **Baixo**, Estável, 15–35k, Boa) **não** são classificados em nenhuma classe: nenhuma regra do C4.5 os cobre (a base de treino não tinha esses casos). Em OWL isso não é erro, é ausência de conhecimento; a árvore de decisão, ao contrário, sempre devolveria uma classe (possivelmente errada). Para cobrir o segundo caso seria preciso acrescentar uma regra, por exemplo vinda do ID3 (`Patrimônio Baixo ⇒ Alto`), o que mostra a diferença entre as árvores da Lista 1.

## 4. Discussão
* **Representação:** o conhecimento sai do código e vira modelo declarativo, explícito, reutilizável e verificável.
* **Raciocínio:** dedutivo (certo se as premissas valem), ao contrário da árvore (induzida de dados, estatística).
* **Limites:** (i) a árvore C4.5 é aprendida, a ontologia foi **transcrita** (não aprende); (ii) OWL não lida bem com limiares numéricos finos (usamos faixas categóricas) nem com incerteza (ver Questões 6 e 8); (iii) mundo aberto exige cuidado (casos não cobertos); (iv) as folhas viram muitas classes definidas, e a manutenção cresce com as regras.

<!-- evidencia-protege -->
## Evidência no Protégé (HermiT 1.4.3.456)
Além da execução por código (`rodar_reasoner.py`), a ontologia `credito.owl` foi aberta no **Protégé** com o reasoner **HermiT 1.4.3.456**. Os prints estão em `prints/` (legenda completa em `prints/LEIAME.md`):

* **Estrutura** — `01_metricas_ontologia.png`: 16 classes, 12 propriedades de objeto, 1 de dados, 45 indivíduos, 5 classes equivalentes (definidas) e 2 axiomas de disjunção.
* **Reasoner em execução** — `02_menu_reasoner_HermiT_em_execucao.png`.
* **Classificação automática de clientes** — `03_E1_tipo_inferido_ClienteEmpregoInstavel.png` e `04_E5_tipo_inferido_ClienteEstavelPatrimonioAlto.png` (o tipo inferido aparece em amarelo).
* **Inferência em cadeia** — `05_dlquery_ClienteElegivel_19_instancias.png` e `06_dlquery_ClienteElegivel_lista_final.png`: condições do cliente → classe definida → classe de risco → `ClienteElegivel`, com 19 instâncias (E3, E5, E6, E8, E9, E10, E12, E13, E15, E17, E18, E19, E22, E23, E24, E25, E27, E29, E30). Os 11 clientes de risco alto ficam fora.

*Observação:* em *Types* o Protégé mostra o tipo **direto** inferido (o mais específico); as classes de risco e de elegibilidade são superclasses dele. Os resultados coincidem com `hermit_real.txt`.
