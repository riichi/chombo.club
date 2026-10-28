// Theme toggle, table-of-contents behaviour and the search dialog.
// Everything here is an enhancement: the site works without JavaScript.
(function () {
  "use strict";

  var root = document.documentElement;

  // Theme: auto (follow the OS) -> light -> dark. The initial value is applied
  // by an inline script in <head> to avoid a flash of the wrong theme.
  var THEME_MODES = ["auto", "light", "dark"];

  function currentThemeMode() {
    return root.dataset.themeMode || "auto";
  }

  function updateThemeLabels() {
    var mode = currentThemeMode();
    document.querySelectorAll("[data-theme-toggle]").forEach(function (button) {
      var label = button.dataset.label + ": " + button.getAttribute("data-label-" + mode);
      button.setAttribute("aria-label", label);
      var text = button.querySelector("[data-theme-text]");
      if (text) text.textContent = label;
    });
  }

  function setThemeMode(mode) {
    root.dataset.themeMode = mode;
    if (mode === "auto") {
      delete root.dataset.theme;
    } else {
      root.dataset.theme = mode;
    }
    try {
      if (mode === "auto") {
        localStorage.removeItem("theme");
      } else {
        localStorage.setItem("theme", mode);
      }
    } catch (e) {}
    updateThemeLabels();
  }

  document.addEventListener("click", function (event) {
    var button = event.target.closest("[data-theme-toggle]");
    if (!button) return;
    var next = THEME_MODES[(THEME_MODES.indexOf(currentThemeMode()) + 1) % THEME_MODES.length];
    setThemeMode(next);
  });

  updateThemeLabels();

  // Table of contents: always open on wide screens (sidebar), collapsed by
  // default on narrow ones, and highlights the section being read.
  var toc = document.querySelector(".toc");
  if (toc) {
    var details = toc.querySelector("details");
    var wide = window.matchMedia("(min-width: 1100px)");

    var syncOpen = function () {
      details.open = wide.matches;
    };
    syncOpen();
    wide.addEventListener("change", syncOpen);

    var links = Array.prototype.slice.call(toc.querySelectorAll('a[href^="#"]')).filter(function (link) {
      return link.hash.length > 1 && link.closest(".toc__list");
    });
    var headings = links.map(function (link) {
      return document.getElementById(decodeURIComponent(link.hash.slice(1)));
    });

    toc.addEventListener("click", function (event) {
      if (event.target.closest(".toc__list a") && !wide.matches) details.open = false;
    });

    var activeIndex = -1;
    var updateActive = function () {
      var offset = window.innerHeight * 0.25;
      var index = -1;
      for (var i = 0; i < headings.length; i++) {
        if (headings[i] && headings[i].getBoundingClientRect().top <= offset) index = i;
      }
      // At the very bottom of the page, the last section wins.
      if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 2) {
        index = headings.length - 1;
      }
      if (index === activeIndex) return;
      if (activeIndex >= 0) links[activeIndex].removeAttribute("aria-current");
      if (index >= 0) links[index].setAttribute("aria-current", "location");
      activeIndex = index;
    };

    var ticking = false;
    window.addEventListener("scroll", function () {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(function () {
        updateActive();
        ticking = false;
      });
    }, { passive: true });
    window.addEventListener("resize", updateActive);
    updateActive();
  }

  // Search: Pagefind's UI, loaded the first time the dialog opens. The index
  // only exists in builds that ran `pagefind --site _site`.
  var dialog = document.getElementById("search-dialog");
  var pagefindRequested = false;

  function showSearchUnavailable() {
    dialog.querySelector(".search-dialog__unavailable").hidden = false;
  }

  function loadPagefind() {
    if (pagefindRequested) return;
    pagefindRequested = true;

    var css = document.createElement("link");
    css.rel = "stylesheet";
    css.href = "/pagefind/pagefind-ui.css";
    document.head.appendChild(css);

    var script = document.createElement("script");
    script.src = "/pagefind/pagefind-ui.js";
    script.onload = function () {
      if (typeof window.PagefindUI !== "function") {
        showSearchUnavailable();
        return;
      }
      new window.PagefindUI({ element: "#search", showSubResults: true, autofocus: true });
      var input = dialog.querySelector("input");
      if (input) input.focus();
    };
    script.onerror = showSearchUnavailable;
    document.head.appendChild(script);
  }

  if (dialog && typeof dialog.showModal === "function") {
    document.addEventListener("click", function (event) {
      if (event.target.closest("[data-search-open]")) {
        dialog.showModal();
        loadPagefind();
        var input = dialog.querySelector("input");
        if (input) input.focus();
      } else if (event.target.closest("[data-search-close]") || event.target === dialog) {
        dialog.close();
      }
    });
  } else {
    document.querySelectorAll("[data-search-open]").forEach(function (button) {
      button.hidden = true;
    });
  }
})();
