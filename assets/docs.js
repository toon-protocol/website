/* The docs pages' behaviour, after herdr.dev/docs: the menu that opens the sidebar on a
   phone, the theme picker, the "On this page" highlight that follows the reader, and a copy
   button on every code block. Without this script the pages read the same: the sidebar sits
   above the page on a phone and the theme follows the system. */
(function () {
  var root = document.documentElement;
  root.classList.add("js");

  // The menu: a sheet over the page on a phone, closed by a link, Escape or a wider window.
  var menu = document.querySelector(".docs-header .menu");
  if (menu) {
    menu.hidden = false;
    var setOpen = function (open) {
      root.classList.toggle("nav-open", open);
      menu.setAttribute("aria-expanded", open ? "true" : "false");
    };
    var sidebar = document.querySelector(".sidebar");
    menu.addEventListener("click", function () { setOpen(!root.classList.contains("nav-open")); });
    sidebar.addEventListener("click", function (ev) { if (ev.target.closest("a")) setOpen(false); });
    document.addEventListener("keydown", function (ev) { if (ev.key === "Escape") setOpen(false); });
    matchMedia("(min-width: 50.01rem)").addEventListener("change", function (mq) { if (mq.matches) setOpen(false); });
    // Scroll the sidebar, not the page, to the page open.
    var current = sidebar.querySelector('a[aria-current="page"]');
    if (current && getComputedStyle(sidebar).position === "fixed")
      sidebar.scrollTop = current.offsetTop - sidebar.clientHeight / 2;
  }

  // The theme: dark, light, or auto (the system), kept in localStorage when it can be.
  // A button opens a menu of the three; arrows move, Enter or a click picks, Escape closes.
  var theme = document.querySelector(".docs-header .theme");
  if (theme) {
    var button = theme.querySelector(".theme-btn"), list = theme.querySelector(".theme-menu");
    var options = Array.prototype.slice.call(list.querySelectorAll("li"));
    var show = function (value) {
      options.forEach(function (li) {
        var on = li.getAttribute("data-value") === value;
        li.setAttribute("aria-selected", on ? "true" : "false");
        if (on) {
          button.querySelector(".icon").innerHTML = li.querySelector("svg").outerHTML;
          button.querySelector(".label").textContent = li.textContent;
          button.setAttribute("aria-label", "Theme: " + li.textContent);
        }
      });
    };
    var openMenu = function (open) {
      list.hidden = !open;
      button.setAttribute("aria-expanded", open ? "true" : "false");
      if (open) (list.querySelector('[aria-selected="true"]') || options[0]).focus();
    };
    var pick = function (value) {
      if (value === "auto") delete root.dataset.theme; else root.dataset.theme = value;
      try { if (value === "auto") localStorage.removeItem("toon-theme"); else localStorage.setItem("toon-theme", value); } catch (e) {}
      show(value);
      openMenu(false);
      button.focus();
    };
    show(root.dataset.theme || "auto");
    theme.hidden = false;
    button.addEventListener("click", function () { openMenu(list.hidden); });
    list.addEventListener("click", function (ev) {
      var li = ev.target.closest("li");
      if (li) pick(li.getAttribute("data-value"));
    });
    list.addEventListener("keydown", function (ev) {
      var i = options.indexOf(document.activeElement);
      if (ev.key === "ArrowDown" || ev.key === "ArrowUp") {
        ev.preventDefault();
        options[(i + (ev.key === "ArrowDown" ? 1 : options.length - 1)) % options.length].focus();
      } else if (ev.key === "Enter" || ev.key === " ") {
        ev.preventDefault();
        if (i !== -1) pick(options[i].getAttribute("data-value"));
      } else if (ev.key === "Escape") {
        ev.stopPropagation(); openMenu(false); button.focus();
      } else if (ev.key === "Tab") openMenu(false);
    });
    document.addEventListener("click", function (ev) { if (!list.hidden && !theme.contains(ev.target)) openMenu(false); });
  }

  // "On this page": the heading the reader is in is the last one above the top of the page.
  var links = Array.prototype.slice.call(document.querySelectorAll(".toc a, .mtoc a"));
  var label = document.querySelector(".mtoc summary span");
  var targets = [], seen = {};
  links.forEach(function (a) {
    var id = decodeURIComponent(a.hash.slice(1));
    if (seen[id]) return;
    var el = document.getElementById(id);
    if (el) { seen[id] = true; targets.push(el); }
  });
  if (targets.length) {
    var ticking = false;
    var update = function () {
      ticking = false;
      var line = parseFloat(getComputedStyle(root).scrollPaddingTop) || 100, at = targets[0];
      for (var i = 0; i < targets.length; i++) {
        if (targets[i].getBoundingClientRect().top <= line + 1) at = targets[i]; else break;
      }
      // At the foot of the page the last heading is the one being read, however short.
      if (innerHeight + scrollY >= root.scrollHeight - 2) at = targets[targets.length - 1];
      links.forEach(function (a) {
        var on = a.hash === "#" + at.id;
        if (on) a.setAttribute("aria-current", "true"); else a.removeAttribute("aria-current");
        if (on && label) label.textContent = a.textContent;
      });
    };
    addEventListener("scroll", function () { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
    update();
  }
  var mtoc = document.querySelector(".mtoc");
  if (mtoc) mtoc.addEventListener("click", function (ev) { if (ev.target.closest("a")) mtoc.open = false; });

  // Copy buttons: in the header of a terminal card, and in the corner of a plain code block.
  function copier(text, where) {
    var button = document.createElement("button");
    button.type = "button";
    button.textContent = "copy";
    button.addEventListener("click", function () {
      var done = function () {
        button.textContent = "copied"; button.classList.add("done");
        setTimeout(function () { button.textContent = "copy"; button.classList.remove("done"); }, 1400);
      };
      if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(text()).then(done);
    });
    where.appendChild(button);
  }
  if (!(navigator.clipboard && window.isSecureContext)) return;
  document.querySelectorAll(".doc .ev").forEach(function (ev) {
    var hd = ev.querySelector(".hd");
    if (!hd || hd.querySelector("button")) return;
    copier(function () {
      var lines = ev.querySelectorAll(".l");
      if (!lines.length) return (ev.querySelector("pre") || ev).textContent.trim();
      return Array.prototype.map.call(lines, function (l) { return l.textContent.trim(); }).join("\n");
    }, hd);
  });
  document.querySelectorAll(".doc pre").forEach(function (pre) {
    if (pre.closest(".ev")) return;
    var box = document.createElement("div");
    box.className = "copybox";
    pre.parentNode.insertBefore(box, pre);
    box.appendChild(pre);
    copier(function () { return pre.textContent.replace(/\n$/, ""); }, box);
  });
})();
