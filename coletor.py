"""
Coletor de notícias: baixa os feeds RSS, extrai os campos de interesse
(título, descrição, imagem, data, link e fonte) e mantém um cache em memória.
"""

import html
import re
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

import feedparser
import requests

from fontes import FONTES

TEMPO_CACHE = 10 * 60          # segundos que uma categoria fica em cache
TIMEOUT = 10                   # segundos de espera por feed
HEADERS = {"User-Agent": "Mozilla/5.0 (NewsFinder - trabalho academico)"}

_cache = {}                    # categoria -> (momento da coleta, notícias, erros)

RE_TAG = re.compile(r"<[^>]+>")
RE_IMG = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', re.IGNORECASE)


# ---------------------------------------------------------------- extração

def limpar_html(texto):
    """Remove tags HTML, entidades e espaços repetidos."""
    if not texto:
        return ""
    texto = RE_TAG.sub(" ", texto)
    texto = html.unescape(texto)
    return re.sub(r"\s+", " ", texto).strip()


def extrair_imagem(item):
    """Procura a imagem da notícia nos lugares mais comuns de um feed RSS."""
    for campo in ("media_content", "media_thumbnail"):
        for midia in item.get(campo, []) or []:
            if midia.get("url"):
                return midia["url"]

    for anexo in item.get("enclosures", []) or []:
        if anexo.get("type", "").startswith("image") and anexo.get("href"):
            return anexo["href"]

    # Tag própria usada pela Agência Brasil
    destaque = item.get("imagem-destaque", "")
    if destaque.startswith("http"):
        return destaque.strip()

    # Último recurso: primeira <img> dentro do conteúdo ou da descrição
    trechos = [c.get("value", "") for c in item.get("content", []) or []]
    trechos.append(item.get("summary", ""))
    for trecho in trechos:
        achou = RE_IMG.search(trecho or "")
        if achou:
            return achou.group(1)
    return None


def extrair_data(item):
    """Converte a data do item para ISO 8601 (UTC). Retorna None se não houver."""
    for campo in ("published_parsed", "updated_parsed"):
        data = item.get(campo)
        if data:
            return datetime(*data[:6], tzinfo=timezone.utc).isoformat()
    return None


def extrair_noticia(item, fonte, categoria):
    """Transforma um item do feed no dicionário usado pelo sistema."""
    descricao = limpar_html(item.get("summary", ""))
    if len(descricao) > 300:
        descricao = descricao[:297].rsplit(" ", 1)[0] + "..."

    return {
        "titulo": limpar_html(item.get("title", "")),
        "descricao": descricao,
        "imagem": extrair_imagem(item),
        "data": extrair_data(item),
        "link": item.get("link", ""),
        "fonte": fonte,
        "categoria": categoria,
    }


# ---------------------------------------------------------------- coleta

def coletar_feed(fonte, url, categoria):
    """Baixa e interpreta um único feed. Devolve (notícias, erro)."""
    try:
        resposta = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resposta.raise_for_status()
        feed = feedparser.parse(resposta.content)
    except Exception as erro:  # rede fora, timeout, 404...
        return [], f"{fonte}: {erro.__class__.__name__}"

    if not feed.entries:
        return [], f"{fonte}: feed vazio ou inválido"

    noticias = [extrair_noticia(item, fonte, categoria) for item in feed.entries]
    return [n for n in noticias if n["titulo"] and n["link"]], None


def coletar_categoria(categoria):
    """Coleta todas as fontes de uma categoria em paralelo, usando cache."""
    agora = time.time()
    if categoria in _cache and agora - _cache[categoria][0] < TEMPO_CACHE:
        return _cache[categoria][1], _cache[categoria][2]

    fontes = FONTES.get(categoria, [])
    with ThreadPoolExecutor(max_workers=8) as executor:
        resultados = list(executor.map(lambda f: coletar_feed(f[0], f[1], categoria), fontes))

    noticias, erros, vistos = [], [], set()
    for lista, erro in resultados:
        if erro:
            erros.append(erro)
        for noticia in lista:
            if noticia["link"] not in vistos:      # remove duplicadas
                vistos.add(noticia["link"])
                noticias.append(noticia)

    _cache[categoria] = (agora, noticias, erros)
    return noticias, erros


def coletar(categoria="todas"):
    """Ponto de entrada: coleta uma categoria ou todas, ordenando por data."""
    categorias = list(FONTES) if categoria == "todas" else [categoria]

    noticias, erros = [], []
    for cat in categorias:
        lista, erros_cat = coletar_categoria(cat)
        noticias.extend(lista)
        erros.extend(erros_cat)

    noticias.sort(key=lambda n: n["data"] or "", reverse=True)
    return noticias, erros
