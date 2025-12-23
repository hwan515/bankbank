<template>
  <div class="card-mini" @click="$emit('click')">
    <div class="card-img-wrap">
      <img
        :src="card.image_url"
        :alt="card.name"
        class="card-img"
        @error="handleImageError"
      />
    </div>
    <div class="card-info">
      <div class="card-company">{{ card.company }}</div>
      <div class="card-name">{{ card.name }}</div>
      <div v-if="score !== null" class="card-score">
        매칭 {{ Math.round(score * 100) }}%
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  card: {
    type: Object,
    required: true
  },
  score: {
    type: Number,
    default: null
  }
})

defineEmits(['click'])

function handleImageError(e) {
  e.target.src = 'https://via.placeholder.com/120x80?text=Card'
}
</script>

<style scoped>
.card-mini {
  display: flex;
  gap: 12px;
  padding: 12px;
  border: 1px solid #efefef;
  border-radius: 12px;
  background: #fff;
  cursor: pointer;
  transition: all 0.15s ease;
}

.card-mini:hover {
  border-color: #ddd;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.card-img-wrap {
  flex-shrink: 0;
  width: 80px;
  height: 50px;
  background: #f8f9fa;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.card-img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.card-info {
  flex: 1;
  min-width: 0;
}

.card-company {
  font-size: 11px;
  color: #888;
  margin-bottom: 2px;
}

.card-name {
  font-size: 13px;
  font-weight: 600;
  color: #111;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-score {
  margin-top: 4px;
  font-size: 11px;
  color: #0f5132;
  font-weight: 600;
}
</style>
