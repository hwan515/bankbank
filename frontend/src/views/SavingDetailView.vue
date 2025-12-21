<template>
  <div class="container py-4">
    <div v-if="loading" class="text-center">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else-if="product" class="card">
      <div class="card-header bg-success text-white">
        <h4 class="mb-0">적금 상세</h4>
      </div>
      <div class="card-body">
        <table class="table table-bordered">
          <tbody>
            <tr>
              <th class="table-light" style="width: 150px;">공시제출월</th>
              <td>{{ product.dcls_month }}</td>
            </tr>
            <tr>
              <th class="table-light">금융회사명</th>
              <td>{{ product.kor_co_nm }}</td>
            </tr>
            <tr>
              <th class="table-light">상품명</th>
              <td>{{ product.fin_prdt_nm }}</td>
            </tr>
            <tr>
              <th class="table-light">가입제한</th>
              <td>{{ getJoinDenyText(product.join_deny) }}</td>
            </tr>
            <tr>
              <th class="table-light">가입방법</th>
              <td>{{ product.join_way }}</td>
            </tr>
            <tr>
              <th class="table-light">가입대상</th>
              <td>{{ product.join_member }}</td>
            </tr>
            <tr>
              <th class="table-light">최고한도</th>
              <td>{{ product.max_limit ? product.max_limit.toLocaleString() + '원' : '한도없음' }}</td>
            </tr>
            <tr>
              <th class="table-light">우대조건</th>
              <td>{{ product.spcl_cnd || '해당사항 없음' }}</td>
            </tr>
            <tr>
              <th class="table-light">기타 유의사항</th>
              <td>{{ product.etc_note || '해당사항 없음' }}</td>
            </tr>
          </tbody>
        </table>

        <!-- 금리 옵션 리스트 -->
        <h5 class="mt-4 mb-3">금리 옵션</h5>
        <table class="table table-striped table-hover">
          <thead class="table-dark">
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
              <td>{{ option.intr_rate ? option.intr_rate + '%' : '-' }}</td>
              <td>{{ option.intr_rate2 ? option.intr_rate2 + '%' : '-' }}</td>
            </tr>
          </tbody>
        </table>

        <!-- 가입하기 버튼 (로그인 사용자만) -->
        <div class="mt-4 text-center">
          <button
            v-if="isAuthenticated"
            @click="toggleSubscription"
            :class="['btn', 'btn-lg', subscribed ? 'btn-danger' : 'btn-success']"
            :disabled="subscribing"
          >
            {{ subscribing ? '처리중...' : (subscribed ? '가입 해제하기' : '가입하기') }}
          </button>
          <p v-else class="text-muted">
            상품에 가입하려면 <router-link to="/login">로그인</router-link>이 필요합니다.
          </p>
        </div>
      </div>
    </div>

    <div v-else class="alert alert-danger">
      상품 정보를 불러올 수 없습니다.
    </div>

    <div class="mt-3">
      <router-link to="/products" class="btn btn-outline-secondary">
        목록으로 돌아가기
      </router-link>
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
} = useProductDetail('saving')
</script>

<style scoped>
.table th {
  white-space: nowrap;
}
</style>
