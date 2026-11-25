# NewsFinder

Agregador de notícias: coleta notícias de várias fontes brasileiras via **RSS**
e mostra tudo em um só lugar, organizado por categoria, com busca por
palavra-chave ranqueada por **TF-IDF**.

Trabalho da disciplina **Recuperação de Informação na Web e Redes Sociais**.

## Como rodar

Requisito: Python 3.9 ou superior.

```bash
pip install -r requirements.txt
python app.py
```

Depois abra **http://127.0.0.1:5000** no navegador.

## Funcionalidades

| Funcionalidade | Onde está |
|---|---|
| Coletar notícias de várias fontes (RSS) | `coletor.py` |
| Extrair título, descrição, imagem, data, link e fonte | `coletor.py` → `extrair_noticia()` |
| Filtrar por categoria | botões no topo / `?categoria=` |
| Filtrar por fonte | caixa de seleção / `?fonte=` |
| Pesquisar por palavra-chave, ordenado por relevância (TF-IDF) | `busca.py` / `?q=` |
| Exibir fonte e data | cartões (`static/app.js`) |
| Abrir notícia original | link do cartão (nova aba) |
| Favoritos salvos no navegador (LocalStorage) | `static/app.js` |

## Estrutura

```
newsfinder/
├── app.py              # servidor Flask: página e API /api/noticias
├── coletor.py          # download dos feeds, extração dos campos, cache
├── busca.py            # pré-processamento + ranqueamento TF-IDF
├── fontes.py           # lista de feeds RSS por categoria (fácil de editar)
├── requirements.txt
├── templates/
│   └── index.html      # estrutura da página
└── static/
    ├── style.css       # visual dos cartões
    └── app.js          # filtros, busca, favoritos
```

## Como funciona (fluxo)

1. O usuário abre o site e escolhe uma categoria.
2. O front chama `GET /api/noticias?categoria=...&q=...&fonte=...`.
3. O `coletor.py` baixa os feeds da categoria **em paralelo** (threads),
   extrai os campos de cada item e remove notícias repetidas (mesmo link).
   O resultado fica em cache por 10 minutos para não sobrecarregar as fontes.
4. Se houver palavra-chave, o `busca.py` ranqueia as notícias por TF-IDF.
   Sem palavra-chave, as notícias aparecem da mais recente para a mais antiga.
5. O front monta os cartões. Se alguma fonte falhar, aparece um aviso e as
   demais continuam funcionando.

## A parte de Recuperação de Informação

**Coleta:** os feeds RSS são documentos XML padronizados publicados pelos
próprios portais. Usar RSS em vez de raspar o HTML das páginas é mais estável
(o layout do site pode mudar, o RSS não) e respeita o canal que o próprio
site oferece para consumo automatizado.

**Extração:** cada fonte guarda a imagem num lugar diferente. O coletor tenta,
em ordem: `media:content`, `media:thumbnail`, `enclosure`, a tag
`<imagem-destaque>` (Agência Brasil) e, por último, a primeira `<img>` dentro
da descrição. As descrições têm o HTML removido.

**Pré-processamento** (`busca.py`):
- tudo em minúsculas e sem acentos (`Educação` → `educacao`), assim a busca
  por "educacao" encontra "Educação";
- tokenização por palavras;
- remoção de *stopwords* do português (de, para, que, uma...).

**Ranqueamento TF-IDF:**

- **TF** (frequência do termo): quantas vezes o termo aparece na notícia,
  dividido pelo total de termos da notícia. Termos no **título contam em
  dobro**, porque o título resume o assunto.
- **IDF** (inverso da frequência nos documentos):
  `idf = log((N + 1) / (df + 1)) + 1`, onde `N` é o total de notícias e `df`
  é quantas contêm o termo. Termos raros na coleção valem mais que termos
  que aparecem em tudo.
- **Pontuação** da notícia = soma de `TF × IDF` dos termos da consulta.
  Notícias com pontuação zero não aparecem; as demais são ordenadas da maior
  para a menor. A pontuação aparece no rodapé de cada cartão.

## Usando a API diretamente

```
GET /api/noticias?categoria=tecnologia
GET /api/noticias?categoria=todas&q=inteligencia artificial
GET /api/noticias?categoria=economia&fonte=InfoMoney
```

Resposta (JSON): `total`, `fontes`, `erros` (fontes que não responderam) e
`noticias` (lista com `titulo`, `descricao`, `imagem`, `data`, `link`,
`fonte`, `categoria` e, na busca, `relevancia`).

## Adicionar ou trocar fontes

Edite `fontes.py`. Cada categoria é uma lista de `("Nome", "URL do RSS")`.
Para criar uma categoria nova, adicione a chave em `FONTES` e o nome
de exibição em `NOMES_CATEGORIAS`.

## Limitações

- Depende de os portais manterem os feeds no ar; se um endereço mudar, a fonte
  aparece no aviso "Algumas fontes não responderam" e basta corrigir a URL.
- A busca considera só título e descrição (o RSS não traz o texto completo).
- Favoritos ficam salvos apenas no navegador em que foram marcados.
