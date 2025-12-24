<template>
  <div class="page">
    <div class="container py-4">

      <!-- 로딩 -->
      <div v-if="loading" class="state">
        <div class="spinner-border" style="width: 2.6rem; height: 2.6rem;"></div>
        <p class="state-sub">상품 정보를 불러오는 중...</p>
      </div>

      <!-- 상세 -->
      <template v-else-if="product">
        <!-- 상단 헤더 -->
        <div class="head">
          <div class="ui-badge">Saving</div>
          <h1 class="ui-title serif-title">적금 상세</h1>
          <p class="ui-sub">
            {{ product.kor_co_nm }} · {{ product.fin_prdt_nm }}
          </p>
        </div>

        <div class="layout">
          <!-- 왼쪽: 요약 + 액션 -->
          <div class="left">
            <div class="box ui-card">
              <div class="box-head">
                <div class="box-title">요약</div>
              </div>

              <div class="box-body">
                <div class="kv">
                  <div class="kv-row">
                    <span class="k">금융회사</span>
                    <strong class="v">{{ product.kor_co_nm }}</strong>
                  </div>
                  <div class="kv-row">
                    <span class="k">상품명</span>
                    <strong class="v">{{ product.fin_prdt_nm }}</strong>
                  </div>
                  <div class="kv-row">
                    <span class="k">공시제출월</span>
                    <strong class="v">{{ product.dcls_month }}</strong>
                  </div>
                  <div class="kv-row">
                    <span class="k">가입제한</span>
                    <strong class="v">{{ getJoinDenyText(product.join_deny) }}</strong>
                  </div>
                  <div class="kv-row">
                    <span class="k">최고한도</span>
                    <strong class="v">
                      {{ product.max_limit ? product.max_limit.toLocaleString() + '원' : '한도없음' }}
                    </strong>
                  </div>
                </div>

                <div class="field mt2">
                  <label class="label">가입 기간</label>
                  <select v-model="selectedTerm" class="select">
                    <option value="">선택</option>
                    <option v-for="term in availableTerms" :key="term" :value="String(term)">
                      {{ term }}개월
                    </option>
                  </select>
                </div>

                <div class="field mt2">
                  <label class="label">적립 방식</label>
                  <select v-model="selectedSavingType" class="select">
                    <option value="">선택</option>
                    <option v-for="type in availableSavingTypes" :key="type" :value="type">
                      {{ type }}
                    </option>
                  </select>
                </div>

                <div class="field mt2">
                  <label class="label">월 납입액(원)</label>
                  <input
                    v-model.number="monthlyAmount"
                    type="number"
                    class="input"
                    min="0"
                    placeholder="예: 300000"
                  />
                </div>

                <div v-if="estimatedTotal != null" class="estimate mt2">
                  <div class="estimate-row">
                    <span class="ek">예상 이자</span>
                    <span class="ev">{{ estimatedInterest.toLocaleString() }}원</span>
                  </div>
                  <div class="estimate-row">
                    <span class="ek">예상 만기수령액</span>
                    <span class="ev strong">{{ estimatedTotal.toLocaleString() }}원</span>
                  </div>
                  <div class="estimate-note">* 단순 계산(세전) 기준입니다.</div>
                </div>

                <div class="cta">
                  <template v-if="isAuthenticated">
                    <button
                      class="ui-btn w100"
                      :class="subscribed ? 'ui-btn-danger' : 'ui-btn-primary'"
                      @click="toggleSubscription"
                      :disabled="subscribing || (!subscribed && !selectedTerm)"
                    >
                      {{ subscribing ? '처리중...' : (subscribed ? '가입 해제하기' : '가입하기') }}
                    </button>

                    <button
                      v-if="subscribed"
                      class="ui-btn ui-btn-ghost w100 mt2"
                      @click="updateSubscriptionTerm"
                      :disabled="subscribing || !canUpdateTerm"
                    >
                      기간 변경
                    </button>
                  </template>

                  <p v-else class="muted">
                    상품에 가입하려면
                    <router-link to="/login" class="link">로그인</router-link>이 필요합니다.
                  </p>
                </div>
              </div>
            </div>

            <router-link to="/products?tab=saving" class="ui-btn ui-btn-ghost mt">
              ← 목록으로 돌아가기
            </router-link>
          </div>

          <!-- 오른쪽: 상세 정보 + 옵션 -->
          <div class="right">
            <!-- 상세 정보 -->
            <div class="box ui-card mb">
              <div class="box-head">
                <div class="box-title">상품 정보</div>
              </div>

              <div class="box-body">
                <div class="info-grid">
                  <div class="info-item">
                    <div class="ik">가입방법</div>
                    <div class="iv">{{ product.join_way || '정보 없음' }}</div>
                  </div>
                  <div class="info-item">
                    <div class="ik">가입대상</div>
                    <div class="iv">{{ product.join_member || '정보 없음' }}</div>
                  </div>
                  <div class="info-item span-2">
                    <div class="ik">우대조건</div>
                    <div class="iv pre">{{ product.spcl_cnd || '해당사항 없음' }}</div>
                  </div>
                  <div class="info-item span-2">
                    <div class="ik">기타 유의사항</div>
                    <div class="iv pre">{{ product.etc_note || '해당사항 없음' }}</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 금리 옵션 -->
            <div class="box ui-card">
              <div class="box-head">
                <div class="box-title">금리 옵션</div>
              </div>

              <div class="box-body">
                <div class="table-wrap">
                  <table class="t">
                    <thead>
                      <tr>
                        <th>금리유형</th>
                        <th>적립유형</th>
                        <th>저축기간</th>
                        <th>기본금리</th>
                        <th>최고우대금리</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="option in product.saving_options" :key="option.id">
                        <td>{{ option.intr_rate_type_nm }}</td>
                        <td>{{ option.rsrv_type_nm }}</td>
                        <td>{{ option.save_trm }}개월</td>
                        <td>{{ option.intr_rate != null ? option.intr_rate + '%' : '-' }}</td>
                        <td>{{ option.intr_rate2 != null ? option.intr_rate2 + '%' : '-' }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <div v-if="!product.saving_options?.length" class="muted mt2">
                  금리 옵션 정보가 없습니다.
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- 실패 -->
      <div v-else class="state">
        <div class="alert alert-danger">상품 정보를 불러올 수 없습니다.</div>
        <router-link to="/products?tab=saving" class="ui-btn ui-btn-ghost mt">← 목록으로 돌아가기</router-link>
      </div>

    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useProductDetail } from '@/composables/useProductDetail'

