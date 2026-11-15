"""Roda um reasoner OWL 2 REAL (HermiT, via Owlready2) sobre credito.owl.
Requisitos: pip install owlready2 e Java. USO: python rodar_reasoner.py
Executado e validado: a saída está em hermit_real.txt."""
from owlready2 import World, sync_reasoner_hermit, OwlReadyInconsistentOntologyError, Thing
import os, io, contextlib
ARQ = "file://" + os.path.abspath("credito.owl")
def carregar():
    w = World(); return w, w.get_ontology(ARQ).load()

w, onto = carregar()
print("Classes:", len(list(onto.classes())), "| Propriedades:", len(list(onto.properties())), "| Indivíduos:", len(list(onto.individuals())))
with onto:
    sync_reasoner_hermit(w, infer_property_values=True)
print("\n== Consistência == CONSISTENTE (HermiT não encontrou contradição)")
print("Classes inconsistentes (≡ Nothing):", list(w.inconsistent_classes()))

def risco(i):
    t = {c.name for c in i.INDIRECT_is_a if hasattr(c, "name")}
    return sorted(t & {"ClienteRiscoAlto", "ClienteRiscoModerado", "ClienteRiscoBaixo"})

clientes = sorted((i for i in onto.individuals() if onto.Cliente in i.INDIRECT_is_a), key=lambda i: int(i.name[1:]) if i.name[1:].isdigit() else 99)
print("\n== Classificação automática de risco (inferida pelo HermiT) ==")
cont = {}
for i in clientes:
    r = risco(i); cont[tuple(r)] = cont.get(tuple(r), 0) + 1
    print(f"  {i.name:<4}: {', '.join(r) or '(nenhuma: mundo aberto)'}")
print("  Resumo:", {(k[0] if k else 'nenhuma'): v for k, v in cont.items()})
eleg = sorted(i.name for i in onto.ClienteElegivel.instances())
print(f"\n== Inferência em cadeia (definida -> risco -> ClienteElegivel) == {len(eleg)} elegíveis: {eleg}")

# Teste de inconsistência: cliente asserido RiscoBaixo com emprego instável (classes de risco disjuntas)
w2, o2 = carregar()
with o2:
    ex = o2.Cliente("EX"); ex.is_a.append(o2.ClienteRiscoBaixo)
    ex.temEmprego = o2.EmpregoInstavel
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            sync_reasoner_hermit(w2, infer_property_values=True)
        print("\n== Teste de inconsistência == HermiT NÃO detectou")
    except OwlReadyInconsistentOntologyError:
        print("\n== Teste de inconsistência (EX asserido RiscoBaixo + EmpregoInstavel => RiscoAlto) == HermiT: ONTOLOGIA INCONSISTENTE ✔")
