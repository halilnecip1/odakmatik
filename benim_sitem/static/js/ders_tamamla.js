// static/js/ders_tamamla.js

document.addEventListener("DOMContentLoaded", function () {
  const buttons = document.querySelectorAll(".ders-tamamla-btn");

  buttons.forEach((button) => {
    button.addEventListener("click", function () {
      const dersId = this.dataset.dersId;
      const csrfToken = getCSRFToken();

      fetch(`/ilerleme/tamamla/${dersId}/`, {
        method: "POST",
        headers: {
          "X-CSRFToken": csrfToken,
          "X-Requested-With": "XMLHttpRequest",
          "Content-Type": "application/json"
        },
        body: JSON.stringify({})
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error("HTTP error " + response.status);
          }
          return response.json();
        })
        .then((data) => {
          if (data.basarili) {
            button.disabled = true;
            button.classList.remove("btn-success");
            button.classList.add("btn-secondary");
            button.textContent = "✓ Tamamlandı";
          }
        })
        .catch((error) => {
          console.error("Tamamlama isteği başarısız oldu:", error);
        });
    });
  });
});

function getCSRFToken() {
  const cookies = document.cookie.split(";");
  for (let i = 0; i < cookies.length; i++) {
    const cookie = cookies[i].trim();
    if (cookie.startsWith("csrftoken=")) {
      return cookie.substring("csrftoken=".length, cookie.length);
    }
  }
  return "";
}
