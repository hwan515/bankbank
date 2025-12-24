<script setup>
import { ref, nextTick, onMounted, onBeforeUnmount, watch } from 'vue'
import { useChatbotStore } from '@/stores/chatbot'
import { useChatRoomsStore } from '@/stores/chatRooms'
import { useRealtimeChatStore } from '@/stores/realtimeChat'

const open = ref(false)
const activeTab = ref('bot') // 'bot' | 'chat'
const input = ref('')
const bodyRef = ref(null)

const bot = useChatbotStore()
const rooms = useChatRoomsStore()
const chat = useRealtimeChatStore()

import { computed } from 'vue'

const dmOnlyRooms = computed(() =>
  (rooms.rooms || []).filter((r) => r.is_dm === true)
)


// ✅ 채팅 모드: public | dm
const chatMode = ref('public')

// ✅ 선택된 방
const selectedRoomId = ref(null)

// ✅ DM 검색
const dmQuery = ref('')

// UI
const toggle = () => { open.value = !open.value; if (open.value) scrollToBottom() }
const close = () => (open.value = false)
const minimize = () => (open.value = false)

const scrollToBottom = async () => {
  await nextTick()
  const el = bodyRef.value
  if (!el) return
  el.scrollTop = el.scrollHeight
}

// 공통: room 입장(히스토리 → ws)
const enterRoom = async (roomId) => {
  selectedRoomId.value = roomId
  const history = await rooms.fetchHistory(roomId, 50)
  chat.setInitial(history)
  chat.connect(roomId)
  scrollToBottom()
}

// public 모드 초기화
const initPublic = async () => {
  await rooms.fetchPublicRooms()

  // ✅ 로비가 있으면 자동 선택(없으면 ensureLobby로 만들고 선택)
  // 1) publicRooms에서 is_lobby 찾기(서버에서 내려주면)
  const lobby = rooms.publicRooms.find((r) => r.is_lobby) || rooms.publicRooms.find((r) => (r.name || '').toLowerCase() === 'lobby')

  if (lobby) {
    // join 보장 후 입장
    await rooms.joinRoom(lobby.id).catch(() => {})
    await enterRoom(lobby.id)
    return
  }

  // 2) 없으면 서버에서 lobby ensure
  const ensured = await rooms.ensureLobby()
  await enterRoom(ensured.id)
}

// dm 모드 초기화
const initDM = async () => {
  await rooms.fetchRooms()

  const firstDM = (rooms.rooms || []).find((r) => r.is_dm === true)
  if (!selectedRoomId.value && firstDM) {
    await enterRoom(firstDM.id)
  }
}


const switchTab = async (tab) => {
  activeTab.value = tab
  if (tab === 'chat') {
    // 기본 public
    if (chatMode.value === 'public') await initPublic()
    else await initDM()
  } else {
    scrollToBottom()
  }
}

// ✅ 모드 변경 시 목록/입장 다시
watch(chatMode, async (mode) => {
  if (activeTab.value !== 'chat') return
  selectedRoomId.value = null
  chat.disconnect()
  chat.setInitial([])

  if (mode === 'public') await initPublic()
  else await initDM()
})

// ✅ DM 검색
watch(dmQuery, async (v) => {
  if (chatMode.value !== 'dm') return
  await rooms.searchUsers(v)
})

// 공개방 선택 변경
const onSelectPublicRoom = async () => {
  if (!selectedRoomId.value) return
  await rooms.joinRoom(selectedRoomId.value).catch(() => {})
  await enterRoom(selectedRoomId.value)
}

// DM방 선택 변경
const onSelectDMRoom = async () => {
  if (!selectedRoomId.value) return
  await enterRoom(selectedRoomId.value)
}

const startDM = async (username) => {
  const room = await rooms.ensureDM(username)
  dmQuery.value = ''
  // 결과 닫기 느낌
  rooms.userResults.splice?.(0) // pinia ref가 배열이면 splice 가능
  await enterRoom(room.id)
}

const sendBot = async () => {
  const text = input.value.trim()
  if (!text || bot.loading) return
  input.value = ''
  await bot.sendMessage(text)
  scrollToBottom()
}

