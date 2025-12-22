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
          <div class="badge">Deposit</div>
          <h1 class="title">정기예금 상세</h1>
          <p class="sub">
            {{ product.kor_co_nm }} · {{ product.fin_prdt_nm }}
          </p>
        </div>

        <div class="layout">
          <!-- 왼쪽: 요약 + 액션 -->
          <div class="left">
            <div class="box">
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
                </div>

                <div class="cta">
                  <button
                    v-if="isAuthenticated"
                    class="btn-solid"
                    :class="{ danger: subscribed }"
                    @click="toggleSubscription"
                    :disabled="subscribing"
                  >
                    {{ subscribing ? '처리중...' : (subscribed ? '가입 해제하기' : '가입하기') }}
                  </button>

                  <p v-else class="muted">
                    상품에 가입하려면
                    <router-link to="/login" class="link">로그인</router-link>이 필요합니다.
                  </p>
                </div>
              </div>
            </div>

            <router-link to="/products" class="btn-ghost mt">
              ← 목록으로 돌아가기
            </router-link>
          </div>

          <!-- 오른쪽: 상세 정보 + 옵션 -->
          <div class="right">
            <!-- 상세 정보 -->
            <div class="box mb">
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
            <div class="box">
              <div class="box-head">
                <div class="box-title">금리 옵션</div>
              </div>

              <div class="box-body">
                <div class="table-wrap">
                  <table class="t">
                    <thead>
                      <tr>
                        <th>금리유형</th>
                        <th>저축기간</th>
                        <th>기본금리</th>
                        <th>최고우대금리</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="option in product.options" :key="option.id">
                        <td>{{ option.intr_rate_type_nm }}</td>
                        <td>{{ option.save_trm }}개월</td>
                        <td>{{ option.intr_rate != null ? option.intr_rate + '%' : '-' }}</td>
                        <td>{{ option.intr_rate2 != null ? option.intr_rate2 + '%' : '-' }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <div v-if="!product.options?.length" class="muted mt2">
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
        <router-link to="/products" class="btn-ghost mt">← 목록으로 돌아가기</router-link>
      </div>

    </div>
  </div>
</template>

<script setup>
import { useProductDetail } from '@/composables/useProductDetail'

const {
  product,
  loading,
  subscribed,
  subscribing,
  isAuthenticated,
  getJoinDenyText,
  toggleSubscription
} = useProductDetail('deposit')
</script>

<style scoped>
/* 배경 */
.page {
  min-height: 100%;
  background: linear-gradient(180deg, #fafafa 0%, #ffffff 100%);
}

/* 상태 */
.state {
  text-align: center;
  padding: 48px 0;
}
.state-sub {
  margin-top: 12px;
  color: #777;
  font-size: 13px;
}

/* 헤더 */
.head {
  margin-bottom: 14px;
}
.badge {
  display: inline-flex;
  align-items: center;
  height: 26px;
  padding: 0 10px;
  border-radius: 999px;
  border: 1px solid #ededed;
  background: #f6f6f6;
  color: #333;
  font-size: 12px;
  font-weight: 900;
}
.title {
  margin: 10px 0 6px;
  font-size: 26px;
  font-weight: 950;
  letter-spacing: -0.4px;
  color: #111;
}
.sub {
  margin: 0;
  font-size: 13px;
  color: #777;
}

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
  background: #fff;
  border: 1px solid #efefef;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 1px 2px rgba(0,0,0,0.08), 0 10px 24px rgba(0,0,0,0.06);
}
.box-head {
  padding: 14px 14px 10px;
  border-bottom: 1px solid #f0f0f0;
}
.box-title {
  font-weight: 900;
  letter-spacing: -0.2px;
  color: #111;
}
.box-body { padding: 14px; }

.mb { margin-bottom: 14px; }
.mt { margin-top: 12px; }
.mt2 { margin-top: 10px; }

/* Key-Value */
.kv-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid #f2f2f2;
}
.kv-row:last-child { border-bottom: 0; }
.k { color: #777; font-size: 13px; }
.v { color: #111; font-size: 13px; font-weight: 900; }

/* CTA */
.cta { margin-top: 12px; }
.muted { color: #777; font-size: 13px; margin: 0; }
.link { color: #111; font-weight: 900; text-decoration: none; }
.link:hover { text-decoration: underline; }

/* 버튼 */
.btn-solid {
  width: 100%;
  height: 44px;
  border-radius: 14px;
  border: 1px solid #111;
  background: #111;
  color: #fff;
  font-weight: 900;
  font-size: 14px;
  cursor: pointer;
}
.btn-solid:hover { background: #000; }
.btn-solid:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-solid.danger {
  background: #fff;
  color: #111;
  border-color: #e8e8e8;
}
.btn-solid.danger:hover { background: #fafafa; }

.btn-ghost {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 40px;
  padding: 0 12px;
  border-radius: 12px;
  border: 1px solid #e8e8e8;
  background: #fff;
  color: #222;
  font-weight: 900;
  font-size: 13px;
  text-decoration: none;
  cursor: pointer;
}
.btn-ghost:hover { background: #fafafa; }

/* 정보 그리드 */
.info-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}
.info-item {
  border: 1px solid #efefef;
  border-radius: 14px;
  padding: 12px;
  background: #fff;
}
.info-item.span-2 { grid-column: 1 / -1; }

.ik {
  font-size: 12px;
  font-weight: 900;
  color: #111;
  margin-bottom: 6px;
}
.iv {
  font-size: 13px;
  color: #555;
  line-height: 1.5;
}
.pre { white-space: pre-line; }

/* 테이블 */
.table-wrap { overflow-x: auto; }
.t {
  width: 100%;
  border-collapse: collapse;
  min-width: 560px;
}
.t thead th {
  text-align: left;
  font-size: 12px;
  font-weight: 900;
  color: #111;
  background: #fafafa;
  border-bottom: 1px solid #efefef;
  padding: 10px 10px;
  white-space: nowrap;
}
.t tbody td {
  font-size: 13px;
  color: #444;
  border-bottom: 1px solid #f2f2f2;
  padding: 10px 10px;
  white-space: nowrap;
}
</style>
