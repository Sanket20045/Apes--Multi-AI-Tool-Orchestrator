/**
 * Apes AI Agent — Anime.js UI Engine
 * ====================================
 * Powers interactive kinetic animations, staggered wave grid matrix,
 * execution timeline scrubber, and spring-physics message rendering.
 */

document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements
  const gridContainer = document.getElementById("anime-grid-matrix");
  const chatMessages = document.getElementById("chat-messages");
  const chatForm = document.getElementById("chat-form");
  const userInput = document.getElementById("user-input");
  const sendBtn = document.getElementById("send-btn");
  const clearChatBtn = document.getElementById("clear-chat-btn");
  const toggleTimelineBtn = document.getElementById("toggle-timeline-btn");
  const timelineBar = document.getElementById("execution-timeline");
  const connectionBadge = document.getElementById("connection-badge");
  const connectionText = document.getElementById("connection-text");
  const welcomeCard = document.getElementById("welcome-card");
  const brandLogo = document.getElementById("brand-logo");

  // Timeline telemetry elements
  const timelineProgress = document.getElementById("timeline-progress");
  const timelineCursor = document.getElementById("timeline-cursor");
  const timelineStepBadge = document.getElementById("timeline-step-badge");
  const latencyCounter = document.getElementById("latency-counter");
  const telemetryModel = document.getElementById("telemetry-model");
  const milestoneNodes = document.querySelectorAll(".milestone-node");
  const toolboxCards = document.querySelectorAll(".toolbox-card");

  let isGenerating = false;
  let timerInterval = null;
  let startTime = 0;
  let gridCols = 0;
  let gridRows = 0;

  // Tool visual configurations
  const TOOL_META = {
    calculator: {
      name: "Calculator",
      icon: "🧮",
      color: "var(--anime-orange)",
      tagClass: "tool-badge-calculator"
    },
    weather_lookup: {
      name: "Weather",
      icon: "🌦️",
      color: "var(--anime-sky)",
      tagClass: "tool-badge-weather_lookup"
    },
    text_utility: {
      name: "Text Utility",
      icon: "📝",
      color: "var(--anime-turquoise)",
      tagClass: "tool-badge-text_utility"
    },
    currency_converter: {
      name: "Currency",
      icon: "💱",
      color: "var(--anime-lavender)",
      tagClass: "tool-badge-currency_converter"
    }
  };

  /* ==========================================================================
     1. Interactive Staggered Matrix Grid (Anime.js signature background)
     ========================================================================== */
  function initStaggerGrid() {
    if (!gridContainer) return;
    gridContainer.innerHTML = "";

    const dotSpacing = 42; // px
    gridCols = Math.floor(window.innerWidth / dotSpacing);
    gridRows = Math.floor(window.innerHeight / dotSpacing);
    const totalDots = gridCols * gridRows;

    gridContainer.style.gridTemplateColumns = `repeat(${gridCols}, 1fr)`;
    gridContainer.style.gridTemplateRows = `repeat(${gridRows}, 1fr)`;

    const fragment = document.createDocumentFragment();
    for (let i = 0; i < totalDots; i++) {
      const dot = document.createElement("div");
      dot.className = "grid-dot";
      dot.dataset.index = i;
      fragment.appendChild(dot);
    }
    gridContainer.appendChild(fragment);

    // Initial ambient ripple stagger on load
    if (typeof anime !== "undefined") {
      anime({
        targets: ".grid-dot",
        scale: [
          { value: 1.8, easing: "easeOutSine", duration: 500 },
          { value: 1, easing: "easeInOutQuad", duration: 800 }
        ],
        opacity: [
          { value: 0.6, easing: "easeOutSine", duration: 500 },
          { value: 0.12, easing: "easeInOutQuad", duration: 800 }
        ],
        delay: anime.stagger(15, {
          grid: [gridCols, gridRows],
          from: "center"
        })
      });
    }
  }

  // Trigger ripple from point
  function triggerGridRipple(originIndex) {
    if (typeof anime === "undefined" || !gridContainer) return;

    anime.remove(".grid-dot");
    anime({
      targets: ".grid-dot",
      scale: [
        { value: 2.4, easing: "easeOutSine", duration: 320 },
        { value: 1, easing: "easeInOutQuad", duration: 700 }
      ],
      opacity: [
        { value: 0.85, easing: "easeOutSine", duration: 320 },
        { value: 0.12, easing: "easeInOutQuad", duration: 700 }
      ],
      delay: anime.stagger(18, {
        grid: [gridCols, gridRows],
        from: originIndex !== undefined ? originIndex : "center"
      })
    });
  }

  // Pointer move interaction with throttled ripple
  let lastMove = 0;
  window.addEventListener("pointermove", (e) => {
    const now = Date.now();
    if (now - lastMove < 120) return;
    lastMove = now;

    const dotSpacing = 42;
    const col = Math.floor(e.clientX / dotSpacing);
    const row = Math.floor(e.clientY / dotSpacing);
    const index = row * gridCols + col;

    if (index >= 0 && index < gridCols * gridRows && typeof anime !== "undefined") {
      anime({
        targets: `.grid-dot[data-index="${index}"]`,
        scale: 2.2,
        opacity: 0.9,
        backgroundColor: "#05dbe9",
        duration: 200,
        easing: "easeOutQuad",
        complete: (anim) => {
          anime({
            targets: anim.animatables[0].target,
            scale: 1,
            opacity: 0.12,
            backgroundColor: "rgba(255, 255, 255, 0.12)",
            duration: 600,
            easing: "easeInOutQuad"
          });
        }
      });
    }
  });

  // Re-init grid on window resize
  let resizeTimer;
  window.addEventListener("resize", () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(initStaggerGrid, 250);
  });

  initStaggerGrid();

  /* ==========================================================================
     2. Brand Logo Kinetic Letter Animation
     ========================================================================== */
  function animateBrandEntrance() {
    if (typeof anime === "undefined") return;

    anime({
      targets: ".brand-title .letter",
      translateY: [-24, 0],
      opacity: [0, 1],
      easing: "easeOutElastic(1, .75)",
      delay: anime.stagger(70, { start: 100 }),
      duration: 800
    });

    anime({
      targets: ".brand-mark",
      scale: [0, 1],
      rotate: [-45, 0],
      easing: "easeOutBack",
      duration: 600
    });
  }

  brandLogo.addEventListener("click", () => {
    if (typeof anime === "undefined") return;
    anime({
      targets: ".brand-title .letter",
      translateY: [
        { value: -10, duration: 180, easing: "easeOutSine" },
        { value: 0, duration: 400, easing: "easeOutBounce" }
      ],
      color: [
        { value: "#05dbe9", duration: 180 },
        { value: "#f6f4f2", duration: 400 }
      ],
      delay: anime.stagger(50)
    });
    triggerGridRipple("center");
  });

  animateBrandEntrance();

  /* ==========================================================================
     3. Backend Health & Server Status Check
     ========================================================================== */
  async function checkServerStatus() {
    try {
      const res = await fetch("/api/status");
      if (!res.ok) throw new Error("Offline");
      const data = await res.json();

      connectionBadge.className = "anime-status-badge";
      if (data.gemini_connected) {
        connectionText.textContent = `${data.model || "Gemini"} Live`;
        telemetryModel.textContent = (data.model || "GEMINI-3.6").toUpperCase();
      } else {
        connectionBadge.classList.add("status-loading");
        connectionText.textContent = "Local Fallback";
        telemetryModel.textContent = "LOCAL FALLBACK";
      }
    } catch (err) {
      connectionBadge.className = "anime-status-badge status-offline";
      connectionText.textContent = "Engine Offline";
      telemetryModel.textContent = "DISCONNECTED";
    }
  }

  checkServerStatus();

  /* ==========================================================================
     4. Execution Timeline Scrubber Controls
     ========================================================================== */
  toggleTimelineBtn.addEventListener("click", () => {
    timelineBar.classList.toggle("collapsed");
    toggleTimelineBtn.classList.toggle("active");
  });

  function setTimelineStage(stagePercent, stageName, activeMilestoneIdx) {
    if (timelineProgress && timelineCursor) {
      timelineProgress.style.width = `${stagePercent}%`;
      timelineCursor.style.left = `${stagePercent}%`;
    }
    if (timelineStepBadge) {
      timelineStepBadge.textContent = stageName.toUpperCase();
      timelineStepBadge.classList.add("active");
    }

    milestoneNodes.forEach((node, idx) => {
      node.classList.remove("active", "completed");
      if (idx < activeMilestoneIdx) {
        node.classList.add("completed");
      } else if (idx === activeMilestoneIdx) {
        node.classList.add("active");
      }
    });
  }

  function startExecutionTimer() {
    startTime = performance.now();
    if (timerInterval) clearInterval(timerInterval);
    timerInterval = setInterval(() => {
      const elapsed = Math.round(performance.now() - startTime);
      latencyCounter.textContent = `${elapsed}ms`;
    }, 40);
  }

  function stopExecutionTimer() {
    if (timerInterval) {
      clearInterval(timerInterval);
      timerInterval = null;
    }
    const finalElapsed = Math.round(performance.now() - startTime);
    latencyCounter.textContent = `${finalElapsed}ms`;
  }

  function highlightToolModules(toolsUsed) {
    // Reset all tool highlights
    toolboxCards.forEach((card) => card.classList.remove("active-tool"));

    if (!toolsUsed || toolsUsed.length === 0) return;

    toolsUsed.forEach((tool) => {
      const card = document.querySelector(`.toolbox-card[data-tool="${tool.name}"]`);
      if (card) {
        card.classList.add("active-tool");
        if (typeof anime !== "undefined") {
          anime({
            targets: card,
            scale: [1, 1.05, 1],
            easing: "easeOutElastic(1, .6)",
            duration: 600
          });
        }
      }
    });
  }

  /* ==========================================================================
     5. Auto-expand Textarea & Key Handlers
     ========================================================================== */
  userInput.addEventListener("input", () => {
    userInput.style.height = "auto";
    userInput.style.height = Math.min(userInput.scrollHeight, 140) + "px";
  });

  userInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      chatForm.dispatchEvent(new Event("submit", { cancelable: true }));
    }
  });

  // Toolbox cards click micro-interaction
  toolboxCards.forEach((card) => {
    card.addEventListener("click", () => {
      const toolKey = card.dataset.tool;
      if (typeof anime !== "undefined") {
        anime({
          targets: card,
          scale: [1, 0.95, 1.03, 1],
          duration: 350,
          easing: "easeOutQuad"
        });
      }
      triggerGridRipple();
    });
  });

  // Clear Session
  clearChatBtn.addEventListener("click", () => {
    if (typeof anime !== "undefined") {
      anime({
        targets: ".message-entry",
        opacity: [1, 0],
        translateY: [0, -16],
        delay: anime.stagger(50),
        duration: 300,
        easing: "easeInQuad",
        complete: () => {
          chatMessages.innerHTML = "";
          if (welcomeCard) chatMessages.appendChild(welcomeCard);
        }
      });
    } else {
      chatMessages.innerHTML = "";
      if (welcomeCard) chatMessages.appendChild(welcomeCard);
    }
    toolboxCards.forEach((c) => c.classList.remove("active-tool"));
    setTimelineStage(0, "IDLE", 0);
    latencyCounter.textContent = "0ms";
  });

  /* ==========================================================================
     6. Form Submission & Agent Query Flow
     ========================================================================== */
  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const query = userInput.value.trim();

    if (!query || isGenerating) return;

    // Dismiss welcome card on first message with anime.js
    if (welcomeCard && welcomeCard.parentElement === chatMessages) {
      if (typeof anime !== "undefined") {
        anime({
          targets: welcomeCard,
          opacity: 0,
          scale: 0.95,
          duration: 250,
          easing: "easeInQuad",
          complete: () => welcomeCard.remove()
        });
      } else {
        welcomeCard.remove();
      }
    }

    // Append User Message
    appendUserMessage(query);

    // Reset input
    userInput.value = "";
    userInput.style.height = "auto";
    setGeneratingState(true);

    // Start Timeline Execution Scrubber
    startExecutionTimer();
    setTimelineStage(25, "ROUTING", 1);
    triggerGridRipple();

    // Show Animated Typing Indicator
    const typingRow = appendTypingIndicator();
    scrollToBottom();

    try {
      // Small visual delay for timeline transition to show routing
      setTimeout(() => {
        if (isGenerating) setTimelineStage(50, "TOOL DISPATCH", 2);
      }, 250);

      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: query })
      });

      typingRow.remove();

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.error || "Server returned an error");
      }

      const data = await response.json();

      // Highlight used tools in toolbox shelf & advance timeline
      if (data.tools_used && data.tools_used.length > 0) {
        highlightToolModules(data.tools_used);
        setTimelineStage(80, "TOOL EXECUTED", 2);
      } else {
        setTimelineStage(80, "DIRECT SYNTHESIS", 2);
      }

      // Finish timeline
      setTimelineStage(100, "COMPLETED", 3);
      stopExecutionTimer();

      // Render agent response with Anime.js spring physics
      appendAgentMessage(data.response || "No response received.", data.tools_used || []);

    } catch (error) {
      if (typingRow) typingRow.remove();
      stopExecutionTimer();
      setTimelineStage(100, "ERROR", 3);
      if (timelineStepBadge) timelineStepBadge.textContent = "ERROR";
      appendAgentMessage(`⚠️ **Engine Error:** ${error.message || "Could not reach agent orchestrator."}`, []);
    } finally {
      setGeneratingState(false);
      scrollToBottom();
      userInput.focus();

      // Reset timeline step tag back to standby after 3s
      setTimeout(() => {
        if (!isGenerating && timelineStepBadge) {
          timelineStepBadge.textContent = "READY";
          timelineStepBadge.classList.remove("active");
        }
      }, 3000);
    }
  });

  function setGeneratingState(generating) {
    isGenerating = generating;
    sendBtn.disabled = generating;
    if (generating) {
      sendBtn.querySelector(".btn-text").textContent = "WAIT";
    } else {
      sendBtn.querySelector(".btn-text").textContent = "RUN";
    }
  }

  function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  /* ==========================================================================
     7. Render User & Agent Messages with Spring Animation
     ========================================================================== */
  function appendUserMessage(text) {
    const entry = document.createElement("div");
    entry.className = "message-entry user-entry";

    entry.innerHTML = `
      <div class="avatar-badge user-avatar">
        <span>YOU</span>
      </div>
      <div class="message-content-wrapper">
        <div class="user-bubble">${escapeHtml(text)}</div>
      </div>
    `;

    chatMessages.appendChild(entry);

    // Anime.js entrance spring
    if (typeof anime !== "undefined") {
      anime({
        targets: entry,
        translateY: [20, 0],
        opacity: [0, 1],
        scale: [0.96, 1],
        easing: "easeOutBack",
        duration: 400
      });
    } else {
      entry.style.opacity = "1";
      entry.style.transform = "none";
    }
    scrollToBottom();
  }

  function appendAgentMessage(markdownText, toolsUsed) {
    const entry = document.createElement("div");
    entry.className = "message-entry agent-entry";

    let toolsHtml = "";
    if (toolsUsed && toolsUsed.length > 0) {
      toolsHtml = `
        <div class="tool-used-ribbon">
          ${toolsUsed.map((t) => {
            const meta = TOOL_META[t.name] || { name: t.name, icon: "⚡", tagClass: "tool-badge-calculator" };
            return `
              <span class="tool-badge-pill ${meta.tagClass}">
                <span>${meta.icon}</span>
                <span>Module: <strong>${meta.name}</strong></span>
              </span>
            `;
          }).join("")}
        </div>
      `;
    }

    const formattedContent = parseMarkdown(markdownText);

    entry.innerHTML = `
      <div class="avatar-badge agent-avatar">
        <span>✦</span>
      </div>
      <div class="message-content-wrapper">
        ${toolsHtml}
        <div class="agent-bubble">
          ${formattedContent}
        </div>
      </div>
    `;

    chatMessages.appendChild(entry);

    // Anime.js entrance with elastic spring
    if (typeof anime !== "undefined") {
      anime({
        targets: entry,
        translateY: [28, 0],
        opacity: [0, 1],
        scale: [0.97, 1],
        easing: "easeOutElastic(1, .75)",
        duration: 750
      });

      // Animate tool tags stagger if present
      if (entry.querySelectorAll(".tool-badge-pill").length > 0) {
        anime({
          targets: entry.querySelectorAll(".tool-badge-pill"),
          scale: [0.85, 1],
          opacity: [0, 1],
          delay: anime.stagger(100, { start: 150 }),
          easing: "easeOutBack"
        });
      }
    } else {
      entry.style.opacity = "1";
      entry.style.transform = "none";
    }
    scrollToBottom();
  }

  /* ==========================================================================
     8. Kinetic Wave Typing Indicator
     ========================================================================== */
  function appendTypingIndicator() {
    const entry = document.createElement("div");
    entry.className = "message-entry agent-entry typing-entry";

    entry.innerHTML = `
      <div class="avatar-badge agent-avatar">
        <span>✦</span>
      </div>
      <div class="message-content-wrapper">
        <div class="typing-box">
          <span class="wave-dot"></span>
          <span class="wave-dot"></span>
          <span class="wave-dot"></span>
        </div>
      </div>
    `;

    chatMessages.appendChild(entry);

    if (typeof anime !== "undefined") {
      anime({
        targets: entry,
        opacity: [0, 1],
        translateY: [12, 0],
        duration: 300,
        easing: "easeOutQuad"
      });

      anime({
        targets: entry.querySelectorAll(".wave-dot"),
        translateY: [-7, 0],
        opacity: [0.3, 1],
        direction: "alternate",
        loop: true,
        delay: anime.stagger(140),
        easing: "easeInOutSine"
      });
    }

    return entry;
  }

  /* ==========================================================================
     9. Markdown Formatter & HTML Helper
     ========================================================================== */
  function parseMarkdown(md) {
    if (!md) return "";
    let html = escapeHtml(md);

    // Code blocks ```...```
    html = html.replace(/```([\s\S]*?)```/g, (match, code) => {
      return `<pre><code>${code.trim()}</code></pre>`;
    });

    // Inline code `...`
    html = html.replace(/`([^`]+)`/g, "<code>$1</code>");

    // Bold **...**
    html = html.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");

    // Italic *...*
    html = html.replace(/\*([^*]+)\*/g, "<em>$1</em>");

    // Bullet points
    const lines = html.split("\n");
    let inList = false;
    let result = [];

    for (let line of lines) {
      const trimmed = line.trim();
      if (trimmed.startsWith("* ") || trimmed.startsWith("- ") || trimmed.startsWith("&bull; ")) {
        if (!inList) {
          result.push("<ul>");
          inList = true;
        }
        const item = trimmed.replace(/^[\*\-&bull;]\s+/, "");
        result.push(`<li>${item}</li>`);
      } else {
        if (inList) {
          result.push("</ul>");
          inList = false;
        }
        if (trimmed.length > 0) {
          result.push(`<p>${line}</p>`);
        }
      }
    }
    if (inList) result.push("</ul>");

    return result.join("");
  }

  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }
});