const currentDMPartner = computed(() => {
  const room = dmOnlyRooms.value.find(r => r.id === selectedRoomId.value)
  return room?.dm_partner_username ? `@${room.dm_partner_username}` : '알 수 없음'
})


const sending = ref(false)

const sendChat = async () => {
  if (sending.value) return   // 🔒 중복 방지
  const text = input.value.trim()
  if (!text) return
  if (!selectedRoomId.value) return alert('먼저 방을 선택해줘!')

  // ❗ sendChat에서는 connect 절대 하지 않는다
  if (!chat.connected) {
    alert('채팅 연결 중입니다. 잠시만 기다려주세요.')
    return
  }

  sending.value = true
  chat.send(text)
  input.value = ''
  scrollToBottom()

  // 아주 짧게 잠금
  setTimeout(() => {
    sending.value = false
  }, 200)
}


// ESC 닫기
const onKeydown = (e) => { if (e.key === 'Escape') close() }
onMounted(() => window.addEventListener('keydown', onKeydown))
onBeforeUnmount(() => window.removeEventListener('keydown', onKeydown))
</script>

<template>
  <button class="chat-fab" @click="toggle" aria-label="Open chat">💬</button>

  <div v-if="open" class="chatbox card shadow">
    <div class="chatbox-header">
      <div class="title">Assistant</div>
      <div class="actions">
        <button class="mini-btn" @click="minimize">_</button>
        <button class="mini-btn" @click="close">×</button>
      </div>
    </div>

    <div class="chatbox-tabs">
      <button class="tab" :class="{active: activeTab==='bot'}" @click="switchTab('bot')">챗봇</button>
      <button class="tab" :class="{active: activeTab==='chat'}" @click="switchTab('chat')">채팅</button>
    </div>

    <!-- ✅ 채팅 탭 도구(미니멀) -->
    <div v-if="activeTab==='chat'" class="chat-tools">
      <div class="tool-row">
        <select class="mode-select" v-model="chatMode">
          <option value="public">공개방</option>
          <option value="dm">DM</option>
        </select>

        <span class="badge" :class="chat.connected ? 'on' : 'off'">
          {{ chat.connected ? 'ON' : 'OFF' }}
        </span>
      </div>

      <!-- 공개방: 전체 목록 -->
      <div v-if="chatMode==='public'" class="tool-row">
        <select class="room-select" v-model.number="selectedRoomId" @change="onSelectPublicRoom">
          <option :value="null" disabled>공개방 선택</option>
          <option v-for="r in rooms.publicRooms" :key="r.id" :value="r.id">
            {{ r.name || ('room-' + r.id) }}
          </option>
        </select>
      </div>

      <!-- DM: 내 방 + username 검색 -->
      <div v-else class="dm-box">
        <div class="tool-row">
          <select class="room-select" v-model.number="selectedRoomId" @change="onSelectDMRoom">
            <option :value="null" disabled>DM 방 선택</option>
            
            <option v-for="r in dmOnlyRooms" :key="r.id" :value="r.id">
              @{{ r.dm_partner_username }}
              <span v-if="r.last_message_at">
                · {{ new Date(r.last_message_at).toLocaleDateString() }}
              </span>
            </option>
            <div v-if="chatMode==='dm' && selectedRoomId" class="dm-current">
              현재 대화: <strong>{{ currentDMPartner }}</strong>
            </div>

          </select>
        </div>

        <div class="tool-row">
          <input class="dm-input" v-model="dmQuery" placeholder="username 검색 후 DM 시작…" />
        </div>

        <div v-if="rooms.userResults?.length" class="dm-results">
          <button v-for="u in rooms.userResults" :key="u.id" class="dm-item" @click="startDM(u.username)">
            @{{ u.username }}
          </button>
        </div>
      </div>
    </div>

    <div class="chatbox-body" ref="bodyRef">
      <!-- 챗봇 -->
      <template v-if="activeTab==='bot'">
        <div v-for="(m, i) in bot.messages" :key="i" class="msg" :class="m.role">
          <div class="bubble">{{ m.content }}</div>
        </div>
      </template>

      <!-- 채팅 -->
      <template v-else>
        <div v-if="!selectedRoomId" class="hint">
          {{ chatMode === 'public' ? '공개방을 선택해줘!' : 'DM 방을 선택하거나 username으로 DM을 시작해줘!' }}
        </div>

        <div v-for="m in chat.messages" :key="m.id" class="msg">
          <div class="meta">{{ m.sender }}</div>
          <div class="bubble">{{ m.text }}</div>
        </div>
      </template>
    </div>

    <div class="chatbox-input">
      <input
        v-model="input"
        class="input"
        :placeholder="activeTab==='bot' ? '질문 입력…' : '메시지 입력…'"
        @keyup.enter.prevent="activeTab==='bot' ? sendBot() : sendChat()"
      />

      <button class="send" @click="activeTab==='bot' ? sendBot() : sendChat()">전송</button>
    </div>
  </div>
