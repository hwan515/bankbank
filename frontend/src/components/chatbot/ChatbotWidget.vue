<template>
  <!-- 작은 채팅창 -->
  <div v-if="open" class="chat-window ui-card" role="dialog" aria-label="채팅 위젯">
    <!-- 헤더 -->
    <div class="chat-header">
      <div class="h-left">
        <div class="dot" :class="{ off: activeTab === 'chat' && !chat.connected }"></div>
        <div class="h-title">
          <div class="t1">Bankbook</div>
          <div class="t2">{{ activeTab === 'bot' ? '챗봇 상담' : (chat.connected ? '실시간 채팅' : '채팅 미연결') }}</div>
        </div>
      </div>

      <div class="h-actions">
        <button class="icon-btn" @click="minimize" title="최소화">—</button>
        <button class="icon-btn" @click="close" title="닫기">✕</button>
      </div>
    </div>

    <!-- 탭 -->
    <div class="tabs">
      <button class="tab" :class="{ active: activeTab === 'bot' }" @click="switchTab('bot')">챗봇</button>
      <button class="tab" :class="{ active: activeTab === 'chat' }" @click="switchTab('chat')">채팅</button>
    </div>

    <!-- 바디 -->
    <div class="chat-body" ref="bodyRef">
      <!-- 챗봇 -->
      <template v-if="activeTab === 'bot'">
        <div v-for="m in bot.messages" :key="m.id" class="msg" :class="m.role === 'user' ? 'user' : 'bot'">
          <div class="bubble">{{ m.text }}</div>
        </div>
        <div v-if="bot.loading" class="msg bot">
          <div class="bubble ghost">응답 생성 중…</div>
        </div>
      </template>

      <!-- 실시간 채팅 -->
      <template v-else>
        <div class="chat-meta">
          <div class="meta-row">
            <span class="label">Room</span>
            <span class="value">{{ roomId }}</span>
          </div>
          <div class="meta-row">
            <span class="label">Status</span>
            <span class="value" :class="{ ok: chat.connected }">{{ chat.connected ? 'Connected' : 'Disconnected' }}</span>
          </div>
        </div>

        <div v-for="m in chat.messages" :key="m.id" class="msg" :class="m.sender === sender ? 'user' : 'bot'">
          <div class="bubble">
            <div class="sender" v-if="m.sender && m.sender !== 'system'">{{ m.sender }}</div>
            <div>{{ m.text }}</div>
          </div>
        </div>
      </template>
    </div>

    <!-- 풋터(입력) -->
    <div class="chat-input">
      <!-- 챗봇 입력 -->
      <template v-if="activeTab === 'bot'">
        <input
          v-model.trim="input"
          class="input"
          placeholder="챗봇에게 질문해보세요…"
          :disabled="bot.loading"
          @keydown.enter.exact.prevent="sendBot"
        />
        <button class="send" :disabled="bot.loading || !input.trim()" @click="sendBot">전송</button>
      </template>

      <!-- 채팅 입력 -->
      <template v-else>
        <input
          v-model.trim="input"
          class="input"
          placeholder="채팅 메시지를 입력하세요…"
          @keydown.enter.exact.prevent="sendChat"
        />
        <button class="send" :disabled="!input.trim()" @click="sendChat">전송</button>
      </template>
    </div>

    <!-- 하단 액션 -->
    <div class="footer-actions">
      <button v-if="activeTab === 'bot'" class="mini-btn" @click="bot.clear">대화 초기화</button>

      <template v-else>
        <button v-if="!chat.connected" class="mini-btn" @click="chat.connect(roomId)">연결</button>
        <button v-else class="mini-btn" @click="chat.disconnect">연결끊기</button>
        <button class="mini-btn danger" @click="chat.reset">채팅 초기화</button>
      </template>
    </div>
  </div>

  <!-- FAB 버튼 -->
  <button class="fab" @click="toggle" :aria-expanded="open ? 'true' : 'false'" aria-label="채팅 열기">
    <span v-if="!open">💬</span>
    <span v-else>✕</span>
  </button>
</template>

