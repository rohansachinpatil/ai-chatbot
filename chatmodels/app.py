import streamlit as st
from model_loader import get_mistral_model
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
import time

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Chat Bot",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS — iOS Glassmorphism Dark ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

/* ────────────────── Variables — Gemini Light ────────────────── */
:root {
  --bg:             #f0f4f9;
  --surface:        #ffffff;
  --surface2:       #f8f9fa;
  --border:         #e3e6ea;
  --accent:         #1a73e8;
  --accent2:        #8b5cf6;
  --accent3:        #f59e0b;
  --danger:         #ef4444;
  --text:           #1f2937;
  --muted:          #6b7280;
  --radius:         18px;
  --radius-sm:      12px;
  --shadow:         0 4px 24px rgba(0,0,0,0.08);
  --shadow-sm:      0 1px 8px rgba(0,0,0,0.06);
  --blur:           blur(16px);
}

/* ────────────────── Base ────────────────── */
*, *::before, *::after { box-sizing: border-box; }
html, body { height: 100%; }
body { font-family: 'Outfit', sans-serif; }

[data-testid="stAppViewContainer"] {
  background:
    radial-gradient(ellipse 70% 50% at 10% 0%,   rgba(26,115,232,0.07)  0%, transparent 60%),
    radial-gradient(ellipse 60% 45% at 90% 90%,   rgba(139,92,246,0.06)  0%, transparent 60%),
    linear-gradient(160deg, #eef2fb 0%, #f0f4f9 60%, #f3f0fb 100%) !important;
  min-height: 100vh;
}

/* Hide chrome */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"] { display: none !important; }

/* ────────────────── Sidebar ────────────────── */
[data-testid="stSidebar"] {
  background: #ffffff !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 26px 16px 20px !important; }
[data-testid="stSidebar"] * { color: var(--text) !important; }

.sb-logo-row {
  display: flex; align-items: center; gap: 12px; margin-bottom: 24px;
}
.sb-icon {
  width: 44px; height: 44px; border-radius: 14px; flex-shrink: 0;
  background: linear-gradient(135deg, rgba(26,115,232,0.15), rgba(139,92,246,0.12));
  border: 1px solid rgba(26,115,232,0.20);
  display: flex; align-items: center; justify-content: center;
  font-size: 22px;
  box-shadow: 0 4px 18px rgba(48,209,88,0.20);
}
.sb-title  { font-size: 22px; font-weight: 700; letter-spacing: -0.3px; color: var(--text); }
.sb-sub    { font-size: 11px; color: var(--muted); margin-top: 1px; }

.sb-section {
  font-size: 10px; font-weight: 600; letter-spacing: 1.3px;
  color: var(--muted); text-transform: uppercase; margin: 20px 0 10px;
}

/* Stats row */
.stats-row { display: flex; gap: 7px; flex-wrap: wrap; margin-bottom: 16px; }
.stat-chip {
  background: #f1f5f9;
  border: 1px solid var(--border);
  border-radius: 999px; padding: 5px 11px;
  font-size: 11px; color: var(--muted);
  display: flex; align-items: center; gap: 5px;
}
.stat-chip b { color: var(--text); font-weight: 600; }

/* Context bar */
.ctx-wrap { margin: 8px 0 18px; }
.ctx-lbl  { font-size: 11px; color: var(--muted); margin-bottom: 5px; display: flex; justify-content: space-between; }
.ctx-track { height: 5px; background: #e5e7eb; border-radius: 999px; overflow: hidden; }
.ctx-fill  { height: 100%; border-radius: 999px; transition: width 0.4s ease; }

/* History cards */
.hist-card {
  display: flex; align-items: flex-start; gap: 9px;
  background: #f8fafc; border: 1px solid var(--border);
  border-radius: var(--radius-sm); padding: 11px 13px;
  margin-bottom: 7px; font-size: 12.5px; color: var(--text);
  transition: all 0.2s ease; cursor: pointer; line-height: 1.4;
}
.hist-card:hover {
  background: #eff6ff;
  border-color: rgba(26,115,232,0.35);
  transform: translateX(3px);
}

/* Model info table */
.model-table {
  background: #f8fafc; border: 1px solid var(--border);
  border-radius: var(--radius-sm); padding: 12px 14px;
}
.model-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 4px 0; border-bottom: 1px solid #f1f5f9;
}
.model-row:last-child { border-bottom: none; }
.model-key  { font-size: 11px; color: var(--muted); }
.model-val  { font-size: 11px; font-weight: 600; }

/* ────────────────── Main content ────────────────── */
.main .block-container { padding: 0 !important; max-width: 100% !important; }

/* Top bar */
.top-bar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 13px 28px;
  background: rgba(255,255,255,0.85);
  backdrop-filter: var(--blur); -webkit-backdrop-filter: var(--blur);
  border-bottom: 1px solid var(--border);
  position: sticky; top: 0; z-index: 100;
}
.top-bar-left  { display: flex; align-items: center; gap: 10px; }
.top-bar-title { font-size: 16px; font-weight: 600; color: var(--text); letter-spacing: -0.2px; }
.top-bar-right { display: flex; align-items: center; gap: 10px; }

.badge-live {
  background: #dcfce7; border: 1px solid #86efac;
  color: #16a34a; font-size: 11px; font-weight: 600;
  padding: 4px 10px; border-radius: 999px;
  display: flex; align-items: center; gap: 5px;
}
.dot-live {
  width: 6px; height: 6px; background: #16a34a; border-radius: 50%;
  animation: blink 2s infinite;
}
@keyframes blink {
  0%,100% { opacity:1; transform:scale(1); }
  50%     { opacity:0.4; transform:scale(0.7); }
}
.model-tag {
  background: #f1f5f9; border: 1px solid var(--border);
  border-radius: 999px; padding: 4px 12px;
  font-size: 11px; color: var(--muted);
}

/* Token strip */
.tok-strip {
  display: flex; align-items: center; gap: 12px;
  padding: 8px 28px;
  background: #f8fafc;
  border-bottom: 1px solid var(--border);
}
.tok-lbl   { font-size: 11px; color: var(--muted); white-space: nowrap; }
.tok-track { flex: 1; height: 4px; background: #e5e7eb; border-radius: 999px; overflow: hidden; }
.tok-fill  { height: 100%; border-radius: 999px; transition: width 0.4s ease; }
.tok-val   { font-size: 11px; font-weight: 600; white-space: nowrap; }

/* ────────────────── Messages ────────────────── */
.msg-wrap {
  display: flex; gap: 13px; padding: 12px 28px;
  align-items: flex-start; animation: fadeUp 0.28s ease;
}
.msg-wrap.user { flex-direction: row-reverse; }
@keyframes fadeUp {
  from { opacity:0; transform:translateY(8px); }
  to   { opacity:1; transform:translateY(0); }
}
.ava {
  width: 36px; height: 36px; border-radius: 12px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center; font-size: 16px;
}
.ava.bot {
  background: linear-gradient(135deg, rgba(26,115,232,0.15), rgba(139,92,246,0.12));
  border: 1px solid rgba(26,115,232,0.20);
  box-shadow: 0 2px 8px rgba(26,115,232,0.10);
}
.ava.user {
  background: linear-gradient(135deg, rgba(139,92,246,0.15), rgba(26,115,232,0.10));
  border: 1px solid rgba(139,92,246,0.20);
}
.bubble-col { display: flex; flex-direction: column; gap: 5px; max-width: 70%; }
.msg-wrap.user .bubble-col { align-items: flex-end; }
.bubble {
  padding: 13px 16px; font-size: 14px; line-height: 1.65;
  color: var(--text);
}
.bubble.bot {
  background: #ffffff;
  border: 1px solid var(--border);
  border-radius: 4px 16px 16px 16px;
  box-shadow: var(--shadow-sm);
}
.bubble.user {
  background: linear-gradient(135deg, #eff6ff, #f5f3ff);
  border: 1px solid rgba(139,92,246,0.20);
  border-radius: 16px 4px 16px 16px;
  box-shadow: 0 1px 6px rgba(139,92,246,0.10);
}
.msg-meta {
  display: flex; align-items: center; gap: 7px;
  font-size: 10.5px; color: var(--muted); padding: 0 3px;
}
.tok-badge {
  background: #eff6ff; border: 1px solid #bfdbfe;
  border-radius: 999px; padding: 2px 8px;
  font-size: 10px; color: #3b82f6;
}
.chips { display: flex; gap: 5px; flex-wrap: wrap; }
.chip {
  background: #f8fafc; border: 1px solid var(--border);
  border-radius: 999px; padding: 3px 10px;
  font-size: 10px; color: var(--muted); cursor: pointer;
  transition: all 0.15s;
}
.chip:hover {
  background: #eff6ff; border-color: rgba(26,115,232,0.30);
  color: var(--accent);
}

/* ────────────────── Empty state ────────────────── */
.empty {
  text-align: center; padding: 72px 40px 40px;
  animation: fadeUp 0.4s ease;
}
.empty-icon  { font-size: 54px; margin-bottom: 16px; }
.empty-title {
  font-size: 28px; font-weight: 700; color: transparent;
  background: linear-gradient(135deg, #1a73e8, #8b5cf6);
  -webkit-background-clip: text; background-clip: text;
  letter-spacing: -0.5px; margin-bottom: 8px;
}
.empty-sub   { font-size: 14px; color: var(--muted); margin-bottom: 36px; }
.sug-grid    { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; max-width: 540px; margin: 0 auto; }
.sug {
  background: #ffffff; border: 1px solid var(--border);
  border-radius: var(--radius-sm); padding: 15px 16px;
  font-size: 13px; color: var(--muted); cursor: pointer; text-align: left;
  box-shadow: var(--shadow-sm); transition: all 0.2s;
}
.sug:hover { background: #eff6ff; border-color: rgba(26,115,232,0.30); color: var(--text); transform: translateY(-2px); box-shadow: var(--shadow); }
.sug-i { font-size: 20px; margin-bottom: 7px; display: block; }

/* ────────────────── Spacer for fixed input ────────────────── */
.bottom-spacer { height: 148px; }

/* ────────────────── FIXED INPUT BAR ────────────────── */
[data-testid="stBottom"] > div {
  background: rgba(255,255,255,0.95) !important;
  backdrop-filter: var(--blur) !important;
  -webkit-backdrop-filter: var(--blur) !important;
  border-top: 1px solid var(--border) !important;
  padding: 14px 28px 18px !important;
}

[data-testid="stBottom"] [data-testid="stTextArea"] textarea {
  background: #f8fafc !important;
  border: 1px solid var(--border) !important;
  border-radius: 16px !important;
  color: var(--text) !important;
  font-family: 'Outfit', sans-serif !important;
  font-size: 14px !important;
  resize: none !important;
  padding: 13px 16px !important;
  caret-color: var(--accent) !important;
  box-shadow: inset 0 1px 3px rgba(0,0,0,0.04) !important;
}
[data-testid="stBottom"] [data-testid="stTextArea"] textarea:focus {
  border-color: rgba(26,115,232,0.50) !important;
  box-shadow: 0 0 0 3px rgba(26,115,232,0.10) !important;
  outline: none !important;
  background: #fff !important;
}
[data-testid="stBottom"] [data-testid="stTextArea"] textarea::placeholder {
  color: #9ca3af !important;
}

/* Buttons inside fixed bar - legacy selectors kept for desktop */
[data-testid="stBottom"] .stButton > button {
  font-family: 'Outfit', sans-serif !important;
  font-weight: 600 !important;
  border-radius: 13px !important;
  font-size: 13px !important;
  height: 46px !important;
  transition: all 0.2s !important;
}
[data-testid="stBottom"] .btn-send button {
  background: linear-gradient(135deg, #1a73e8, #6d4de8) !important;
  color: #fff !important; border: none !important;
  box-shadow: 0 4px 14px rgba(26,115,232,0.30) !important;
}
[data-testid="stBottom"] .btn-regen button {
  background: #f1f5f9 !important;
  color: #6b7280 !important;
  border: 1px solid var(--border) !important;
}
[data-testid="stBottom"] .btn-clear button {
  background: #fff !important;
  color: var(--muted) !important;
  border: 1px solid var(--border) !important;
}
[data-testid="stBottom"] .btn-clear button:hover {
  background: #fef2f2 !important;
  border-color: #fca5a5 !important;
  color: #ef4444 !important;
}
[data-testid="stBottom"] .stButton > button:hover { transform: translateY(-2px) !important; }

/* Form border removal */
[data-testid="stBottom"] [data-testid="stForm"] { border: none !important; padding: 0 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 999px; }

/* ── Show sidebar toggle (hamburger) always ── */
[data-testid="collapsedControl"] {
  display: flex !important;
  visibility: visible !important;
  opacity: 1 !important;
  top: 12px !important;
  left: 8px !important;
  z-index: 9999 !important;
  background: #ffffff !important;
  border-radius: 10px !important;
  border: 1px solid var(--border) !important;
  width: 36px !important;
  height: 36px !important;
  align-items: center !important;
  justify-content: center !important;
  box-shadow: var(--shadow-sm) !important;
}
[data-testid="collapsedControl"]:hover {
  background: #eff6ff !important;
  border-color: rgba(26,115,232,0.35) !important;
}

/* ── Bottom input: keep buttons always in a horizontal row ── */
.input-btn-row [data-testid="stHorizontalBlock"] {
  gap: 8px !important;
}
.input-btn-row .stFormSubmitButton button {
  width: 100% !important;
  height: 42px !important;
  font-size: 13px !important;
  font-family: 'Outfit', sans-serif !important;
  font-weight: 600 !important;
  border-radius: 12px !important;
  transition: all 0.2s !important;
}
.input-btn-row .btn-send button {
  background: linear-gradient(135deg, #1a73e8, #6d4de8) !important;
  color: #fff !important; border: none !important;
  box-shadow: 0 4px 14px rgba(26,115,232,0.25) !important;
}
.input-btn-row .btn-regen button {
  background: #f1f5f9 !important;
  color: #6b7280 !important;
  border: 1px solid var(--border) !important;
}
.input-btn-row .btn-clear button {
  background: #fff !important;
  color: var(--muted) !important;
  border: 1px solid var(--border) !important;
}
.input-btn-row .btn-clear button:hover {
  background: #fef2f2 !important;
  border-color: #fca5a5 !important;
  color: #ef4444 !important;
}
.input-btn-row button:hover { transform: translateY(-1px) !important; }

@media (max-width: 768px) {
  .top-bar { padding: 10px 14px; gap: 8px; }
  .top-bar-title { font-size: 13px; }
  .badge-live, .model-tag { font-size: 10px; padding: 3px 8px; }
  .tok-strip { padding: 6px 14px; flex-wrap: wrap; gap: 6px; }
  .tok-lbl, .tok-val { font-size: 10px; }
  .empty { padding: 32px 16px 20px; }
  .empty-icon { font-size: 40px; }
  .empty-title { font-size: 20px; }
  .empty-sub { font-size: 13px; }
  .sug-grid { grid-template-columns: 1fr; gap: 8px; }
  .sug { padding: 12px 14px; font-size: 12px; }
  .msg-wrap { padding: 10px 14px; gap: 8px; }
  .bubble-col { max-width: 90%; }
  .bubble { padding: 10px 13px; font-size: 13.5px; }
  .ava { width: 30px; height: 30px; font-size: 14px; }
  .chips { display: none; }
  [data-testid="stBottom"] > div { padding: 10px 14px 14px !important; }
  .bottom-spacer { height: 190px; }
}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "messages"       not in st.session_state:
    st.session_state.messages       = [SystemMessage(content="You are a helpful assistant.")]
if "history_labels" not in st.session_state:
    st.session_state.history_labels = []
if "total_tokens"   not in st.session_state:
    st.session_state.total_tokens   = 0
if "msg_count"      not in st.session_state:
    st.session_state.msg_count      = 0
if "session_start"  not in st.session_state:
    st.session_state.session_start  = time.strftime("%H:%M")

# ── Model ─────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_model():
    return get_mistral_model()

model = get_model()
MAX_TOKENS = 4000

def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)

def get_response(msgs):
    response = model.invoke(msgs)
    content = response.content
    usage = response.response_metadata.get("token_usage", {})
    comp_tokens = usage.get("completion_tokens") or estimate_tokens(content)
    total_tokens = usage.get("total_tokens") or estimate_tokens(content) * 2
    return content, comp_tokens, total_tokens

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sb-logo-row">
      <div class="sb-icon">✦</div>
      <div>
        <div class="sb-title">AI Chat Bot</div>
        <div class="sb-sub">Powered by Mistral</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Stats chips
    used_pct = min(100, int(st.session_state.total_tokens / MAX_TOKENS * 100))
    fill_col = "#30d158" if used_pct < 70 else "#ff9f0a" if used_pct < 90 else "#ff453a"
    st.markdown(f"""
    <div class="stats-row">
      <div class="stat-chip">💬 <b>{st.session_state.msg_count}</b> msgs</div>
      <div class="stat-chip">🪙 <b>{st.session_state.total_tokens}</b> tok</div>
      <div class="stat-chip">🕐 <b>{st.session_state.session_start}</b></div>
    </div>
    <div class="ctx-wrap">
      <div class="ctx-lbl">
        <span>Context window</span>
        <span style="color:{fill_col};font-weight:600;">{used_pct}%</span>
      </div>
      <div class="ctx-track">
        <div class="ctx-fill" style="width:{used_pct}%;background:linear-gradient(90deg,{fill_col},{fill_col}88)"></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-section">History</div>', unsafe_allow_html=True)
    if st.session_state.history_labels:
        for lbl in reversed(st.session_state.history_labels[-8:]):
            st.markdown(f'<div class="hist-card"><span style="font-size:13px">✦</span>{lbl}</div>',
                        unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-size:12px;color:rgba(245,245,247,0.25);padding:4px 0;">No history yet.</div>',
                    unsafe_allow_html=True)

    st.markdown('<div class="sb-section" style="margin-top:22px;">Model Config</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="model-table">
      <div class="model-row">
        <span class="model-key">Model</span>
        <span class="model-val" style="color:#30d158">mistral-small-latest</span>
      </div>
      <div class="model-row">
        <span class="model-key">Temperature</span>
        <span class="model-val" style="color:#0a84ff">0.0</span>
      </div>
      <div class="model-row">
        <span class="model-key">Max tokens</span>
        <span class="model-val" style="color:#ff9f0a">150</span>
      </div>
      <div class="model-row">
        <span class="model-key">Context limit</span>
        <span class="model-val" style="color:#bf5af2">4 000</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── Top bar ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="top-bar">
  <div class="top-bar-left">
    <span style="font-size:20px">✦</span>
    <span class="top-bar-title">AI Chat Bot — Super Chat</span>
  </div>
  <div class="top-bar-right">
    <div class="badge-live"><div class="dot-live"></div>Live</div>
    <div class="model-tag">mistral-small-latest</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Token strip ───────────────────────────────────────────────────────────────
used_main = min(100, int(st.session_state.total_tokens / MAX_TOKENS * 100))
col_main  = "#30d158" if used_main < 70 else "#ff9f0a" if used_main < 90 else "#ff453a"
st.markdown(f"""
<div class="tok-strip">
  <span class="tok-lbl">🪙 Tokens used</span>
  <div class="tok-track">
    <div class="tok-fill" style="width:{used_main}%;background:linear-gradient(90deg,{col_main},{col_main}77)"></div>
  </div>
  <span class="tok-val" style="color:{col_main}">{st.session_state.total_tokens} / {MAX_TOKENS}</span>
</div>
""", unsafe_allow_html=True)

# ── Chat messages ─────────────────────────────────────────────────────────────
chat_msgs = [m for m in st.session_state.messages if not isinstance(m, SystemMessage)]

if not chat_msgs:
    st.markdown("""
    <div class="empty">
      <div class="empty-icon">✦</div>
      <div class="empty-title">Hello, I'm your AI Chat Bot.</div>
      <div class="empty-sub">Your intelligent assistant, ready to help with anything.</div>
      <div class="sug-grid">
        <div class="sug"><span class="sug-i">🧠</span>Explain quantum computing simply</div>
        <div class="sug"><span class="sug-i">✍️</span>Write a compelling story opener</div>
        <div class="sug"><span class="sug-i">💡</span>5 innovative startup ideas for 2025</div>
        <div class="sug"><span class="sug-i">🔬</span>How does CRISPR gene editing work?</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in chat_msgs:
        if isinstance(msg, AIMessage):
            tok = estimate_tokens(msg.content)
            st.markdown(f"""
            <div class="msg-wrap">
              <div class="ava bot">✦</div>
              <div class="bubble-col">
                <div class="bubble bot">{msg.content}</div>
                <div class="msg-meta">
                  AI Chat Bot &nbsp;
                  <span class="tok-badge">🪙 ~{tok} tokens</span>
                </div>
                <div class="chips">
                  <div class="chip">📋 Copy</div>
                  <div class="chip">👍 Good</div>
                  <div class="chip">👎 Bad</div>
                  <div class="chip">📄 Save</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)
        elif isinstance(msg, HumanMessage):
            tok = estimate_tokens(msg.content)
            st.markdown(f"""
            <div class="msg-wrap user">
              <div class="ava user">👤</div>
              <div class="bubble-col">
                <div class="bubble user">{msg.content}</div>
                <div class="msg-meta">
                  You &nbsp;
                  <span class="tok-badge">🪙 ~{tok} tokens</span>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

# Auto-scroll to bottom after every render
st.markdown("""
<script>
(function() {
  function scrollToBottom() {
    const chatArea = window.parent.document.querySelector('[data-testid="stAppViewContainer"]');
    if (chatArea) chatArea.scrollTop = chatArea.scrollHeight;
    const main = window.parent.document.querySelector('section.main');
    if (main) main.scrollTop = main.scrollHeight;
    window.parent.scrollTo(0, window.parent.document.body.scrollHeight);
  }
  setTimeout(scrollToBottom, 150);
  setTimeout(scrollToBottom, 400);
})();
</script>
""", unsafe_allow_html=True)

# Spacer so chat isn't hidden behind fixed input
st.markdown('<div class="bottom-spacer"></div>', unsafe_allow_html=True)

# ── Fixed bottom input ────────────────────────────────────────────────────────
with st.bottom:
    with st.form(key="chat_form", clear_on_submit=True, border=False):
        # Row 1: full-width textarea
        user_input = st.text_area(
            label="",
            placeholder="Message AI Chat Bot…",
            height=56,
            key="user_msg",
            label_visibility="collapsed",
        )
        # Row 2: 3 buttons always in one row (equal width)
        st.markdown('<div class="input-btn-row">', unsafe_allow_html=True)
        col_s, col_r, col_c = st.columns([1, 1, 1])
        with col_s:
            st.markdown('<div class="btn-send">', unsafe_allow_html=True)
            send = st.form_submit_button("Send ↑", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with col_r:
            st.markdown('<div class="btn-regen">', unsafe_allow_html=True)
            regen = st.form_submit_button("↻ Redo", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with col_c:
            st.markdown('<div class="btn-clear">', unsafe_allow_html=True)
            clear = st.form_submit_button("🗑 Clear", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ── Actions ───────────────────────────────────────────────────────────────────
if clear:
    st.session_state.messages       = [SystemMessage(content="You are a helpful assistant.")]
    st.session_state.history_labels = []
    st.session_state.total_tokens   = 0
    st.session_state.msg_count      = 0
    st.rerun()

if regen:
    ai_idxs = [i for i, m in enumerate(st.session_state.messages) if isinstance(m, AIMessage)]
    if ai_idxs:
        st.session_state.messages.pop(ai_idxs[-1])
        with st.spinner(""):
            content, comp_tok, total_tok = get_response(st.session_state.messages)
            st.session_state.messages.append(AIMessage(content=content))
            st.session_state.total_tokens = total_tok
        st.rerun()

if send and user_input and user_input.strip():
    prompt = user_input.strip()
    st.session_state.messages.append(HumanMessage(content=prompt))
    st.session_state.msg_count    += 1
    st.session_state.history_labels.append(f'"{prompt[:52]}{"…" if len(prompt)>52 else ""}"')

    with st.spinner(""):
        content, comp_tok, total_tok = get_response(st.session_state.messages)
        st.session_state.messages.append(AIMessage(content=content))
        st.session_state.total_tokens = total_tok
        st.session_state.msg_count    += 1

    st.rerun()