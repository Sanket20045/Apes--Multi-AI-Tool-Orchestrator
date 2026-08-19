/**
 * Pleximus AI Agent — Web UI Client Logic
 * ========================================
 * Handles chat communication with /api/chat, renders rich messages,
 * shows tool execution badges, and manages interactive UI states.
 */

document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements
  const chatMessages = document.getElementById("chat-messages");
  const chatForm = document.getElementById("chat-form");
  const userInput = document.getElementById("user-input");
  const sendBtn = document.getElementById("send-btn");
  const clearChatBtn = document.getElementById("clear-chat-btn");
  const connectionBadge = document.getElementById("connection-badge");
  const connectionText = document.getElementById("connection-text");
  const welcomeCard = document.getElementById("welcome-card");
  const quickPromptsBar = document.getElementById("quick-prompts-bar");

  let isGenerating = false;

  // Tool visual metadata
  const TOOL_ICONS = {
    calculator: "🧮",
    weather_lookup: "🌦️",
    text_utility: "📝",
    currency_converter: "💱"
  };

  const TOOL_LABELS = {
    calculator: "calculator",
    weather_lookup: "weather_lookup",
    text_utility: "text_utility",
    currency_converter: "currency_converter"
  };

  // 1. Fetch Backend & Gemini Connection Status
  async function checkServerStatus() {
    try {
      const res = await fetch("/api/status");
      if (!res.ok) throw new Error("Status endpoint unavailable");
      const data = await res.json();

      connectionBadge.className = "status-pill";
      if (data.gemini_connected) {
        connectionBadge.classList.add("status-online");
        connectionText.textContent = `${data.model || "Gemini"} Live`;
      } else {
        connectionBadge.classList.add("status-fallback");
        connectionText.textContent = "Local Mode Active";
      }
    } catch (err) {
      connectionBadge.className = "status-pill status-fallback";
      connectionText.textContent = "Offline Mode";
    }
  }

  // 2. Auto-expand textarea on input
  userInput.addEventListener("input", () => {
    userInput.style.height = "auto";
    userInput.style.height = Math.min(userInput.scrollHeight, 120) + "px";
  });

  // 3. Handle Enter key for submit (Shift+Enter for newline)
  userInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      chatForm.dispatchEvent(new Event("submit", { cancelable: true }));
    }
  });

  // 4. Quick Suggestion Chip Click Handlers
  document.querySelectorAll("[data-query]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const query = btn.getAttribute("data-query");
      if (query && !isGenerating) {
        userInput.value = query;
        userInput.style.height = "auto";
        chatForm.dispatchEvent(new Event("submit", { cancelable: true }));
      }
    });
  });

  // Clear Chat Handler
  clearChatBtn.addEventListener("click", () => {
    chatMessages.innerHTML = "";
    if (welcomeCard) {
      chatMessages.appendChild(welcomeCard);
    }
  });

  // 6. Form Submission Handler
  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const query = userInput.value.trim();

    if (!query || isGenerating) return;

    // Remove welcome card on first message
    if (welcomeCard && welcomeCard.parentElement === chatMessages) {
      welcomeCard.remove();
      quickPromptsBar.classList.remove("hidden");
    }

    // Append User Message
    appendUserMessage(query);

    // Reset input
    userInput.value = "";
    userInput.style.height = "auto";
    setGeneratingState(true);

    // Show typing / thinking indicator
    const typingIndicator = appendTypingIndicator();
    scrollToBottom();

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: query })
      });

      typingIndicator.remove();

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || "Server returned an error");
      }

      const data = await response.json();
      appendAgentMessage(data.response || "No response received.", data.tools_used || []);

    } catch (error) {
      if (typingIndicator) typingIndicator.remove();
      appendAgentMessage(`⚠️ Error: ${error.message || "Could not connect to agent service."}`, []);
    } finally {
      setGeneratingState(false);
      scrollToBottom();
      userInput.focus();
    }
  });

  function setGeneratingState(generating) {
    isGenerating = generating;
    sendBtn.disabled = generating;
  }

  function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  // 7. Append User Message
  function appendUserMessage(text) {
    const row = document.createElement("div");
    row.className = "message-row user-message-row";

    row.innerHTML = `
      <div class="message-avatar user-avatar">
        <span>👤</span>
      </div>
      <div class="message-content-wrapper">
        <div class="message-bubble user-bubble">${escapeHtml(text)}</div>
      </div>
    `;

    chatMessages.appendChild(row);
  }

  // 8. Append Agent Message with Tool Badges
  function appendAgentMessage(markdownText, toolsUsed) {
    const row = document.createElement("div");
    row.className = "message-row agent-message-row";

    let toolsHtml = "";
    if (toolsUsed && toolsUsed.length > 0) {
      toolsHtml = `
        <div class="tool-used-banner">
          ${toolsUsed.map(t => `
            <span class="tool-used-tag tool-${t.name}">
              <span>${TOOL_ICONS[t.name] || "⚡"}</span>
              <span>Tool selected: <strong>${TOOL_LABELS[t.name] || t.name}</strong></span>
            </span>
          `).join("")}
        </div>
      `;
    }

    const formattedContent = parseMarkdown(markdownText);

    row.innerHTML = `
      <div class="message-avatar agent-avatar">
        <span>✦</span>
      </div>
      <div class="message-content-wrapper">
        ${toolsHtml}
        <div class="message-bubble agent-bubble">
          ${formattedContent}
        </div>
      </div>
    `;

    chatMessages.appendChild(row);
  }

  // 9. Append Animated Typing Indicator
  function appendTypingIndicator() {
    const row = document.createElement("div");
    row.className = "message-row agent-message-row typing-row";

    row.innerHTML = `
      <div class="message-avatar agent-avatar">
        <span>✦</span>
      </div>
      <div class="message-content-wrapper">
        <div class="message-bubble agent-bubble typing-indicator">
          <span class="typing-dot"></span>
          <span class="typing-dot"></span>
          <span class="typing-dot"></span>
        </div>
      </div>
    `;

    chatMessages.appendChild(row);
    return row;
  }

  // 10. Lightweight Markdown Parser
  function parseMarkdown(md) {
    if (!md) return "";
    let html = escapeHtml(md);

    // Code blocks ```...```
    html = html.replace(/```([\s\S]*?)```/g, (match, code) => {
      return `<pre><code>${code.trim()}</code></pre>`;
    });

    // Inline code `...`
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

    // Bold **...**
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');

    // Italic *...*
    html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');

    // Bullet lists: lines starting with * or -
    const lines = html.split('\n');
    let inList = false;
    let result = [];

    for (let line of lines) {
      const trimmed = line.trim();
      if (trimmed.startsWith('* ') || trimmed.startsWith('- ') || trimmed.startsWith('&bull; ')) {
        if (!inList) {
          result.push('<ul>');
          inList = true;
        }
        const itemContent = trimmed.replace(/^[\*\-&bull;]\s+/, '');
        result.push(`<li>${itemContent}</li>`);
      } else {
        if (inList) {
          result.push('</ul>');
          inList = false;
        }
        if (trimmed.length > 0) {
          result.push(`<p>${line}</p>`);
        }
      }
    }
    if (inList) {
      result.push('</ul>');
    }

    return result.join('');
  }

  // 11. Escape HTML Helper
  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }

  // Check initial server connection
  checkServerStatus();
});
