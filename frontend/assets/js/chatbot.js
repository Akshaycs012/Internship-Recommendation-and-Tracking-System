document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("chatForm");
  const input = document.getElementById("chatInput");
  const chatWindow = document.getElementById("chatWindow");

  function appendMessage(text, role) {
    const div = document.createElement("div");
    div.classList.add("chat-message", role);
    div.textContent = (role === "user" ? "You: " : "Bot: ") + text;
    chatWindow.appendChild(div);
    chatWindow.scrollTop = chatWindow.scrollHeight;
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const message = input.value.trim();
    if (!message) return;

    appendMessage(message, "user");
    input.value = "";

    // TODO: Send to backend /chatbot endpoint
    // For now, simple placeholder response:
    setTimeout(() => {
      appendMessage(
        "This is a placeholder response. Later this will use FastAPI + AI to suggest internships.",
        "bot"
      );
    }, 300);
  });
});