</template>

<style scoped>
.chat-fab{ position:fixed; right:20px; bottom:20px; width:54px; height:54px; border-radius:999px; border:none; background:#111; color:#fff; font-size:20px; cursor:pointer; z-index:9999; }
.chatbox{ position:fixed; right:20px; bottom:86px; width:320px; height:480px; display:flex; flex-direction:column; border-radius:14px; overflow:hidden; z-index:9999; background:#fff; }
.chatbox-header{ padding:10px 12px; display:flex; align-items:center; justify-content:space-between; border-bottom:1px solid #eee; }
.chatbox-tabs{ display:flex; border-bottom:1px solid #eee; }
.tab{ flex:1; padding:8px; border:none; background:#fff; cursor:pointer; font-size:13px; }
.tab.active{ font-weight:700; background:#fafafa; }
.chatbox-body{ flex:1; overflow:auto; padding:12px; background:#fcfcfc; }
.chatbox-input{ display:flex; gap:8px; padding:10px; border-top:1px solid #eee; background:#fff; }
.input{ flex:1; border:1px solid #e6e6e6; border-radius:10px; padding:8px 10px; font-size:13px; }
.send{ border:none; background:#111; color:#fff; border-radius:10px; padding:0 12px; font-size:13px; cursor:pointer; }
.mini-btn{ border:none; background:transparent; cursor:pointer; font-size:16px; line-height:1; padding:2px 6px; }

.msg{ margin-bottom:10px; }
.meta{ font-size:11px; color:#777; margin-bottom:4px; }
.bubble{ display:inline-block; padding:8px 10px; border-radius:12px; background:#fff; border:1px solid #eee; font-size:13px; }
.msg.user .bubble{ background:#111; color:#fff; border-color:#111; }
.hint{ font-size:12px; color:#888; padding:8px; border:1px dashed #ddd; border-radius:10px; background:#fff; }

.chat-tools{ padding:10px 12px; border-bottom:1px solid #eee; background:#fff; }
.tool-row{ display:flex; gap:8px; align-items:center; margin-bottom:8px; }
.tool-row:last-child{ margin-bottom:0; }

.mode-select{ width:110px; border:1px solid #e6e6e6; border-radius:10px; padding:6px 8px; font-size:12px; background:#fff; }
.room-select{ flex:1; border:1px solid #e6e6e6; border-radius:10px; padding:6px 8px; font-size:12px; background:#fff; }

.badge{ font-size:11px; padding:2px 8px; border-radius:999px; border:1px solid #ddd; }
.badge.on{ background:#eefaf0; border-color:#cfead6; color:#1f7a3a; }
.badge.off{ background:#fff4f4; border-color:#f1caca; color:#b42318; }

.dm-input{ width:100%; border:1px solid #e6e6e6; border-radius:10px; padding:7px 10px; font-size:12px; }
.dm-results{ display:flex; flex-wrap:wrap; gap:6px; }
.dm-item{ border:1px solid #e6e6e6; background:#fff; border-radius:999px; padding:4px 10px; font-size:12px; cursor:pointer; }
.dm-item:hover{ background:#fafafa; }

.dm-current{
  font-size: 12px;
  color: #666;
  margin-top: -2px;
  margin-bottom: 6px;
}

</style>
