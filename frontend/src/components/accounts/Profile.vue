<template>
  <div class="container profile-shell">
    <div v-if="loading" class="sub">로딩중...</div>

    <template v-else>
      <div class="container profile-shell">
        <!-- Header (그대로) -->
        <div class="header">
          <div class="avatar-wrap">
            <img src="@/assets/cat.jpg" alt="프로필 이미지" class="avatar" />
          </div>

          <div class="header-text">
            <h1 class="title">{{ account.username }}</h1>
            <p class="sub">{{ account.greeting || '아직 인사말이 없습니다. 작성해주세요.' }}</p>
          </div>

          <div class="header-actions">
            <button class="btn ghost" @click="openEdit">편집</button>
            <button class="btn solid">저장</button>
          </div>
        </div>

        <div class="divider"></div>

        <!-- Content (레이아웃 그대로) -->
        <div class="grid">
          <!-- ✅ 정보 카드: 클릭하면 모달 -->
          <div
            v-for="(info, idx) in infos"
            :key="info.id"
            class="card"
            style="cursor: pointer;"
            @click="openInfoModal(idx)"
          >
            <div class="card-title"> 제목 : {{ info.title }}</div>
            <div class="card-body">
              {{ info.content }}
            </div>
          </div>

          <!-- ✅ + 카드: 클릭하면 새 정보 모달 -->
          <div class="card" @click="openInfoModal(null)" style="cursor: pointer; text-align: center;">
            <div class="card-title">+</div>
            <div class="card-body">정보 추가</div>
          </div>
        </div>
      </div>

      <!-- 기존 프로필 편집 모달 (그대로) -->
      <EditModal
        v-if="isEditOpen"
        :initial="draft"
        :saving="saving"
        @close="isEditOpen = false"
        @save="handleSave"
      />

      <!-- ✅ 정보 편집/추가 모달 (분리된 파일) -->
      <InfoModal
        v-if="isInfoOpen"
        :initial="infoDraft"
        :saving="infoSaving"
        :is-new="selectedInfoIndex === null"
        @close="closeInfoModal"
        @save="saveInfo"
        @remove="removeInfo"
      />
    </template>
  </div>
</template>

<script setup>
import { useAccountStore } from '@/stores/account'
import { ref, onMounted } from 'vue'
import EditModal from '@/components/accounts/EditModal.vue'
import InfoModal from '@/components/accounts/InfoModal.vue'

const accountStore = useAccountStore()
const account = ref(null)
const infromation = ref(null)
const loading = ref(true)

const isEditOpen = ref(false)
const saving = ref(false)
const draft = ref({ username: '', greeting: '', email: '' })

// ✅ infos 상태
const infos = ref([])

// ✅ InfoModal 상태
const isInfoOpen = ref(false)
const infoSaving = ref(false)
const selectedInfoIndex = ref(null) // number | null
const infoDraft = ref({ title: '', text: '' })

onMounted(async () => {
  try {
    const data = await accountStore.loadProfile()
    account.value = data || null
    
    const info = await accountStore.load_information()
    infos.value = info || null
  } finally {
    loading.value = false
  }
})

// 프로필 편집 모달
const openEdit = () => {
  draft.value = {
    username: account.value?.username ?? '',
    greeting: account.value?.greeting ?? '',
    email: account.value?.email ?? '',
  }
  isEditOpen.value = true
}

const handleSave = async (payload) => {
  saving.value = true
  try {
    const updated = await accountStore.updateProfile(payload)
    account.value = updated
    isEditOpen.value = false
  } catch (e) {
    console.error(e)
    alert('저장 실패')
  } finally {
    saving.value = false
  }
}

// ✅ 정보 모달 열기 (idx=null이면 새로 추가)
const openInfoModal = (idx) => {
  selectedInfoIndex.value = idx

  if (idx === null) {
    infoDraft.value = { title: '', text: '' }
  } else {
    const cur = infos.value[idx]
    infoDraft.value = { title: cur.title ?? '', text: cur.text ?? '' }
  }

  isInfoOpen.value = true
}

const closeInfoModal = () => {
  isInfoOpen.value = false
  selectedInfoIndex.value = null
}

// ✅ 저장(추가/수정)
const saveInfo = async ({ title, content }) => {
  infoSaving.value = true
  try {
    if (selectedInfoIndex.value === null) {
      console.log(title,content)
      const created = await accountStore.addInformation({ title:title, content:content }) // POST
      infos.value.push(created) // 서버가 id 포함해서 주는 값
    } else {
      // const cur = infos.value[selectedInfoIndex.value]
      // const updated = await accountStore.addInformation(cur.id, { title, content }) // PATCH
      // infos.value[selectedInfoIndex.value] = updated
    }
    closeInfoModal()
  } finally {
    infoSaving.value = false
  }
}


// ✅ 삭제
const removeInfo = () => {
  if (selectedInfoIndex.value === null) return
  infos.value.splice(selectedInfoIndex.value, 1)
  closeInfoModal()
}
</script>

<style scoped>
/* ✅ 너가 올린 기존 CSS 그대로 */
.profile-shell { margin-top: 5%; padding: 24px; border: 1px solid #ececec; border-radius: 14px; background: #ffffff; }
.header { display: grid; grid-template-columns: auto 1fr auto; gap: 16px; align-items: center; }
.avatar-wrap { display: flex; align-items: center; justify-content: center; }
.avatar { width: 64px; height: 64px; border-radius: 999px; object-fit: cover; border: 1px solid #ededed; }
.title { margin: 0; font-size: 20px; font-weight: 750; letter-spacing: -0.2px; }
.sub { margin: 6px 0 0; font-size: 13px; color: #777; }
.header-actions { display: flex; gap: 8px; }
.btn { height: 34px; padding: 0 12px; border-radius: 10px; font-size: 13px; cursor: pointer; border: 1px solid transparent; }
.btn.ghost { background: #fff; border-color: #e8e8e8; color: #222; }
.btn.ghost:hover { background: #fafafa; }
.btn.solid { background: #111; color: #fff; }
.btn.solid:hover { background: #000; }
.divider { height: 1px; background: #f0f0f0; margin: 18px 0; }
.grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }
.card {
  border: 1px solid #efefef;
  border-radius: 12px;
  padding: 14px;
  background: #fff;

  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.08),
    0 4px 8px rgba(0, 0, 0, 0.06);

  transition: background 0.12s ease,
              border-color 0.12s ease,
              box-shadow 0.12s ease;
}

.card:hover {
  background: #fcfcfc;
  border-color: #e7e7e7;

  /* 👇 hover 시만 살짝 강조 */
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
}

.card-title { font-size: 13px; font-weight: 700; color: #111; margin-bottom: 8px; }
.card-body { font-size: 13px; color: #555; line-height: 1.45; }
@media (max-width: 992px) { .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 576px) {
  .header { grid-template-columns: auto 1fr; }
  .header-actions { grid-column: 1 / -1; justify-content: flex-end; }
  .grid { grid-template-columns: 1fr; }
}


</style>
