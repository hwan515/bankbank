<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'

const slides = ref([
  {
    id: 1,
    title: "현명한 자산 관리의 시작",
    description: "한눈에 비교하는 예적금 금리 비교 서비스",
    image: "https://placehold.co/1200x400/EEE/31343C?text=Banner+1",
    action: "금리 비교하기",
    route: "products"
  },
  {
    id: 2,
    title: "AI 기반 카드 추천",
    description: "어떤 카드가 당신에게 적합한지 추천받으세요.",
    image: "https://placehold.co/1200x400/EEE/31343C?text=Banner+2",
    action: "추천 받기",
    route: "cards",
    query: { tab: 'recommend' }
  },
  {
    id: 3,
    title: "내 주변 은행 찾기",
    description: "가까운 은행 지점과 경로를 안내해드립니다.",
    image: "https://placehold.co/1200x400/EEE/31343C?text=Banner+3",
    action: "지도 보기",
    route: "bank-map"
  }
])
</script>

<template>
  <div id="serviceCarousel" class="carousel slide hero" data-bs-ride="carousel">
    <div class="carousel-indicators">
      <button
        v-for="(slide, index) in slides"
        :key="slide.id"
        type="button"
        data-bs-target="#serviceCarousel"
        :data-bs-slide-to="index"
        :class="{ active: index === 0 }"
        :aria-current="index === 0 ? 'true' : undefined"
        :aria-label="`Slide ${index + 1}`"
      />
    </div>

    <div class="carousel-inner hero-inner">
      <div
        v-for="(slide, index) in slides"
        :key="slide.id"
        class="carousel-item"
        :class="{ active: index === 0 }"
        data-bs-interval="5000"
      >
        <img :src="slide.image" class="d-block w-100 hero-img" :alt="slide.title" />

        <!-- ✅ 미니멀 캡션 -->
        <div class="hero-overlay"></div>
        <div class="hero-caption">
          <div class="hero-title">{{ slide.title }}</div>
          <div class="hero-desc">{{ slide.description }}</div>
          <RouterLink :to="{ name: slide.route, query: slide.query }" class="hero-btn">
            {{ slide.action }} →
          </RouterLink>
        </div>
      </div>
    </div>

    <button class="carousel-control-prev ctrl" type="button" data-bs-target="#serviceCarousel" data-bs-slide="prev">
      <span class="carousel-control-prev-icon" aria-hidden="true"></span>
      <span class="visually-hidden">Previous</span>
    </button>
    <button class="carousel-control-next ctrl" type="button" data-bs-target="#serviceCarousel" data-bs-slide="next">
      <span class="carousel-control-next-icon" aria-hidden="true"></span>
      <span class="visually-hidden">Next</span>
    </button>
  </div>
</template>

<style scoped>
.hero {
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid #efefef;
  background: #fff;
}

.hero-inner {
  border-radius: 16px;
}

.hero-img {
  height: 380px;
  object-fit: cover;
  filter: saturate(1.02);
}

.hero-overlay {
  position: absolute;
  inset: 0;
  /* 좌하단 가독성용 그라데이션 */
  background: linear-gradient(90deg, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0.15) 45%, rgba(0,0,0,0.00) 70%);
}

.hero-caption {
  position: absolute;
  left: 18px;
  bottom: 18px;
  max-width: 520px;
  color: #fff;
}

.hero-title {
  font-size: 22px;
  font-weight: 900;
  letter-spacing: -0.3px;
  margin-bottom: 6px;
}

.hero-desc {
  font-size: 14px;
  color: rgba(255,255,255,0.88);
  margin-bottom: 12px;
  line-height: 1.5;
}

.hero-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  text-decoration: none;
  background: rgba(255,255,255,0.92);
  color: #111;
  border: 1px solid rgba(255,255,255,0.35);
  border-radius: 12px;
  padding: 10px 12px;
  font-weight: 800;
  font-size: 13px;
}

.hero-btn:hover {
  background: #fff;
}

.ctrl {
  opacity: 0.75;
}
.ctrl:hover {
  opacity: 1;
}

@media (max-width: 576px) {
  .hero-img { height: 320px; }
  .hero-caption { right: 18px; }
  .hero-title { font-size: 18px; }
}
</style>
