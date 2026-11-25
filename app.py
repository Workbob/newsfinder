"""
NewsFinder - agregador de notícias por categoria.

Execute com:  python app.py
e acesse:     http://127.0.0.1:5000
"""

from flask import Flask, jsonify, render_template, request

from busca import buscar
from coletor import coletar
from fontes import FONTES, NOMES_CATEGORIAS

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html", categorias=NOMES_CATEGORIAS)


@app.route("/api/noticias")
def api_noticias():
    """
    Parâmetros (todos opcionais):
      categoria  - chave da categoria (padrão: todas)
      q          - palavras-chave para a busca
      fonte      - nome exato de uma fonte para filtrar
    """
    categoria = request.args.get("categoria", "todas")
    consulta = request.args.get("q", "").strip()
    fonte = request.args.get("fonte", "").strip()

    if categoria != "todas" and categoria not in FONTES:
        return jsonify({"erro": f"Categoria '{categoria}' não existe."}), 400

    noticias, erros = coletar(categoria)
    fontes_disponiveis = sorted({n["fonte"] for n in noticias})

    if fonte:
        noticias = [n for n in noticias if n["fonte"] == fonte]
    if consulta:
        noticias = buscar(noticias, consulta)

    return jsonify({
        "categoria": categoria,
        "consulta": consulta,
        "total": len(noticias),
        "fontes": fontes_disponiveis,
        "erros": erros,
        "noticias": noticias,
    })


if __name__ == "__main__":
    app.run(debug=True)
