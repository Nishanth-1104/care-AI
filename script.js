const input = document.getElementById("userInput");
const chatBox = document.getElementById("chatBox");
const welcomePanel = document.getElementById("welcomePanel");
const unavailableMessage =
  "⚠️ CAREAI is temporarily unavailable. Please make sure the Python server is running and try again.";

function saveChat() {
  localStorage.setItem("careaiChat", chatBox.innerHTML);
}

function addMessage(text, className) {
  const message = document.createElement("div");
  message.className = className;
  message.textContent = text;
  chatBox.appendChild(message);
  return message;
}

function loadChat() {
  const savedChat = localStorage.getItem("careaiChat");
  if (savedChat) {
    chatBox.innerHTML = savedChat;
    welcomePanel.hidden = true;
  }
}

async function sendMessage() {
  const message = input.value.trim();
  if (!message) return;

  welcomePanel.hidden = true;
  addMessage(message, "user-message");
  saveChat();
  input.value = "";

  const typing = document.createElement("div");
  typing.className = "bot-message";
  typing.innerHTML =
    '<span class="typing-text">CAREAI</span><span class="typing-dots"><span>.</span><span>.</span><span>.</span></span>';
  chatBox.appendChild(typing);
  chatBox.scrollTop = chatBox.scrollHeight;

  await new Promise((resolve) => setTimeout(resolve, 1000));

  try {
    const response = await fetch("http://127.0.0.1:5000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    const data = await response.json();
    if (!response.ok || typeof data.response !== "string") {
      throw new Error(data.error || "Invalid server response.");
    }

    typing.remove();
    addMessage(data.response, "bot-message");
  } catch (error) {
    typing.remove();
    addMessage(unavailableMessage, "bot-message");
    console.error(error);
  }

  saveChat();
  chatBox.scrollTop = chatBox.scrollHeight;
}

function startVoice() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    alert("Voice input is not supported in this browser.");
    return;
  }

  const recognition = new SpeechRecognition();
  recognition.lang = navigator.language || "en-US";
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;
  recognition.onresult = (event) => {
    input.value = event.results[0][0].transcript;
  };
  recognition.onerror = (event) => {
    console.error("Voice recognition failed:", event.error);
    alert("Voice input could not be completed. Please try again.");
  };
  recognition.start();
}

function quickMessage(message) {
  input.value = message;
  sendMessage();
}

function clearChat() {
  if (!confirm("Are you sure you want to clear the chat?")) return;
  chatBox.innerHTML = "";
  localStorage.removeItem("careaiChat");
  welcomePanel.hidden = false;
}

input.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    sendMessage();
  }
});

loadChat();
