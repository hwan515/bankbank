<template>
  <div class="preference-form">
    <div class="form-section">
      <h6 class="section-title">소비 정보</h6>

      <div class="form-group">
        <label class="form-label">월 평균 소비 금액</label>
        <select v-model.number="form.monthly_spend" class="form-select">
          <option :value="0">선택 안함</option>
          <option :value="500000">50만원 이하</option>
          <option :value="1000000">100만원 이하</option>
          <option :value="2000000">200만원 이하</option>
          <option :value="3000000">300만원 이하</option>
          <option :value="5000000">500만원 이하</option>
          <option :value="10000000">500만원 초과</option>
        </select>
      </div>

      <div class="form-group">
        <label class="form-label">연회비 허용 상한</label>
        <select v-model.number="form.fee_tolerance" class="form-select">
          <option :value="0">무료만</option>
          <option :value="10000">1만원 이하</option>
          <option :value="20000">2만원 이하</option>
          <option :value="50000">5만원 이하</option>
          <option :value="100000">10만원 이하</option>
          <option :value="999999">제한 없음</option>
        </select>
      </div>

      <div class="form-group">
        <label class="form-label">전월실적 허용 상한</label>
        <select v-model.number="form.min_spend_tolerance" class="form-select">
          <option :value="0">조건 없음만</option>
          <option :value="300000">30만원 이하</option>
          <option :value="500000">50만원 이하</option>
          <option :value="1000000">100만원 이하</option>
          <option :value="999999">제한 없음</option>
        </select>
      </div>
    </div>

    <div class="form-section">
      <h6 class="section-title">선호 카테고리</h6>
      <p class="section-desc">자주 사용하는 카테고리의 중요도를 설정하세요 (0~5)</p>

      <div class="category-grid">
        <div
          v-for="(name, code) in categories"
          :key="code"
          class="category-item"
        >
          <div class="category-label">{{ name }}</div>
          <div class="category-slider">
            <input
              type="range"
              min="0"
              max="5"
              v-model.number="form.category_weights[code]"
              class="form-range"
            />
            <span class="category-value">{{ form.category_weights[code] || 0 }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="form-actions">
      <button
        class="ui-btn ui-btn-primary w100"
        @click="handleSave"
        :disabled="saving"
      >
        {{ saving ? '저장 중...' : '설정 저장' }}
      </button>
    </div>

    <div v-if="saveMessage" class="save-message" :class="saveMessage.type">
      {{ saveMessage.text }}
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  profile: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['save'])

const categories = {
  TRANS: '교통',
  COFFEE: '카페',
  FOOD: '음식',
  SHOP: '쇼핑',
  GAS: '주유',
  MART: '마트',
  TRAVEL: '여행',
  SUB: '구독',
  PAY: '간편결제',
  COMM: '통신',
  UTIL: '공과금',
  ETC: '기타'
}

const form = ref({
  monthly_spend: 0,
  fee_tolerance: 0,
  min_spend_tolerance: 0,
  category_weights: {}
})

const saving = ref(false)
const saveMessage = ref(null)

// 프로필 데이터 동기화
watch(() => props.profile, (p) => {
  if (p) {
    form.value = {
      monthly_spend: p.monthly_spend || 0,
      fee_tolerance: p.fee_tolerance || 0,
      min_spend_tolerance: p.min_spend_tolerance || 0,
      category_weights: { ...p.category_weights } || {}
    }
  }
}, { immediate: true })

async function handleSave() {
  saving.value = true
  saveMessage.value = null

  try {
    await emit('save', form.value)
    saveMessage.value = { type: 'success', text: '설정이 저장되었습니다.' }
    setTimeout(() => { saveMessage.value = null }, 3000)
  } catch (err) {
    saveMessage.value = { type: 'error', text: '저장 중 오류가 발생했습니다.' }
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.preference-form {
  padding: 4px 0;
}

.form-section {
  margin-bottom: 24px;
}

.section-title {
  font-weight: 700;
  color: var(--ink);
  margin-bottom: 4px;
}

.section-desc {
  font-size: 12px;
  color: var(--muted);
  margin-bottom: 12px;
}

.form-group {
  margin-bottom: 16px;
}

.form-label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: var(--ink-soft);
  margin-bottom: 6px;
}

.form-select {
  width: 100%;
  height: 40px;
  padding: 0 12px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 14px;
  background: var(--surface);
}

.form-select:focus {
  outline: none;
  border-color: rgba(27, 95, 122, 0.5);
  box-shadow: 0 0 0 0.2rem rgba(27, 95, 122, 0.15);
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

@media (max-width: 576px) {
  .category-grid {
    grid-template-columns: 1fr;
  }
}

.category-item {
  padding: 10px 12px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--bg-alt);
}

.category-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--ink-soft);
  margin-bottom: 6px;
}

.category-slider {
  display: flex;
  align-items: center;
  gap: 8px;
}

.form-range {
  flex: 1;
  height: 6px;
}

.category-value {
  font-size: 13px;
  font-weight: 700;
  color: var(--ink);
  min-width: 20px;
  text-align: right;
}

.form-actions {
  margin-top: 20px;
}


.save-message {
  margin-top: 12px;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 13px;
  text-align: center;
}

.save-message.success {
  background: #d4edda;
  color: #155724;
}

.save-message.error {
  background: #f8d7da;
  color: #721c24;
}
</style>
