// ── State ────────────────────────────────────────────────────────────────────
const MAX_TOKENS = 32000;
let messages   = [];   // [{role:"user"|"assistant", content:"..."}]
let totalTokens = 0;
let isLoading   = false;

// ── DOM refs ─────────────────────────────────────────────────────────────────
const chatArea    = document.getElementById('chatArea');
const msgInput    = document.getElementById('msgInput');
const emptyState  = document.getElementById('emptyState');
const historyList = document.getElementById('historyList');
const tokFill     = document.getElementById('tokFill');
const tokVal      = document.getElementById('tokVal');
const sendBtn     = document.getElementById('sendBtn');
const regenBtn    = document.getElementById('regenBtn');
const sidebar     = document.getElementById('sidebar');
const overlay     = document.getElementById('sidebarOverlay');

// ── Sidebar toggle ────────────────────────────────────────────────────────────
document.getElementById('menuBtn').addEventListener('click', () => {
  sidebar.classList.toggle('open');
  overlay.classList.toggle('open');
});
document.getElementById('closeBtn').addEventListener('click', () => {
  sidebar.classList.remove('open');
  overlay.classList.remove('open');
});
overlay.addEventListener('click', () => {
  sidebar.classList.remove('open');
  overlay.classList.remove('open');
});

// ── New chat ─────────────────────────────────────────────────────────────────
document.getElementById('newChatBtn').addEventListener('click', clearChat);

// ── Auto-resize textarea ─────────────────────────────────────────────────────
msgInput.addEventListener('input', () => {
  msgInput.style.height = 'auto';
  msgInput.style.height = Math.min(msgInput.scrollHeight, 180) + 'px';
});

// ── Send on Enter (Shift+Enter = newline) ─────────────────────────────────────
msgInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

// ── Suggestion buttons ────────────────────────────────────────────────────────
function fillSuggestion(btn) {
  const text = btn.querySelector('.sug-i').nextSibling.textContent.trim();
  msgInput.value = text;
  msgInput.focus();
  msgInput.dispatchEvent(new Event('input'));
}

// ── Token bar update ──────────────────────────────────────────────────────────
function updateTokenBar() {
  const pct = Math.min(100, (totalTokens / MAX_TOKENS) * 100);
  tokFill.style.width = pct + '%';
  tokFill.style.background = pct < 70
    ? 'linear-gradient(90deg,#1a73e8,#8b5cf6)'
    : pct < 90
      ? 'linear-gradient(90deg,#f59e0b,#ef4444)'
      : '#ef4444';
  tokVal.textContent = `${totalTokens.toLocaleString()} / ${MAX_TOKENS.toLocaleString()}`;
  tokVal.style.color = pct > 80 ? '#ef4444' : '#6b7280';
}

// ── Render a message bubble ───────────────────────────────────────────────────
function renderMessage(role, content, tokCount = null) {
  const isUser = role === 'user';
  const wrap = document.createElement('div');
  wrap.className = `msg-wrap ${isUser ? 'user' : ''}`;

  // User messages: escape HTML (plain text)
  // Bot messages: render Markdown → HTML
  const bodyHtml = isUser
    ? escapeHtml(content)
    : marked.parse(content, { breaks: true, gfm: true });

  const tokInfo = tokCount !== null
    ? `<span class="tok-badge">🪙 ${tokCount} tokens</span>`
    : '';

  const chips = !isUser
    ? `<div class="chips">
        <div class="chip" onclick="copyText(this)">📋 Copy</div>
       </div>`
    : '';

  wrap.innerHTML = `
    <div class="ava ${isUser ? 'user' : 'bot'}">${isUser ? '👤' : '✦'}</div>
    <div class="bubble-col">
      <div class="bubble ${isUser ? 'user' : 'bot'}">${bodyHtml}</div>
      <div class="msg-meta">
        ${isUser ? 'You' : 'AI Chat Bot'}&nbsp;${tokInfo}
      </div>
      ${chips}
    </div>`;

  chatArea.appendChild(wrap);
  scrollBottom();
  return wrap;
}

