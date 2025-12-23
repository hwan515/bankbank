<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'

const slides = ref([
  {
    id: 1,
    eyebrow: "예적금 비교",
    title: "현명한 자산 관리의 첫 페이지",
    description: "금리, 우대 조건, 기간을 한 화면에서 정리해서 비교하세요.",
    action: "금리 비교하기",
    route: "products",
    tone: "marine"
  },
  {
    id: 2,
    eyebrow: "카드 추천",
    title: "라이프스타일에 맞춘 카드 큐레이션",
    description: "검색 한 번으로 필요한 혜택만 콕 집어 추천해 드려요.",
    action: "추천 받기",
    route: "cards",
    query: { tab: 'recommend' },
    tone: "slate"
  },
  {
    id: 3,
    eyebrow: "은행 지도",
    title: "가까운 은행을 빠르게 찾아서 이동",
    description: "필요할 때 가까운 지점을 찾고 경로를 확인하세요.",
    action: "지도 보기",
    route: "bank-map",
    tone: "sand"
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
        <div class="hero-shell" :class="`tone-${slide.tone}`">
          <div class="hero-content reveal-up">
            <div class="hero-eyebrow">{{ slide.eyebrow }}</div>
            <div class="hero-title serif-title">{{ slide.title }}</div>
            <div class="hero-desc">{{ slide.description }}</div>
            <RouterLink :to="{ name: slide.route, query: slide.query }" class="hero-btn">
              {{ slide.action }} →
            </RouterLink>
          </div>
          <div class="hero-visual">
            <div class="hero-orb"></div>
            <div class="hero-stack">
              <div class="hero-tile tile-lg"></div>
              <div class="hero-tile tile-md"></div>
              <div class="hero-tile tile-sm"></div>
            </div>
            <div class="hero-line"></div>
          </div>
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
  border-radius: var(--radius-lg);
  overflow: hidden;
  border: 1px solid var(--border);
  background: var(--surface);
  box-shadow: var(--shadow-2);
}

.hero-inner {
  border-radius: var(--radius-lg);
}

.hero-shell {
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(0, 0.9fr);
  align-items: center;
  min-height: 360px;
  padding: 34px 36px;
  position: relative;
}

.tone-marine {
  background:
    radial-gradient(400px 300px at 90% 15%, rgba(27, 95, 122, 0.25), transparent 70%),
    linear-gradient(120deg, #fbf7f2 0%, #f2eee7 45%, #e9f0f3 100%);
}

.tone-slate {
  background:
    radial-gradient(380px 280px at 95% 20%, rgba(18, 72, 95, 0.28), transparent 70%),
    linear-gradient(130deg, #f8f6f2 0%, #eef1f4 55%, #e8edf1 100%);
}

.tone-sand {
  background:
    radial-gradient(380px 280px at 88% 20%, rgba(201, 139, 74, 0.28), transparent 70%),
    linear-gradient(130deg, #fbf7f1 0%, #f3efe7 55%, #efe8dc 100%);
}

.hero-content {
  max-width: 520px;
  color: var(--ink);
}

.hero-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--accent);
  margin-bottom: 10px;
}

.hero-title {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 10px;
}

.hero-desc {
  font-size: 14px;
  color: var(--ink-soft);
  margin-bottom: 18px;
  line-height: 1.5;
}

.hero-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  text-decoration: none;
  background: var(--accent);
  color: #fff;
  border: 1px solid var(--accent);
  border-radius: 999px;
  padding: 10px 16px;
  font-weight: 600;
  font-size: 13px;
  box-shadow: 0 10px 20px rgba(27, 95, 122, 0.2);
}

.hero-btn:hover {
  background: var(--accent-strong);
}

.hero-visual {
  position: relative;
  display: grid;
  place-items: center;
  min-height: 260px;
}

.hero-orb {
  position: absolute;
  width: 190px;
  height: 190px;
  border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.9), rgba(27, 95, 122, 0.2));
  filter: blur(0.5px);
  animation: soft-glow 3s ease-in-out infinite alternate;
}

.hero-stack {
  display: grid;
  gap: 14px;
  z-index: 1;
}

.hero-tile {
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.6);
  background: rgba(255, 255, 255, 0.85);
  box-shadow: 0 14px 30px rgba(16, 24, 40, 0.18);
  backdrop-filter: blur(8px);
}

.tile-lg { width: 200px; height: 90px; }
.tile-md { width: 180px; height: 70px; margin-left: 18px; }
.tile-sm { width: 160px; height: 56px; margin-left: 36px; }

.hero-line {
  position: absolute;
  width: 180px;
  height: 2px;
  background: linear-gradient(90deg, rgba(27, 95, 122, 0.6), rgba(27, 95, 122, 0.05));
  top: 24px;
  right: 10px;
}

.ctrl {
  opacity: 0.75;
}
.ctrl:hover {
  opacity: 1;
}

@media (max-width: 576px) {
  .hero-shell { grid-template-columns: 1fr; gap: 18px; padding: 24px; }
  .hero-visual { min-height: 200px; }
  .hero-title { font-size: 22px; }
}
</style>