<script setup>
import { ref, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { useChatbotStore } from '@/stores/chatbot'
import { useRealtimeChatStore } from '@/stores/realtimeChat'

const open = ref(false)
const activeTab = ref('bot') // 'bot' | 'chat'
const input = ref('')
const bodyRef = ref(null)

// 채팅 기본 설정(임시)
// ✅ 로그인 유저 닉네임으로 바꾸면 됨
const sender = ref('me')
// ✅ 기본 채팅방(나중에 “상품/커뮤니티/1:1” 룸아이디로 바꿔도 됨)
const roomId = ref('lobby')

const bot = useChatbotStore()
const chat = useRealtimeChatStore()

const toggle = () => {
  open.value = !open.value
  if (open.value) scrollToBottom()
}
const close = () => (open.value = false)
const minimize = () => (open.value = false)

const switchTab = (tab) => {
  activeTab.value = tab
  // 채팅 탭 들어갈 때 자동 연결하고 싶으면 여기서 connect 호출
  // if (tab === 'chat' && !chat.connected) chat.connect(roomId.value)
  scrollToBottom()
}

const scrollToBottom = async () => {
  await nextTick()
  const el = bodyRef.value
  if (!el) return
  el.scrollTop = el.scrollHeight
}

const sendBot = async () => {
  const text = input.value.trim()
  if (!text || bot.loading) return
  input.value = ''
  await bot.sendMessage(text)
  scrollToBottom()
}

const sendChat = () => {
  const text = input.value.trim()
  if (!text) return
  if (!chat.connected) {
    // 연결 안돼 있으면 자동 연결 후 전송
    chat.connect(roomId.value)
    setTimeout(() => chat.send(sender.value, text), 250)
  } else {
    chat.send(sender.value, text)
  }
  // 내 로컬 에코(서버가 다시 보내주는 구조면 없어도 됨)
  chat.messages.push({ id: Date.now(), sender: sender.value, text })
  input.value = ''
  scrollToBottom()
}

// ESC로 닫기
const onKeydown = (e) => {
  if (e.key === 'Escape') close()
}
onMounted(() => window.addEventListener('keydown', onKeydown))
onBeforeUnmount(() => window.removeEventListener('keydown', onKeydown))
</script>

<style scoped>
/* FAB */
.fab {
  position: fixed;
  right: 18px;
  bottom: 18px;
  width: 52px;
  height: 52px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: var(--accent);
  color: #fff;
  font-size: 20px;
  display: grid;
  place-items: center;
  cursor: pointer;
  z-index: 9999;
  box-shadow: var(--shadow-2);
}
.fab:hover { background: var(--accent-strong); }

/* Window */
.chat-window {
  position: fixed;
  right: 18px;
  bottom: 80px;
  width: 360px;
  height: 520px;
  border-radius: 18px;
  overflow: hidden;
  z-index: 9999;
  display: grid;
  grid-template-rows: auto auto 1fr auto auto;
}

/* Header */
.chat-header {
  padding: 12px 12px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.h-left { display: flex; align-items: center; gap: 10px; }
.dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: #22c55e;
  box-shadow: 0 0 0 4px rgba(34,197,94,0.15);
}
.dot.off {
  background: #f97316;
  box-shadow: 0 0 0 4px rgba(249,115,22,0.14);
}
.h-title .t1 { font-weight: 700; color: var(--ink); font-size: 14px; letter-spacing: -0.2px; }
.h-title .t2 { font-size: 12px; color: var(--muted); margin-top: 2px; }

.h-actions { display: flex; gap: 6px; }
.icon-btn {
  width: var(--btn-h-sm);
  height: var(--btn-h-sm);
  border-radius: 10px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--ink);
  font-weight: 700;
  cursor: pointer;
}
.icon-btn:hover { background: var(--bg-alt); }

/* Tabs */
.tabs {
  padding: 10px 10px 0;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}
.tab {
  height: var(--btn-h-sm);
  border-radius: 12px;
  border: 1px solid var(--border);
  background: var(--surface);
  font-weight: 700;
  color: var(--ink-soft);
  cursor: pointer;
}
.tab.active {
  background: var(--accent);
  border-color: var(--accent);
  color: #fff;
}

/* Body */
.chat-body {
  padding: 12px;
  overflow: auto;
  background: var(--bg-alt);
}
.msg { display: flex; margin-bottom: 10px; }
.msg.user { justify-content: flex-end; }
.msg.bot { justify-content: flex-start; }

.bubble {
  max-width: 80%;
  padding: 10px 12px;
  border-radius: 14px;
  border: 1px solid var(--border);
  background: var(--surface);
  font-size: 13px;
  line-height: 1.45;
  color: var(--ink-soft);
  white-space: pre-line;
}
.msg.user .bubble {
  background: var(--accent);
  border-color: var(--accent);
  color: #fff;
}
.bubble.ghost { color: var(--muted); }

.sender {
  font-size: 11px;
  font-weight: 700;
  opacity: 0.75;
  margin-bottom: 4px;
}

/* Chat meta */
.chat-meta {
  border: 1px solid var(--border);
  background: var(--surface);
  border-radius: 14px;
  padding: 10px 12px;
  margin-bottom: 10px;
}
.meta-row {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--muted);
}
.meta-row .label { font-weight: 700; color: var(--ink); }
.meta-row .value.ok { color: #16a34a; font-weight: 900; }

/* Input */
.chat-input {
  border-top: 1px solid var(--border);
  padding: 10px;
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 8px;
  background: var(--surface);
}
.input {
  height: var(--btn-h);
  border-radius: 999px;
  border: 1px solid var(--border);
  padding: 0 12px;
  font-size: 14px;
  outline: none;
}
.input:focus {
  border-color: rgba(27, 95, 122, 0.5);
  box-shadow: 0 0 0 0.2rem rgba(27, 95, 122, 0.15);
}
.send {
  height: var(--btn-h);
  border-radius: 999px;
  border: 1px solid var(--accent);
  background: var(--accent);
  color: #fff;
  font-weight: 600;
  font-size: 13px;
  padding: 0 12px;
  cursor: pointer;
}
.send:hover { background: var(--accent-strong); }
.send:disabled { opacity: .6; cursor: not-allowed; }

/* footer buttons */
.footer-actions {
  border-top: 1px solid var(--border);
  padding: 10px;
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  background: var(--surface);
}
.mini-btn {
  height: var(--btn-h-sm);
  padding: 0 10px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--ink);
  font-weight: 600;
  font-size: 12px;
  cursor: pointer;
}
.mini-btn:hover { background: var(--bg-alt); }
.mini-btn.danger { color: #b91c1c; border-color: #f0d7d7; }

/* Mobile */
@media (max-width: 576px) {
  .chat-window {
    right: 12px;
    left: 12px;
    width: auto;
    height: 70vh;
    bottom: 74px;
  }
  .fab { right: 12px; bottom: 12px; }
}
</style>
