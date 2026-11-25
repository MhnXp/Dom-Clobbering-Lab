/* Shared helpers for every lab page. */
(function () {
  "use strict";

  var ESC = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };

  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, function (c) { return ESC[c]; });
  }

  function clock() {
    return new Date().toTimeString().slice(0, 8);
  }

  var Lab = {
    /* set by each lab's runVictim(), used to filter collector entries */
    startedAt: Date.now(),

    escapeHtml: escapeHtml,

    /** Human readable description of whatever a victim variable resolved to. */
    describe: function (value) {
      if (value === undefined) return "undefined";
      if (value === null) return "null";
      if (typeof value === "string") return JSON.stringify(value);
      if (typeof value === "function") return "function () { … }";
      var name = (value.constructor && value.constructor.name) || typeof value;
      var tag = value.nodeName ? " <" + String(value.nodeName).toLowerCase() + ">" : "";
      return name + tag;
    },

    log: function (message, cls) {
      var box = document.getElementById("evidence");
      if (!box) return;
      var line = document.createElement("div");
      line.className = "line " + (cls || "");
      line.innerHTML = '<span class="t">' + clock() + "</span> " + escapeHtml(message);
      box.appendChild(line);
      box.scrollTop = box.scrollHeight;
    },

    clearLog: function () {
      var box = document.getElementById("evidence");
      if (box) box.innerHTML = "";
    },

    /** Render user controlled HTML into the simulated vulnerable page. */
    inject: function (html) {
      var victim = document.getElementById("victim");
      if (victim) victim.innerHTML = html == null ? "" : html;
    },

    wipe: function () {
      var victim = document.getElementById("victim");
      if (victim) victim.innerHTML = "";
    },

    entries: function () {
      return fetch("/collect.json", { cache: "no-store" })
        .then(function (r) { return r.ok ? r.json() : []; })
        .catch(function () { return []; });
    },

    /** Collector entries created after this page performed its last run. */
    since: function (timestamp) {
      return Lab.entries().then(function (rows) {
        return rows.filter(function (row) { return row.ts * 1000 >= timestamp; });
      });
    },

    clearCollector: function () {
      return fetch("/reset", { method: "POST" }).catch(function () {});
    },

    wait: function (ms) {
      return new Promise(function (resolve) { setTimeout(resolve, ms); });
    },

    isSolved: function (id) {
      try {
        var map = JSON.parse(localStorage.getItem("domlab.solved") || "{}");
        return Boolean(map[id]);
      } catch (err) {
        return false;
      }
    },

    solved: function (id, flag) {
      try {
        var map = JSON.parse(localStorage.getItem("domlab.solved") || "{}");
        map[id] = Date.now();
        localStorage.setItem("domlab.solved", JSON.stringify(map));
      } catch (err) { /* ignore */ }
      var banner = document.getElementById("flag");
      if (banner) {
        banner.textContent = "✔ Solved — " + flag;
        banner.classList.remove("hidden");
      }
    },

    showExistingSolve: function (id) {
      if (!Lab.isSolved(id)) return;
      var banner = document.getElementById("flag");
      if (banner) {
        banner.textContent = "✔ You solved this lab earlier. Run the exploit again to see it live.";
        banner.classList.remove("hidden");
      }
    },

    /** Wire the standard run/verify/reset buttons for a lab. */
    wire: function (options) {
      var runBtn = document.getElementById("run");
      var verifyBtn = document.getElementById("verify");
      var resetBtn = document.getElementById("reset");

      if (runBtn) runBtn.addEventListener("click", options.run);
      if (verifyBtn) verifyBtn.addEventListener("click", options.verify);
      if (resetBtn) {
        resetBtn.addEventListener("click", function () {
          Lab.wipe();
          Lab.clearLog();
          if (options.reset) options.reset();
        });
      }
    }
  };

  window.Lab = Lab;
})();
