"""Questão 3 — ELIZA (estilo Weizenbaum, 1966) em português: palavras-chave com ranking, decomposição (regex),
remontagem rotativa, reflexão de pronomes, memória e resposta padrão. Modo trace mostra qual regra disparou."""
import re, sys, random

REFLEXAO = {"eu": "você", "me": "você", "mim": "você", "meu": "seu", "minha": "sua", "meus": "seus", "minhas": "suas",
            "comigo": "com você", "estou": "está", "sou": "é", "você": "eu", "voce": "eu", "seu": "meu", "sua": "minha"}
def refletir(frag):
    return " ".join(REFLEXAO.get(w, w) for w in frag.split())

# palavra-chave -> (rank, [(padrão de decomposição, [remontagens])])   {1} = 1º grupo capturado (já refletido)
REGRAS = {
 "computador": (50, [(r".*", ["Os computadores te preocupam?", "Por que você mencionou computadores?", "O que você acha de máquinas?"])]),
 "mãe":   (5, [(r".*", ["Fale mais sobre sua família.", "Como era seu relacionamento com sua mãe?"])]),
 "pai":   (5, [(r".*", ["Fale mais sobre sua família.", "Seu pai influencia o que você sente hoje?"])]),
 "lembro": (5, [(r".*lembro (?:de |que )?(.*)", ["Você costuma pensar em {1}?", "O que mais vem à mente quando você pensa em {1}?"]),
                (r".*", ["O que você lembra?"])]),
 "sonho": (4, [(r".*sonh\w+ (?:com |que )?(.*)", ["O que esse sonho com {1} sugere para você?", "Você sonha com {1} com frequência?"])]),
 "me sinto": (4, [(r".*me sinto (.*)", ["Por que você se sente {1}?", "Há quanto tempo você se sente {1}?", "Você gosta de se sentir {1}?"])]),
 "estou": (3, [(r".*\bestou (.*)", ["Há quanto tempo você está {1}?", "Você veio aqui porque está {1}?", "O que significa para você estar {1}?"])]),
 "eu sou": (3, [(r".*\beu sou (.*)", ["Você acredita que é {1}?", "Você gostaria de não ser {1}?"])]),
 "quero": (3, [(r".*\bquero (.*)", ["O que mudaria se você conseguisse {1}?", "Por que você quer {1}?"])]),
 "não consigo": (3, [(r".*não consigo (.*)", ["Você acha mesmo que não consegue {1}?", "Talvez você consiga {1} se tentar de outro modo."])]),
 "porque": (2, [(r".*", ["Essa é a verdadeira razão?", "Que outras razões vêm à mente?"])]),
 "meu": (2, [(r".*\b(?:meu|minha|meus|minhas) (.*)", ["Por que você diz que seu {1}?", "Seu {1} é importante para você?"])]),
 "minha": (2, [(r".*\b(?:minha|minhas) (.*)", ["Por que você diz que sua {1}?", "Sua {1} é importante para você?"])]),
 "você": (1, [(r".*\bvocê (?:é |está )?(.*)", ["Estamos falando de você, não de mim.", "Por que você pergunta sobre mim?"])]),
 "sim": (1, [(r".*", ["Você parece bastante seguro.", "Entendo. Pode explicar melhor?"])]),
 "não": (1, [(r".*", ["Por que não?", "Você está sendo um pouco negativo."])]),
}
NENHUMA = ["Por favor, continue.", "Entendo.", "Fale mais sobre isso.", "Isso é interessante. Prossiga."]

class Eliza:
    def __init__(self, trace=False, seed=0):
        self.trace, self.idx, self.mem = trace, {}, []
        random.seed(seed)
    def _escolhe(self, chave, lista):
        i = self.idx.get(chave, 0); self.idx[chave] = (i + 1) % len(lista); return lista[i], i + 1
    def responder(self, texto):
        t = re.sub(r"[^\w\sçãõáéíóúâêôà,.?!-]", "", texto.lower()).strip()
        sent = re.split(r"[,.?!;]| mas ", t)                      # corta na 1ª pontuação que já tenha palavra-chave (como o original)
        for s in sent:
            s = s.strip()
            if not s: continue
            achadas = [(r, k) for k, (r, _) in REGRAS.items() if re.search(rf"(?<!\w){re.escape(k)}(?!\w)", s)]
            if not achadas: continue
            rank, k = max(achadas)
            for pad, resp in REGRAS[k][1]:
                m = re.match(pad, s)
                if m:
                    frag = refletir(m.group(1)) if m.groups() else ""
                    modelo, n = self._escolhe((k, pad), resp)
                    out = modelo.replace("{1}", frag).replace("  ", " ")
                    if k in ("meu", "minha"): self.mem.append(f"Antes você disse que {s}. Isso tem a ver com o que você sente agora?")   # MEMORY
                    if self.trace: print(f"    [trace] sentença='{s}' | chave='{k}' (rank {rank}) | decomposição=/{pad}/ | grupo1='{m.group(1) if m.groups() else ''}' -> refletido='{frag}' | remontagem #{n}")
                    return out
        if self.mem:
            out = self.mem.pop(0)
            if self.trace: print("    [trace] sem palavra-chave -> usa MEMÓRIA")
            return out
        out, n = self._escolhe("NONE", NENHUMA)
        if self.trace: print(f"    [trace] sem palavra-chave -> resposta padrão #{n}")
        return out

DIALOGO = ["Olá, estou muito cansado ultimamente.", "Eu me sinto sozinho no trabalho.", "Meu chefe não me escuta.",
           "Eu odeio meu chefe", "Eu lembro da minha infância no interior.", "Sonhei com minha mãe ontem.",
           "O tempo está bonito hoje.", "Você é um robô?", "Não estou triste, estou irritado.", "Não consigo dormir.",
           "Eu estou lendo sobre computador e IA.", "Qual é o sentido da vida?"]

if __name__ == "__main__":
    if "--chat" in sys.argv:
        e = Eliza(); print("ELIZA: Como você está se sentindo hoje? (Ctrl-C para sair)")
        while True: print("ELIZA:", e.responder(input("Você: ")))
    e = Eliza(trace=True)
    print("ELIZA: Como você está? Conte-me seu problema.")
    for fala in DIALOGO:
        print(f"\nUSUÁRIO: {fala}"); r = e.responder(fala); print(f"ELIZA:   {r}")
