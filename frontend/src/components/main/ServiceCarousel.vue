<script setup>
import { ref } from 'vue';
import { RouterLink } from 'vue-router';

const slides = ref([
  {
    id: 1,
    title: "현명한 자산 관리의 시작",
    description: "한눈에 비교하는 예적금 금리 비교 서비스",
    image: "https://placehold.co/1200x400/EEE/31343C?text=Banner+1",
    action: "금리 비교하기",
    route: "deposit-list"
  },
  {
    id: 2,
    title: "AI 기반 카드 추천",
    description: "어떤 카드가 당신에게 적합한지 추천받으세요.",
    image: "https://placehold.co/1200x400/EEE/31343C?text=Banner+2",
    action: "추천 받기",
    route: "card-recommendation"
  },
  {
    id: 3,
    title: "내 주변 은행 찾기",
    description: "가까운 은행 지점과 경로를 안내해드립니다.",
    image: "https://placehold.co/1200x400/EEE/31343C?text=Banner+3",
    action: "지도 보기",
    route: "bank-map"
  }
]);
</script>

<template>
  <div id="serviceCarousel" class="carousel slide" data-bs-ride="carousel">
    <div class="carousel-indicators">
      <button 
        v-for="(slide, index) in slides" 
        :key="slide.id"
        type="button" 
        data-bs-target="#serviceCarousel" 
        :data-bs-slide-to="index" 
        :class="{ active: index === 0 }"
        :aria-current="index === 0 ? 'true' : undefined"
        :aria-label="`Slide ${index + 1}`">
      </button>
    </div>

    <div class="carousel-inner rounded-3 shadow-sm">
      <div 
        v-for="(slide, index) in slides" 
        :key="slide.id" 
        class="carousel-item" 
        :class="{ active: index === 0 }"
        data-bs-interval="5000"> <img :src="slide.image" class="d-block w-100 carousel-img" :alt="slide.title">
        
        <div class="carousel-caption d-none d-md-block bg-dark bg-opacity-50 rounded p-3">
          <h5 class="fw-bold">{{ slide.title }}</h5>
          <p>{{ slide.description }}</p>
          <RouterLink :to="{ name: slide.route }" class="btn btn-light btn-sm text-primary fw-bold">
            {{ slide.action }}
          </RouterLink>
        </div>
      </div>
    </div>

    <button class="carousel-control-prev" type="button" data-bs-target="#serviceCarousel" data-bs-slide="prev">
      <span class="carousel-control-prev-icon" aria-hidden="true"></span>
      <span class="visually-hidden">Previous</span>
    </button>
    <button class="carousel-control-next" type="button" data-bs-target="#serviceCarousel" data-bs-slide="next">
      <span class="carousel-control-next-icon" aria-hidden="true"></span>
      <span class="visually-hidden">Next</span>
    </button>
  </div>
</template>

<style scoped>
.carousel-img {
  height: 400px;
  object-fit: cover; /* 이미지가 찌그러지지 않도록 처리 */
  filter: brightness(0.9); /* 텍스트 가독성을 위해 살짝 어둡게 */
}
</style>