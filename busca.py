"""
Busca por palavra-chave com ranqueamento TF-IDF.

É a parte de Recuperação de Informação do projeto:
  1. Pré-processamento: minúsculas, remoção de acentos, tokenização,
     remoção de stopwords.
  2. Modelo vetorial simplificado: cada notícia recebe uma pontuação
     igual à soma de TF x IDF dos termos da consulta.
  3. O título pesa mais que a descrição (termo no título conta em dobro).
"""

import math
import re
import unicodedata
from collections import Counter

STOPWORDS = set("""
a ao aos as ate com como da das de dela dele deles do dos e ela ele eles em
entre era essa esse esta este eu foi for ha isso isto ja la mais mas me mesmo
na nas nao no nos o os ou para pela pelas pelo pelos por qual quando que quem
se sem ser seu seus sua suas so sobre tambem te tem um uma umas uns vai voce
""".split())

PESO_TITULO = 2


def normalizar(texto):
    """Minúsculas e sem acentos: 'Educação' -> 'educacao'."""
    texto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def tokenizar(texto):
    """Quebra o texto em termos, descartando stopwords e termos de 1 letra."""
    termos = re.findall(r"[a-z0-9]+", normalizar(texto))
    return [t for t in termos if len(t) > 1 and t not in STOPWORDS]


def termos_da_noticia(noticia):
    """Frequência dos termos da notícia, com o título valendo mais."""
    contagem = Counter(tokenizar(noticia["descricao"]))
    for termo in tokenizar(noticia["titulo"]):
        contagem[termo] += PESO_TITULO
    return contagem


def buscar(noticias, consulta):
    """
    Devolve as notícias que contêm ao menos um termo da consulta,
    ordenadas por relevância (TF-IDF). Cada uma ganha o campo 'relevancia'.
    """
    termos_consulta = tokenizar(consulta)
    if not termos_consulta:
        return noticias

    documentos = [termos_da_noticia(n) for n in noticias]
    total = len(documentos)

    # IDF: termos raros na coleção valem mais (com suavização)
    idf = {}
    for termo in set(termos_consulta):
        df = sum(1 for doc in documentos if termo in doc)
        idf[termo] = math.log((total + 1) / (df + 1)) + 1

    resultados = []
    for noticia, doc in zip(noticias, documentos):
        tamanho = sum(doc.values()) or 1
        pontuacao = sum((doc[t] / tamanho) * idf[t] for t in termos_consulta if t in doc)
        if pontuacao > 0:
            resultados.append({**noticia, "relevancia": round(pontuacao, 4)})

    resultados.sort(key=lambda n: n["relevancia"], reverse=True)
    return resultados
