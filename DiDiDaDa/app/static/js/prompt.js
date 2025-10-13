
document.addEventListener('DOMContentLoaded', () => {
  const generateBtn = document.getElementById('generate-btn');
  const regenerateBtn = document.getElementById('regenerate-btn');
  const loadingOverlay = document.getElementById('loading-overlay');

  async function generateWithPrompt(optimizedPrompt) {
    try {
      loadingOverlay && (loadingOverlay.style.display = 'block');
      const res = await fetch('/generate_image', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ optimized_prompt: optimizedPrompt })
      });
      const data = await res.json();
      if (data.image_url) {
        const img = document.getElementById('AI_img');
        if (img) img.src = data.image_url;
      }
    } catch (err) {
      console.error('生成失敗：', err);
    } finally {
      loadingOverlay && (loadingOverlay.style.display = 'none');
    }
  }

  async function optimizeAndGenerate() {
    try {
      const chatContainer = document.getElementById('chat-container');
      const lastAi = chatContainer ? chatContainer.lastElementChild?.textContent || '' : '';
      const lastAiResponse = lastAi.replace(/^Chatbot:\s*/, '');
      const res = await fetch('/optimize_prompt', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ last_ai_response: lastAiResponse })
      });
      const data = await res.json();
      if (data.optimized_prompt) {
        await generateWithPrompt(data.optimized_prompt);
      }
    } catch (e) {
      console.error('優化失敗：', e);
    }
  }

  generateBtn && generateBtn.addEventListener('click', optimizeAndGenerate);
  regenerateBtn && regenerateBtn.addEventListener('click', optimizeAndGenerate);
});

