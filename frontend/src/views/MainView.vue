<script setup>
import ServiceCarousel from '@/components/main/ServiceCarousel.vue'

const services = [
  { title: '예·적금 비교', desc: '금리/우대 조건을 빠르게 비교', to: { name: 'products' } },
  { title: '카드 추천', desc: '소비 패턴 기반 추천/혜택 비교', to: { name: 'cards' } },
  { title: '은행 지도', desc: '내 주변 은행 찾고 경로 보기', to: { name: 'bank-map' } },
  { title: '커뮤니티', desc: '정보 공유/후기/질문 답변', to: { name: 'community' } },
]
</script>

<template>
  <div class="container py-4 main">
    <section class="mb-4">
      <ServiceCarousel />
    </section>

    <section class="mb-3">
      <div class="head">
        <h3 class="title">주요 금융 서비스</h3>
        <p class="sub">자주 쓰는 기능을 빠르게 이용하세요.</p>
      </div>
    </section>

    <section class="grid mb-4">
      <RouterLink v-for="s in services" :key="s.title" :to="s.to" class="card">
        <div class="card-title">{{ s.title }}</div>
        <div class="card-desc">{{ s.desc }}</div>
        <div class="card-arrow">→</div>
      </RouterLink>
    </section>
  </div>
</template>

<style scoped>
.main { max-width: 1080px; }

.head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
}

.title {
  margin: 0;
  font-weight: 900;
  letter-spacing: -0.3px;
  color: #111;
}

.sub {
  margin: 0;
  font-size: 13px;
  color: #777;
}

.grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.card {
  text-decoration: none;
  color: inherit;
  background: #fff;
  border: 1px solid #efefef;
  border-radius: 14px;
  padding: 14px;
  position: relative;
  transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
  box-shadow: 0 1px 2px rgba(0,0,0,0.08), 0 6px 14px rgba(0,0,0,0.06);
}

.card:hover {
  transform: translateY(-2px);
  border-color: #e3e3e3;
  box-shadow: 0 2px 6px rgba(0,0,0,0.10), 0 12px 26px rgba(0,0,0,0.08);
}

.card-title {
  font-weight: 900;
  font-size: 14px;
  color: #111;
  margin-bottom: 8px;
}

.card-desc {
  font-size: 13px;
  color: #666;
  line-height: 1.45;
  padding-right: 18px;
}

.card-arrow {
  position: absolute;
  right: 14px;
  bottom: 12px;
  color: #999;
  font-weight: 800;
}

@media (max-width: 992px) {
  .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 576px) {
  .head { flex-direction: column; align-items: flex-start; }
  .grid { grid-template-columns: 1fr; }
}
</style>
