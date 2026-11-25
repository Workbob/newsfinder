"""
Fontes de notícias (feeds RSS) organizadas por categoria.

Para adicionar ou trocar uma fonte, basta editar este dicionário:
    "categoria": [("Nome da fonte", "URL do feed RSS"), ...]
"""

FONTES = {
    "tecnologia": [
        ("G1 Tecnologia", "https://g1.globo.com/rss/g1/tecnologia/"),
        ("Tecmundo", "https://rss.tecmundo.com.br/feed"),
        ("Canaltech", "https://canaltech.com.br/rss/"),
        ("Olhar Digital", "https://olhardigital.com.br/feed/"),
    ],
    "educacao": [
        ("G1 Educação", "https://g1.globo.com/rss/g1/educacao/"),
        ("Agência Brasil", "https://agenciabrasil.ebc.com.br/rss/educacao/feed.xml"),
        ("Folha Educação", "https://feeds.folha.uol.com.br/educacao/rss091.xml"),
    ],
    "economia": [
        ("G1 Economia", "https://g1.globo.com/rss/g1/economia/"),
        ("InfoMoney", "https://www.infomoney.com.br/feed/"),
        ("Agência Brasil", "https://agenciabrasil.ebc.com.br/rss/economia/feed.xml"),
        ("Folha Mercado", "https://feeds.folha.uol.com.br/mercado/rss091.xml"),
    ],
    "ciencia": [
        ("G1 Ciência e Saúde", "https://g1.globo.com/rss/g1/ciencia-e-saude/"),
        ("Folha Ciência", "https://feeds.folha.uol.com.br/ciencia/rss091.xml"),
    ],
    "esportes": [
        ("ge", "https://ge.globo.com/rss/ge/"),
        ("Folha Esporte", "https://feeds.folha.uol.com.br/esporte/rss091.xml"),
    ],
    "mundo": [
        ("G1 Mundo", "https://g1.globo.com/rss/g1/mundo/"),
        ("Folha Mundo", "https://feeds.folha.uol.com.br/mundo/rss091.xml"),
    ],
}

# Nomes exibidos na interface
NOMES_CATEGORIAS = {
    "todas": "Todas",
    "tecnologia": "Tecnologia",
    "educacao": "Educação",
    "economia": "Economia",
    "ciencia": "Ciência e Saúde",
    "esportes": "Esportes",
    "mundo": "Mundo",
}
