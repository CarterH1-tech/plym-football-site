// Progressive enhancements: game filters and the next-game countdown.
// The page is fully usable with JavaScript disabled.

(function () {
  "use strict";

  /* ---------- Filters ---------- */
  var games = Array.prototype.slice.call(document.querySelectorAll(".game"));
  var buttons = Array.prototype.slice.call(document.querySelectorAll(".filter"));
  var empty = document.getElementById("empty");

  function matches(el, filter) {
    switch (filter) {
      case "all": return true;
      case "home": return el.dataset.site === "home";
      case "away": return el.dataset.site === "away";
      case "conf": return el.dataset.conf === "1";
      case "final": return el.dataset.status === "final";
      case "upcoming": return el.dataset.status === "upcoming";
      default: return true;
    }
  }

  function apply(filter) {
    var visible = 0;
    games.forEach(function (el) {
      var show = matches(el, filter);
      el.classList.toggle("is-hidden", !show);
      if (show) visible++;
    });
    if (empty) empty.hidden = visible !== 0;
    buttons.forEach(function (b) {
      var active = b.dataset.filter === filter;
      b.classList.toggle("is-active", active);
      b.setAttribute("aria-pressed", active ? "true" : "false");
    });
  }

  buttons.forEach(function (b) {
    b.addEventListener("click", function () { apply(b.dataset.filter); });
  });

  /* ---------- Countdown ---------- */
  var cd = document.querySelector(".nextgame__countdown");
  if (cd && cd.closest(".nextgame") && cd.closest(".nextgame").dataset.kickoff) {
    var target = new Date(cd.closest(".nextgame").dataset.kickoff).getTime();

    var tick = function () {
      var diff = target - Date.now();
      if (isNaN(target)) { cd.textContent = ""; return; }
      if (diff <= 0) { cd.textContent = "Kicking off!"; return; }
      var d = Math.floor(diff / 86400000);
      var h = Math.floor((diff % 86400000) / 3600000);
      var m = Math.floor((diff % 3600000) / 60000);
      var s = Math.floor((diff % 60000) / 1000);
      cd.textContent =
        (d > 0 ? d + "d " : "") +
        (h > 0 || d > 0 ? h + "h " : "") +
        m + "m " + s + "s";
    };

    tick();
    setInterval(tick, 1000);
  }
})();
