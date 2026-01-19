/*
app.js
------
JS mínimo e útil:
- Tema claro/escuro com persistência (localStorage)
- Preencher caixa de pergunta ao clicar numa sugestão
*/

(function initTheme() {
  const stored = localStorage.getItem("theme") || "light";
  document.documentElement.setAttribute("data-theme", stored);

  const btn = document.getElementById("themeToggle");
  if (btn) {
    btn.addEventListener("click", () => {
      const current = document.documentElement.getAttribute("data-theme") || "light";
      const next = current === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      localStorage.setItem("theme", next);
    });
  }
})();

function fillQuestion(text) {
  const input = document.querySelector('input[name="question"]');
  if (input) {
    input.value = text;
    input.focus();
  }
}

// Sugestões: clicar e preencher a pergunta (sem inline JS / sem JSON)
document.addEventListener("DOMContentLoaded", () => {
  const input = document.querySelector('input[name="question"]');
  document.querySelectorAll(".suggestion-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      if (!input) return;
      input.value = btn.getAttribute("data-question") || "";
      input.focus();
    });
  });
});
