"""
Ponte entre o HTML e a sua análise em Python.

Este arquivo NÃO modifica o seu código: ele executa o analise.py como está,
responde o input() com a opção escolhida na página e captura o que o código
produz (prints, gráficos do matplotlib e a variável final `tabela`).

Como usar:
    pip install flask pandas matplotlib seaborn
    python app.py
Depois abra http://127.0.0.1:5000 no navegador.
"""

import base64
import builtins
import contextlib
import io
import os
import shutil
import tempfile
import threading
import traceback
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # gera imagens sem abrir janelas
from matplotlib import pyplot as plt
from flask import Flask, jsonify, request, send_from_directory

BASE = Path(__file__).parent
ARQUIVO_ANALISE = BASE / "codigo.py"  # coloque aqui o seu código

app = Flask(__name__)
trava = (
    threading.Lock()
)  # o matplotlib não lida bem com várias execuções ao mesmo tempo


def executar_analise(opcao):
    codigo = compile(
        ARQUIVO_ANALISE.read_text(encoding="utf-8"), str(ARQUIVO_ANALISE), "exec"
    )
    escopo = {"__name__": "__analise__"}
    saida = io.StringIO()

    def input_da_pagina(pergunta=""):
        # Mostra a pergunta e a resposta, como aconteceria no notebook
        print(f"{pergunta}{opcao}")
        return str(opcao)

    input_original = builtins.input
    pasta_original = os.getcwd()
    builtins.input = input_da_pagina
    # O código roda numa pasta temporária e vazia: o 'Banco de dados.db' que ele
    # cria (CREATE TABLE + INSERT) nasce do zero a cada execução e é descartado
    # depois. Assim o banco real nunca recebe linhas duplicadas.
    pasta_temp = tempfile.mkdtemp()
    os.chdir(pasta_temp)
    try:
        with contextlib.redirect_stdout(saida):
            exec(codigo, escopo)

        graficos = []
        for numero in plt.get_fignums():
            buffer = io.BytesIO()
            plt.figure(numero).savefig(
                buffer, format="png", dpi=110, bbox_inches="tight"
            )
            graficos.append(base64.b64encode(buffer.getvalue()).decode("ascii"))

        tabela = escopo.get("tabela")
        tabela_html = tabela.to_html(border=0) if hasattr(tabela, "to_html") else None

        return {"saida": saida.getvalue(), "graficos": graficos, "tabela": tabela_html}
    finally:
        builtins.input = input_original
        os.chdir(pasta_original)
        plt.close("all")
        banco = escopo.get("banco")
        if banco is not None:
            banco.close()  # precisa fechar antes de apagar (no Windows o arquivo fica travado)
        shutil.rmtree(pasta_temp, ignore_errors=True)


@app.route("/")
def index():
    return send_from_directory(BASE, "visual.html")


@app.route("/api/executar")
def executar():
    try:
        opcao = int(request.args.get("opcao", 1))
    except ValueError:
        return jsonify({"erro": "A opção precisa ser um número."}), 400

    with trava:
        try:
            return jsonify(executar_analise(opcao))
        except Exception:
            return jsonify({"erro": traceback.format_exc()}), 500


if __name__ == "__main__":
    app.run(debug=True)
