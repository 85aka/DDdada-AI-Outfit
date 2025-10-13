document.getElementById('regenerate-btn').addEventListener('click', function(event) {
    event.stopPropagation();  // 防止事件冒泡

    let btn = document.getElementById('regenerate-btn');
    btn.disabled = true;  // 禁用按鈕
    let loadingOverlay = document.getElementById('loading-overlay'); // Get the loading overlay element
    loadingOverlay.style.display = 'flex'; // Show the loading overlay

    let chatContainer = document.getElementById('chat-container');
    let messages = chatContainer.childNodes;
    let aiResponse = messages[messages.length - 1].innerText;

    // 发送请求以优化提示
    fetch('/optimize_prompt', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({"last_ai_response": aiResponse})
    })
    .then(response => response.json())
    .then(data => {
        if(data.error) {
            console.error("Optimization error:", data.error);
            btn.disabled = false;  // 啟用按鈕
            return;
        }

        let optimizedPrompt = data.optimized_prompt;
        console.log("Sending request to /generate_image with body:", JSON.stringify({"optimized_prompt": optimizedPrompt}));

        // 使用优化的提示生成图像
        return fetch('/generate_image', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({"optimized_prompt": optimizedPrompt})
        });
    })
    .then(response => response ? response.json() : null)
    .then(data => {
        if(data && data.error) {
            console.error("Image generation error:", data.error);
            return;
        }
        
        let imageUrl = data.image_url;
        document.getElementById('AI_img').src = imageUrl; // 显示生成的图像
    })
    .catch(error => {
        console.error("Error encountered:", error);
    })
    .finally(() => {
        btn.disabled = false;  // 啟用按鈕
        loadingOverlay.style.display = 'none'; // Hide the loading overlay
    });
});
