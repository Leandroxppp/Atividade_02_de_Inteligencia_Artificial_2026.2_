"""Roda um reasoner OWL 2 REAL (HermiT, via Owlready2) sobre livros.owl.
Requisitos: pip install owlready2 e Java. USO: python rodar_reasoner.py
Executado e validado: a saída está em hermit_real.txt.
Mostra: consistência, tipos inferidos (diretos + indiretos), propriedades inferidas
(inversas/transitivas) e teste de inconsistência (indivíduo em classes disjuntas)."""
from owlready2 import (World, sync_reasoner_hermit, OwlReadyInconsistentOntologyError, Thing)
import os, sys, io, contextlib
ARQ = "file://" + os.path.abspath("livros.owl")

def carregar():
    w = World(); return w, w.get_ontology(ARQ).load()

w, onto = carregar()
print("Classes:", len(list(onto.classes())), "| Propriedades:", len(list(onto.properties())), "| Indivíduos:", len(list(onto.individuals())))
with onto:
    sync_reasoner_hermit(w, infer_property_values=True)
print("\n== Consistência == CONSISTENTE (HermiT não encontrou contradição)")
print("Classes inconsistentes (≡ Nothing):", list(w.inconsistent_classes()))
print("\n== Classificação inferida pelo HermiT (tipos diretos + indiretos, sem Thing) ==")
for ind in sorted(onto.individuals(), key=lambda i: i.name):
    tipos = sorted({c.name for c in ind.INDIRECT_is_a if hasattr(c, "name") and c is not Thing})
    if len(tipos) > 1 or ind.name.startswith("L") or ind.name in ("Ana", "Bruno", "Carla"):
        print(f"  {ind.name:<14}: {', '.join(tipos)}")
print("\n== Classes definidas -> indivíduos (via HermiT) ==")
for cn in ("LivroCurto", "LeituraRapidaParaIniciante", "LivroBemAvaliado", "LivroDeIA", "LeitorIniciante"):
    c = getattr(onto, cn, None)
    if c: print(f"  {cn}: {sorted(i.name for i in c.instances())}")
print("\n== Relações implícitas (inversas/transitivas) ==")
for p in ("escreveu", "ehPrerequisitoDe"):
    pr = getattr(onto, p, None)
    if pr:
        n = 0
        for ind in onto.individuals():
            for v in getattr(ind, p, []):
                if n < 12: print(f"  {ind.name} {p} {getattr(v,'name',v)}")
                n += 1
        print(f"  ({p}: {n} asserções no total após inferência)")

# Teste de inconsistência: LX é LivroTecnico E LivroFiccao (classes disjuntas)
w2, o2 = carregar()
with o2:
    lx = o2.LivroTecnico("LX"); lx.is_a.append(o2.LivroFiccao)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            sync_reasoner_hermit(w2)
        print("\n== Teste de inconsistência == HermiT NÃO detectou (inesperado)")
    except OwlReadyInconsistentOntologyError:
        print("\n== Teste de inconsistência (LX ∈ LivroTecnico ⊓ LivroFiccao) == HermiT: ONTOLOGIA INCONSISTENTE ✔ (disjunção detectada)")
