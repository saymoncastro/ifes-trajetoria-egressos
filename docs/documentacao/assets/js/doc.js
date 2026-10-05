/* Documentação do Trajetória Ifes — navegação, destaque da seção atual, filtros de tabela e
   tema. JavaScript simples, sem dependências; a página funciona por completo sem ele (a
   navegação lateral fica visível no desktop e os filtros simplesmente não aparecem). */
(function () {
  "use strict";

  var raiz = document.documentElement;
  var lateral = document.getElementById("lateral");
  var veu = document.getElementById("veu");
  var botaoMenu = document.getElementById("botao-menu");
  var botaoTema = document.getElementById("botao-tema");
  var voltar = document.getElementById("voltar-topo");

  raiz.classList.add("js");

  /* ---------- Rótulos das células para a leitura em cartões no celular ---------- */
  Array.prototype.forEach.call(document.querySelectorAll(".tabela table"), function (t) {
    if (!t.tHead || !t.tBodies[0]) return;
    var cab = Array.prototype.map.call(t.tHead.rows[0].cells, function (c) { return c.textContent.trim(); });
    Array.prototype.forEach.call(t.tBodies[0].rows, function (tr) {
      var col = 0;
      Array.prototype.forEach.call(tr.cells, function (c) {
        if (c.tagName === "TD" && !c.hasAttribute("data-rotulo") && cab[col] && c.colSpan === 1) {
          c.setAttribute("data-rotulo", cab[col]);
        }
        col += c.colSpan || 1;
      });
    });
  });

  /* ---------- Tema (preferência local; nunca obrigatória) ---------- */
  function lerTema() {
    try { return localStorage.getItem("trajetoria-doc-tema"); } catch (e) { return null; }
  }
  function gravarTema(valor) {
    try { localStorage.setItem("trajetoria-doc-tema", valor); } catch (e) { /* sem armazenamento */ }
  }
  function temaEfetivo() {
    var t = raiz.getAttribute("data-theme");
    if (t) return t;
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  function atualizarBotaoTema() {
    if (!botaoTema) return;
    var escuro = temaEfetivo() === "dark";
    botaoTema.setAttribute("aria-pressed", escuro ? "true" : "false");
    botaoTema.querySelector(".so-leitor").textContent = escuro ? "Usar tema claro" : "Usar tema escuro";
  }
  var salvo = lerTema();
  if (salvo === "dark" || salvo === "light") raiz.setAttribute("data-theme", salvo);
  if (botaoTema) {
    botaoTema.hidden = false;
    botaoTema.addEventListener("click", function () {
      var novo = temaEfetivo() === "dark" ? "light" : "dark";
      raiz.setAttribute("data-theme", novo);
      gravarTema(novo);
      atualizarBotaoTema();
    });
    atualizarBotaoTema();
  }

  /* ---------- Menu lateral no celular ---------- */
  var desktop = window.matchMedia("(min-width: 64em)");
  function abrirMenu() {
    lateral.classList.add("aberta");
    veu.classList.add("visivel");
    botaoMenu.setAttribute("aria-expanded", "true");
    var primeiro = lateral.querySelector("a");
    if (primeiro) primeiro.focus();
  }
  function fecharMenu(devolverFoco) {
    lateral.classList.remove("aberta");
    veu.classList.remove("visivel");
    botaoMenu.setAttribute("aria-expanded", "false");
    if (devolverFoco) botaoMenu.focus();
  }
  if (botaoMenu && lateral) {
    botaoMenu.hidden = false;
    botaoMenu.addEventListener("click", function () {
      if (lateral.classList.contains("aberta")) fecharMenu(true); else abrirMenu();
    });
    veu.addEventListener("click", function () { fecharMenu(true); });
    document.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape" && lateral.classList.contains("aberta")) fecharMenu(true);
    });
    lateral.addEventListener("click", function (ev) {
      if (ev.target.closest("a") && !desktop.matches) fecharMenu(false);
    });
  }

  /* ---------- Seção atual na navegação ---------- */
  var links = Array.prototype.slice.call(document.querySelectorAll(".lateral nav a[href^='#']"));
  var porId = {};
  links.forEach(function (a) { porId[a.getAttribute("href").slice(1)] = a; });
  var secoes = Array.prototype.slice.call(document.querySelectorAll("section.doc[id]"))
    .filter(function (s) { return porId[s.id]; });

  function marcar(id) {
    links.forEach(function (a) { a.removeAttribute("aria-current"); });
    var a = porId[id];
    if (!a) return;
    a.setAttribute("aria-current", "true");
    if (desktop.matches) {
      var r = a.getBoundingClientRect();
      var rl = lateral.getBoundingClientRect();
      if (r.top < rl.top + 40 || r.bottom > rl.bottom - 40) {
        a.scrollIntoView({ block: "center" });
      }
    }
  }
  if ("IntersectionObserver" in window && secoes.length) {
    var visiveis = {};
    var obs = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (e) { visiveis[e.target.id] = e.isIntersecting; });
      for (var i = 0; i < secoes.length; i++) {
        if (visiveis[secoes[i].id]) { marcar(secoes[i].id); break; }
      }
    }, { rootMargin: "-72px 0px -65% 0px", threshold: 0 });
    secoes.forEach(function (s) { obs.observe(s); });
  }

  /* ---------- Voltar ao topo ---------- */
  if (voltar) {
    voltar.hidden = false;
    window.addEventListener("scroll", function () {
      voltar.classList.toggle("visivel", window.scrollY > 900);
    }, { passive: true });
  }

  /* ---------- Filtros de tabela ----------
     <div class="filtro" data-tabela="id-da-tabela"> com <select data-coluna="n"> e/ou
     <input type="search">. O select compara o texto da célula da coluna n (contém). */
  Array.prototype.forEach.call(document.querySelectorAll(".filtro[data-tabela]"), function (f) {
    var tabela = document.getElementById(f.getAttribute("data-tabela"));
    if (!tabela) return;
    f.hidden = false;
    var linhas = Array.prototype.slice.call(tabela.tBodies[0].rows);
    var selects = Array.prototype.slice.call(f.querySelectorAll("select[data-coluna]"));
    var busca = f.querySelector("input[type='search']");
    var contagem = f.querySelector(".contagem");
    function normalizar(s) {
      return (s || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
    }
    function aplicar() {
      var termo = busca ? normalizar(busca.value.trim()) : "";
      var n = 0;
      linhas.forEach(function (tr) {
        var ok = selects.every(function (s) {
          if (!s.value) return true;
          var c = tr.cells[parseInt(s.getAttribute("data-coluna"), 10)];
          return c && normalizar(c.textContent).indexOf(normalizar(s.value)) !== -1;
        });
        if (ok && termo) ok = normalizar(tr.textContent).indexOf(termo) !== -1;
        tr.hidden = !ok;
        if (ok) n++;
      });
      if (contagem) contagem.textContent = n + " de " + linhas.length + " linhas";
    }
    selects.forEach(function (s) { s.addEventListener("change", aplicar); });
    if (busca) busca.addEventListener("input", aplicar);
    aplicar();
  });
})();
