// Estado da tela
let categoriaAtual = "todas";
let consultaAtual = "";
let fonteAtual = "";

const CHAVE_FAVORITOS = "newsfinder_favoritos";

const lista = document.getElementById("lista");
const statusEl = document.getElementById("status");
const avisosEl = document.getElementById("avisos");
const filtroFonte = document.getElementById("filtro-fonte");
const campoBusca = document.getElementById("campo-busca");
const modelo = document.getElementById("modelo-cartao");

// ---------------------------------------------------------------- favoritos (LocalStorage)

function lerFavoritos() {
  try {
    return JSON.parse(localStorage.getItem(CHAVE_FAVORITOS)) || [];
  } catch {
    return [];
  }
}

function salvarFavoritos(favoritos) {
  try {
    localStorage.setItem(CHAVE_FAVORITOS, JSON.stringify(favoritos));
  } catch {
    /* navegador sem LocalStorage: favoritos não persistem */
  }
}

function ehFavorito(link) {
  return lerFavoritos().some((n) => n.link === link);
}

function alternarFavorito(noticia, botao) {
  let favoritos = lerFavoritos();
  if (ehFavorito(noticia.link)) {
    favoritos = favoritos.filter((n) => n.link !== noticia.link);
  } else {
    favoritos.unshift(noticia);
  }
  salvarFavoritos(favoritos);
  atualizarBotaoFavorito(botao, noticia.link);
  if (categoriaAtual === "favoritos") mostrarFavoritos();
}

function atualizarBotaoFavorito(botao, link) {
  const ativo = ehFavorito(link);
  botao.textContent = ativo ? "★" : "☆";
  botao.classList.toggle("ativo", ativo);
  botao.title = ativo ? "Remover dos favoritos" : "Salvar nos favoritos";
}

// ---------------------------------------------------------------- renderização

function formatarData(iso) {
  if (!iso) return "";
  return new Date(iso).toLocaleString("pt-BR", {
    day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit",
  });
}

function criarCartao(noticia) {
  const cartao = modelo.content.cloneNode(true);

  const linkImagem = cartao.querySelector(".imagem");
  const img = cartao.querySelector(".imagem img");
  linkImagem.href = noticia.link;
  if (noticia.imagem) {
    img.src = noticia.imagem;
    img.onerror = () => semImagem(linkImagem, noticia.fonte);
  } else {
    semImagem(linkImagem, noticia.fonte);
  }

  cartao.querySelector(".fonte").textContent = noticia.fonte;
  const data = cartao.querySelector(".data");
  data.textContent = formatarData(noticia.data);
  if (noticia.data) data.dateTime = noticia.data;

  const titulo = cartao.querySelector(".titulo a");
  titulo.textContent = noticia.titulo;
  titulo.href = noticia.link;

  cartao.querySelector(".descricao").textContent = noticia.descricao;
  cartao.querySelector(".abrir").href = noticia.link;

  if (noticia.relevancia !== undefined) {
    const rel = cartao.querySelector(".relevancia");
    rel.textContent = `Relevância (TF-IDF): ${noticia.relevancia}`;
    rel.hidden = false;
  }

  const botao = cartao.querySelector(".favoritar");
  atualizarBotaoFavorito(botao, noticia.link);
  botao.addEventListener("click", () => alternarFavorito(noticia, botao));

  return cartao;
}

function semImagem(elemento, fonte) {
  elemento.innerHTML = "";
  elemento.textContent = fonte;
  elemento.classList.add("sem-imagem");
}

function renderizar(noticias, mensagemVazia) {
  lista.innerHTML = "";
  if (noticias.length === 0) {
    lista.innerHTML = `<p class="vazio">${mensagemVazia}</p>`;
    return;
  }
  const fragmento = document.createDocumentFragment();
  noticias.forEach((n) => fragmento.appendChild(criarCartao(n)));
  lista.appendChild(fragmento);
}

function preencherFontes(fontes) {
  filtroFonte.innerHTML = '<option value="">Todas as fontes</option>';
  fontes.forEach((f) => {
    const opcao = document.createElement("option");
    opcao.value = f;
    opcao.textContent = f;
    if (f === fonteAtual) opcao.selected = true;
    filtroFonte.appendChild(opcao);
  });
}

// ---------------------------------------------------------------- carregamento

async function carregarNoticias() {
  statusEl.textContent = "Buscando notícias nas fontes...";
  avisosEl.hidden = true;
  filtroFonte.hidden = false;

  const params = new URLSearchParams({ categoria: categoriaAtual });
  if (consultaAtual) params.set("q", consultaAtual);
  if (fonteAtual) params.set("fonte", fonteAtual);

  try {
    const resposta = await fetch(`/api/noticias?${params}`);
    const dados = await resposta.json();
    if (!resposta.ok) throw new Error(dados.erro || "Erro ao buscar notícias");

    preencherFontes(dados.fontes);

    const sufixo = consultaAtual ? ` para "${consultaAtual}" (ordenadas por relevância)` : "";
    statusEl.textContent = `${dados.total} notícia(s) encontrada(s)${sufixo}`;

    if (dados.erros.length) {
      avisosEl.textContent = `Algumas fontes não responderam: ${dados.erros.join("; ")}`;
      avisosEl.hidden = false;
    }

    renderizar(dados.noticias, "Nenhuma notícia encontrada. Tente outra palavra-chave ou categoria.");
  } catch (erro) {
    statusEl.textContent = "Não foi possível carregar as notícias.";
    renderizar([], erro.message);
  }
}

function mostrarFavoritos() {
  filtroFonte.hidden = true;
  avisosEl.hidden = true;
  let favoritos = lerFavoritos();
  if (consultaAtual) {
    const termo = consultaAtual.toLowerCase();
    favoritos = favoritos.filter((n) =>
      (n.titulo + " " + n.descricao).toLowerCase().includes(termo));
  }
  statusEl.textContent = `${favoritos.length} notícia(s) salva(s)`;
  renderizar(favoritos, "Você ainda não salvou nenhuma notícia. Clique na ☆ de um cartão.");
}

function atualizar() {
  if (categoriaAtual === "favoritos") mostrarFavoritos();
  else carregarNoticias();
}

// ---------------------------------------------------------------- eventos

document.getElementById("categorias").addEventListener("click", (e) => {
  const botao = e.target.closest(".categoria");
  if (!botao) return;
  document.querySelectorAll(".categoria").forEach((b) => b.classList.remove("ativa"));
  botao.classList.add("ativa");
  categoriaAtual = botao.dataset.categoria;
  fonteAtual = "";
  atualizar();
});

document.getElementById("form-busca").addEventListener("submit", (e) => {
  e.preventDefault();
  consultaAtual = campoBusca.value.trim();
  atualizar();
});

campoBusca.addEventListener("search", () => {   // botão "x" do campo limpa a busca
  if (campoBusca.value === "" && consultaAtual) {
    consultaAtual = "";
    atualizar();
  }
});

filtroFonte.addEventListener("change", () => {
  fonteAtual = filtroFonte.value;
  carregarNoticias();
});

atualizar();
