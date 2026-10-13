function saveChat() {
    const chatBox = document.getElementById("chatBox");
    localStorage.setItem("careaiChat", chatBox.innerHTML);
}

function loadChat() {
    const chatBox = document.getElementById("chatBox");
    const savedChat = localStorage.getItem("careaiChat");

    if (savedChat) {
        chatBox.innerHTML = savedChat;
    }
}
async function sendMessage() {
    const input = document.getElementById("userInput");
    const chatBox = document.getElementById("chatBox");

    const userMessage = input.value.trim();

    if (userMessage === "") {
        return;
    }

    // Show user message
    const userDiv = document.createElement("div");
    userDiv.className = "user-message";
    userDiv.textContent = userMessage;
    chatBox.appendChild(userDiv);
    saveChat();

    input.value = "";

    // Typing indicator
    const typingDiv = document.createElement("div");
    typingDiv.className = "bot-message";

    typingDiv.innerHTML = `
        <span class="typing-text">CAREAI</span>
        <span class="typing-dots">
            <span>.</span>
            <span>.</span>
            <span>.</span>
        </span>
    `;

    chatBox.appendChild(typingDiv);
    chatBox.scrollTop = chatBox.scrollHeight;

    // Wait 1 second before sending to Python
    await new Promise(resolve => setTimeout(resolve, 1000));

    try {
        // Send message to Python Flask
            const response = await fetch("http://127.0.0.1:5000/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: userMessage
            })
        });

        const data = await response.json();

        // Remove typing indicator
        typingDiv.remove();

        // Show Python response
        const botDiv = document.createElement("div");
        botDiv.className = "bot-message";
        botDiv.textContent = data.response;

        chatBox.appendChild(botDiv);
        saveChat();

        chatBox.scrollTop = chatBox.scrollHeight;

    } catch (error) {

        typingDiv.remove();

        const botDiv = document.createElement("div");
        botDiv.className = "bot-message";
        botDiv.textContent =
           "⚠️ CAREAI is temporarily unavailable. Please make sure the Python server is running and try again.";
        chatBox.appendChild(botDiv);

        console.error(error);
    }
}


// Enter key
document.getElementById("userInput").addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        sendMessage();
    }
});


// Try asking buttons
function quickMessage(message) {
    const input = document.getElementById("userInput");

    input.value = message;

    sendMessage();
}
function clearChat() {
    const confirmClear = confirm("Are you sure you want to clear the chat?");

    if (!confirmClear) {
        return;
    }

    const chatBox = document.getElementById("chatBox");
    chatBox.innerHTML = "";
    localStorage.removeItem("careaiChat");
}
loadChat();