// ── Typing indicator ──────────────────────────────────────────────────────────
function showTyping() {
  const wrap = document.createElement('div');
  wrap.className = 'msg-wrap';
  wrap.id = 'typingWrap';
  wrap.innerHTML = `
    <div class="ava bot">✦</div>
    <div class="bubble-col">
      <div class="bubble bot">
        <div class="typing-dots"><span></span><span></span><span></span></div>
      </div>
    </div>`;
  chatArea.appendChild(wrap);
  scrollBottom();
}
function hideTyping() {
  document.getElementById('typingWrap')?.remove();
}

// ── Scroll to bottom ──────────────────────────────────────────────────────────
function scrollBottom() {
  chatArea.scrollTop = chatArea.scrollHeight;
}

// ── Escape HTML ───────────────────────────────────────────────────────────────
function escapeHtml(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/\n/g, '<br>');
}

// ── Copy text chip ────────────────────────────────────────────────────────────
function copyText(el) {
  const bubble = el.closest('.bubble-col').querySelector('.bubble');
  navigator.clipboard.writeText(bubble.innerText).then(() => {
    el.textContent = '✅ Copied';
    setTimeout(() => el.textContent = '📋 Copy', 2000);
  });
}

// ── History sidebar ───────────────────────────────────────────────────────────
function addToHistory(text) {
  const empty = historyList.querySelector('.history-empty');
  if (empty) empty.remove();

  const item = document.createElement('div');
  item.className = 'history-item';
  item.innerHTML = `<span class="hi-icon">💬</span>${text.slice(0, 50)}${text.length > 50 ? '…' : ''}`;
  historyList.prepend(item);
}

// ── Send message ──────────────────────────────────────────────────────────────
async function sendMessage() {
  const text = msgInput.value.trim();
  if (!text || isLoading) return;

  // Clear input
  msgInput.value = '';
  msgInput.style.height = 'auto';

  // Hide empty state
  if (emptyState) emptyState.style.display = 'none';

  // Add to messages array & render
  messages.push({ role: 'user', content: text });
  renderMessage('user', text);
  addToHistory(text);

  // Show loading
  isLoading = true;
  sendBtn.disabled = true;
  sendBtn.textContent = '…';
  showTyping();

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages }),
    });

    if (!res.ok) throw new Error(`Server error ${res.status}`);
    const data = await res.json();

    // Update state
    messages.push({ role: 'assistant', content: data.reply });
    totalTokens = data.total_tokens || totalTokens;
    updateTokenBar();

    hideTyping();
    renderMessage('assistant', data.reply, data.output_tokens);
  } catch (err) {
    hideTyping();
    renderMessage('assistant', `⚠️ Error: ${err.message}`);
  } finally {
    isLoading = false;
    sendBtn.disabled = false;
    sendBtn.textContent = 'Send ↑';
    msgInput.focus();
  }
}

// ── Regenerate ────────────────────────────────────────────────────────────────
async function regenerate() {
  if (isLoading || messages.length === 0) return;

  // Remove last assistant message from array and DOM
  if (messages[messages.length - 1]?.role === 'assistant') {
    messages.pop();
    const bubbles = chatArea.querySelectorAll('.msg-wrap:not(.user)');
    bubbles[bubbles.length - 1]?.remove();
  }

  // Re-submit
  isLoading = true;
  regenBtn.disabled = true;
  showTyping();

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages }),
    });
    if (!res.ok) throw new Error(`Server error ${res.status}`);
    const data = await res.json();
    messages.push({ role: 'assistant', content: data.reply });
    totalTokens = data.total_tokens || totalTokens;
    updateTokenBar();
    hideTyping();
    renderMessage('assistant', data.reply, data.output_tokens);
  } catch (err) {
    hideTyping();
    renderMessage('assistant', `⚠️ Error: ${err.message}`);
  } finally {
    isLoading = false;
    regenBtn.disabled = false;
  }
}

// ── Clear chat ────────────────────────────────────────────────────────────────
function clearChat() {
  messages = [];
  totalTokens = 0;
  updateTokenBar();

  // Remove all message bubbles
  chatArea.querySelectorAll('.msg-wrap').forEach(el => el.remove());

  // Show empty state again
  if (emptyState) emptyState.style.display = '';

  // Clear history sidebar
  historyList.innerHTML = '<div class="history-empty">No conversations yet.</div>';

  msgInput.focus();
}

// ── Init ──────────────────────────────────────────────────────────────────────
updateTokenBar();
msgInput.focus();
