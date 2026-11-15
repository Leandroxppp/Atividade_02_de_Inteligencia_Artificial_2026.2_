"""Valida o CAMINHO LLM do agente (HTTP -> JSON -> verificador -> planejador -> validador) usando um servidor
local que imita a API de mensagens da Anthropic. NÃO é o modelo real: serve para provar que a integração
(requisição, leitura de 'content[0].text', JSON dentro de cercas ```json, verificação e fallback) funciona.
Para usar o LLM real: defina ANTHROPIC_API_KEY e rode `python agente_llm.py --demo`."""
import json, os, threading, http.server
MODO = {"v": "bom"}
BOM = {"horas_disponiveis": 4, "tarefas": [
    {"id": "A", "nome": "Preparar aula de IA", "min": 90, "prio": "Alta", "prazo": "hoje", "fixa": None},
    {"id": "B", "nome": "Corrigir trabalhos", "min": 120, "prio": "Média", "prazo": "amanha", "fixa": None},
    {"id": "C", "nome": "Reunião de pesquisa", "min": 60, "prio": "Alta", "prazo": "hoje", "fixa": [960, 1020]}]}
RUIM = json.loads(json.dumps(BOM)); RUIM["tarefas"][0]["prio"] = "Altíssima"; RUIM["tarefas"][1]["min"] = 100
class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_POST(self):
        self.rfile.read(int(self.headers["content-length"]))
        assert self.headers["x-api-key"] and self.headers["anthropic-version"]
        if MODO["v"] == "http500": self.send_response(500); self.end_headers(); return
        txt = {"bom": "```json\n" + json.dumps(BOM) + "\n```", "ruim": json.dumps(RUIM), "lixo": "Claro! Aqui está o plano..."}.get(MODO["v"], "")
        body = json.dumps({"content": [{"type": "text", "text": txt}]}).encode()
        self.send_response(200); self.send_header("content-type", "application/json"); self.end_headers(); self.wfile.write(body)
srv = http.server.HTTPServer(("127.0.0.1", 0), H); threading.Thread(target=srv.serve_forever, daemon=True).start()
os.environ["ANTHROPIC_BASE_URL"] = f"http://127.0.0.1:{srv.server_port}"; os.environ["ANTHROPIC_API_KEY"] = "chave-de-teste"
import agente_llm as A
PEDIDO = "Preciso preparar uma aula de IA, corrigir trabalhos e participar de uma reunião de pesquisa às 16h. Tenho 4 horas hoje."
for modo, desc in [("bom", "Resposta válida (JSON em cerca ```json)"), ("ruim", "Saída ruim do LLM (prioridade inválida, 100 min) -> verificador rejeita"),
                   ("lixo", "Resposta que não é JSON -> fallback para heurística"), ("http500", "Erro HTTP 500 -> fallback para heurística")]:
    MODO["v"] = modo; print("=" * 78); print("CENÁRIO:", desc)
    spec, origem = A.interpretar(PEDIDO); print("origem da interpretação:", origem); print("erros do verificador:", A.verificar(spec) or "nenhum")
print("=" * 78); MODO["v"] = "bom"; print("Fluxo completo com o 'LLM' (stub) respondendo:\n"); A.mostrar(PEDIDO)
