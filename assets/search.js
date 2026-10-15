/* The docs search. A button in the docs header opens a dialog over the page; "/" or
   Ctrl+K opens it from anywhere. The index (docs/search-index.js, written by
   build.py) is one record per page section, {u: url, p: page, s: section, t: text}, and is
   loaded the first time the dialog opens. Without this script the buttons stay hidden. */
(function () {
  var dialog = document.querySelector("dialog.docsearch");
  if (!dialog || !dialog.showModal) return;
  var input = dialog.querySelector("input"), list = dialog.querySelector(".results");
  var index = null, loading = false, active = -1;
  var LIMIT = 10;

  function load() {
    if (index || loading) return;
    loading = true;
    var script = document.createElement("script");
    script.src = dialog.getAttribute("data-index");
    script.onload = function () {
      index = (window.TOON_DOCS_INDEX || []).map(function (r) {
        return { r: r, p: r.p.toLowerCase(), s: r.s.toLowerCase(), t: r.t.toLowerCase() };
      });
      render();
    };
    document.head.appendChild(script);
  }

  function escape(text) {
    return text.replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; });
  }

  function count(hay, term) {
    var n = 0, i = hay.indexOf(term);
    while (i !== -1 && n < 5) { n++; i = hay.indexOf(term, i + term.length); }
    return n;
  }

  function termsOf(query) { return query.toLowerCase().trim().split(/\s+/).filter(Boolean); }

  // Every term must appear somewhere; a section heading outranks a page title, which
  // outranks the body, and the whole query as a phrase outranks its words apart.
  function search(query) {
    var q = query.toLowerCase().trim(), terms = termsOf(query), hits = [];
    index.forEach(function (e) {
      var score = 0;
      for (var i = 0; i < terms.length; i++) {
        var term = terms[i], inS = e.s.indexOf(term) !== -1, inP = e.p.indexOf(term) !== -1, inT = count(e.t, term);
        if (!inS && !inP && !inT) return;
        score += (inS ? 10 : 0) + (inP ? 6 : 0) + inT;
      }
      if (terms.length > 1) {
        if (e.s.indexOf(q) !== -1 || e.p.indexOf(q) !== -1) score += 15;
        else if (e.t.indexOf(q) !== -1) score += 8;
      }
      hits.push({ e: e, score: score });
    });
    hits.sort(function (a, b) { return b.score - a.score; });
    return hits.slice(0, LIMIT).map(function (h) { return h.e; });
  }

  // Marks every occurrence of every term, merging overlaps, and escapes the rest.
  function highlight(text, terms) {
    var lower = text.toLowerCase(), on = [];
    terms.forEach(function (term) {
      for (var i = lower.indexOf(term); i !== -1; i = lower.indexOf(term, i + 1))
        for (var j = i; j < i + term.length; j++) on[j] = true;
    });
    var out = "", open = false;
    for (var k = 0; k < text.length; k++) {
      if (!!on[k] !== open) { out += open ? "</mark>" : "<mark>"; open = !open; }
      out += escape(text[k]);
    }
    return out + (open ? "</mark>" : "");
  }

  // A stretch of the section's text around the first term it contains, cut at word edges.
  function snippet(e, terms) {
    var text = e.r.t, at = -1;
    for (var i = 0; i < terms.length && at === -1; i++) at = e.t.indexOf(terms[i]);
    var start = at > 40 ? text.lastIndexOf(" ", at - 40) + 1 : 0;
    var end = Math.min(text.length, start + 160);
    if (end < text.length) end = Math.max(text.lastIndexOf(" ", end), start + 1);
    return (start > 0 ? "…" : "") + text.slice(start, end) + (end < text.length ? "…" : "");
  }

  // Results are grouped under their page, pages in the order of their best result.
  function render() {
    var query = input.value, terms = termsOf(query);
    active = -1;
    if (!terms.length) { list.innerHTML = '<p class="empty">Search every docs page by heading or text.</p>'; return; }
    if (!index) { list.innerHTML = '<p class="empty">Loading the index…</p>'; return; }
    var hits = search(query);
    if (!hits.length) { list.innerHTML = '<p class="empty">Nothing in the docs matches “' + escape(query.trim()) + "”.</p>"; return; }
    var pages = [], byPage = {};
    hits.forEach(function (e) {
      if (!byPage[e.r.p]) { byPage[e.r.p] = []; pages.push(e.r.p); }
      byPage[e.r.p].push(e);
    });
    list.innerHTML = pages.map(function (page) {
      return '<div class="hits"><h4>' + escape(page) + "</h4>" + byPage[page].map(function (e) {
        return '<a href="' + escape(e.r.u) + '"><span class="title">' + highlight(e.r.s || e.r.p, terms) + "</span>" +
          '<span class="text">' + highlight(snippet(e, terms), terms) + "</span></a>";
      }).join("") + "</div>";
    }).join("");
    select(0);
  }

  function select(i) {
    var items = list.querySelectorAll("a");
    if (!items.length) return;
    active = (i + items.length) % items.length;
    Array.prototype.forEach.call(items, function (a, j) { a.classList.toggle("active", j === active); });
    if (i !== 0 || active !== 0) items[active].scrollIntoView({ block: "nearest" });
  }

  function open() {
    if (dialog.open) return;
    dialog.showModal();
    document.documentElement.classList.add("searching");
    input.select();
    load();
    render();
  }

  dialog.addEventListener("close", function () { document.documentElement.classList.remove("searching"); });
  // A click on the backdrop lands on the dialog itself, outside its panel.
  dialog.addEventListener("click", function (ev) { if (ev.target === dialog) dialog.close(); });
  dialog.querySelector(".close").addEventListener("click", function () { dialog.close(); });
  input.addEventListener("input", render);
  input.addEventListener("keydown", function (ev) {
    if (ev.key === "ArrowDown") { ev.preventDefault(); select(active + 1); }
    else if (ev.key === "ArrowUp") { ev.preventDefault(); select(active - 1); }
  });
  dialog.querySelector("form").addEventListener("submit", function (ev) {
    ev.preventDefault();
    var items = list.querySelectorAll("a");
    if (items.length) { dialog.close(); location.href = items[Math.max(active, 0)].href; }
  });
  // A result in the page already open only moves the hash, so close the dialog first.
  list.addEventListener("click", function (ev) { if (ev.target.closest("a")) dialog.close(); });
  list.addEventListener("mousemove", function (ev) {
    var a = ev.target.closest("a");
    if (a) select(Array.prototype.indexOf.call(list.querySelectorAll("a"), a));
  });

  Array.prototype.forEach.call(document.querySelectorAll(".docsearch-open"), function (button) {
    button.hidden = false;
    button.addEventListener("click", open);
  });
  document.addEventListener("keydown", function (ev) {
    // Ctrl+K or Cmd+K opens it from anywhere, as on herdr.dev; "/" only outside a field.
    if ((ev.ctrlKey || ev.metaKey) && !ev.altKey && ev.key.toLowerCase() === "k") { ev.preventDefault(); if (!dialog.open) open(); return; }
    if (ev.key !== "/" || ev.ctrlKey || ev.metaKey || ev.altKey || dialog.open) return;
    var t = ev.target;
    if (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName)) return;
    ev.preventDefault();
    open();
  });
})();
