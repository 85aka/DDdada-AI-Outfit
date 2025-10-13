document.getElementById("chat-form").addEventListener("submit", function (e) {
    e.preventDefault();
    const userMessage = document.getElementById("user-message").value;

    // Display user message
    const userMessageDiv = document.createElement("div");
    userMessageDiv.className = "user-message";
    userMessageDiv.textContent = "You: " + userMessage;
    document.getElementById("chat-container").appendChild(userMessageDiv);

    // 顯示暫時的載入訊息
    const loadingMessageDiv = document.createElement("div");
    loadingMessageDiv.className = "loading-message";
    loadingMessageDiv.textContent = "回應中，請稍候...";
    loadingMessageDiv.id = "loading-message";
    document.getElementById("chat-container").appendChild(loadingMessageDiv);

    // Send user message to the server
    fetch("/chat", {
        method: "POST",
        body: JSON.stringify({ user_message: userMessage }),
        headers: {
            "Content-Type": "application/json",
        },
    })
    .then((response) => response.json())
    .then((data) => {
        // Remove the temporary loading message
        const loadingElement = document.getElementById("loading-message");
        if (loadingElement) {
            loadingElement.parentNode.removeChild(loadingElement);
        }

        // 顯示助理回覆
        const aiMessageDiv = document.createElement("div");
        aiMessageDiv.className = "ai-message";
        aiMessageDiv.textContent = "Chatbot: " + data.ai_msg;
        document.getElementById("chat-container").appendChild(aiMessageDiv);
    });

    // Clear the input field
    document.getElementById("user-message").value = "";
});