const {
  product,
  loading,
  subscribed,
  subscribing,
  isAuthenticated,
  selectedTerm,
  selectedSavingType,
  monthlyAmount,
  availableTerms,
  availableSavingTypes,
  canUpdateTerm,
  getJoinDenyText,
  toggleSubscription,
  updateSubscriptionTerm
} = useProductDetail('saving')

const rateForEstimate = computed(() => {
  const productData = product.value
  const term = Number(selectedTerm.value)
  if (!productData || !Number.isFinite(term)) return null

  let options = productData.saving_options || []
  if (selectedSavingType.value) {
    options = options.filter((option) => option.rsrv_type_nm === selectedSavingType.value)
  }
  options = options.filter((option) => Number(option.save_trm) === term)
  if (!options.length) return null

  let bestRate = null
  options.forEach((option) => {
    const rawRate = option.intr_rate2 != null ? option.intr_rate2 : option.intr_rate
    const rate = Number(rawRate)
    if (Number.isFinite(rate)) {
      if (bestRate == null || rate > bestRate) {
        bestRate = rate
      }
    }
  })
  return bestRate
})

const estimatedInterest = computed(() => {
  const amount = Number(monthlyAmount.value)
  const term = Number(selectedTerm.value)
  const rate = Number(rateForEstimate.value)
  if (!Number.isFinite(amount) || amount <= 0) return null
  if (!Number.isFinite(term) || term <= 0) return null
  if (!Number.isFinite(rate) || rate <= 0) return null

  const monthlyRate = rate / 100 / 12
  const interest = amount * (term * (term + 1) / 2) * monthlyRate
  return Math.round(interest)
})

const estimatedTotal = computed(() => {
  if (estimatedInterest.value == null) return null
  const amount = Number(monthlyAmount.value)
  const term = Number(selectedTerm.value)
  if (!Number.isFinite(amount) || !Number.isFinite(term)) return null
  return Math.round(amount * term + estimatedInterest.value)
})
</script>

<style scoped>
/* 배경 */
.page {
  min-height: 100%;
  background:
    radial-gradient(900px 300px at 10% 0%, rgba(27, 95, 122, 0.10), transparent 60%),
    linear-gradient(180deg, var(--bg-alt) 0%, var(--bg) 100%);
}

/* 상태 */
.state {
  text-align: center;
  padding: 48px 0;
}
.state-sub {
  margin-top: 12px;
  color: var(--muted);
  font-size: 13px;
}

/* 헤더 */
.head { margin-bottom: 14px; }
.ui-title { margin: 10px 0 6px; }
.ui-sub { margin: 0; }

/* 레이아웃 */
.layout {
  display: grid;
  grid-template-columns: 380px 1fr;
  gap: 14px;
}
@media (max-width: 992px) {
  .layout { grid-template-columns: 1fr; }
}

/* 공통 박스 */
.box {
  border-radius: 16px;
  overflow: hidden;
}
.box-head {
  padding: 14px 14px 10px;
  border-bottom: 1px solid var(--border);
}
.box-title { font-weight: 700; letter-spacing: -0.2px; color: var(--ink); }
.box-body { padding: 14px; }

.mb { margin-bottom: 14px; }
.mt { margin-top: 12px; }
.mt2 { margin-top: 10px; }
.field { display: grid; gap: 6px; }
.label { font-size: 12px; font-weight: 700; color: var(--ink); }
.select, .input {
  height: 40px;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: var(--surface);
  padding: 0 10px;
  font-size: 14px;
}
.estimate {
  background: var(--bg-alt);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 10px;
  display: grid;
  gap: 6px;
}
.estimate-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}
.estimate-note {
  font-size: 11px;
  color: var(--muted);
}

/* Key-Value */
.kv-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid var(--border);
}
.kv-row:last-child { border-bottom: 0; }
.k { color: var(--muted); font-size: 13px; }
.v { color: var(--ink); font-size: 13px; font-weight: 700; }

/* CTA */
.cta { margin-top: 12px; }
.muted { color: var(--muted); font-size: 13px; margin: 0; }
.link { color: var(--accent); font-weight: 700; text-decoration: none; }
.link:hover { text-decoration: underline; }

/* 정보 그리드 */
.info-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}
.info-item {
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 12px;
  background: var(--surface);
}
.info-item.span-2 { grid-column: 1 / -1; }

.ik { font-size: 12px; font-weight: 700; color: var(--ink); margin-bottom: 6px; }
.iv { font-size: 13px; color: var(--ink-soft); line-height: 1.5; }
.pre { white-space: pre-line; }

/* 테이블 */
.table-wrap { overflow-x: auto; }
.t {
  width: 100%;
  border-collapse: collapse;
  min-width: 720px;
}
.t thead th {
  text-align: left;
  font-size: 12px;
  font-weight: 700;
  color: var(--ink);
  background: var(--bg-alt);
  border-bottom: 1px solid var(--border);
  padding: 10px 10px;
  white-space: nowrap;
}
.t tbody td {
  font-size: 13px;
  color: var(--ink-soft);
  border-bottom: 1px solid var(--border);
  padding: 10px 10px;
  white-space: nowrap;
}
</style>
