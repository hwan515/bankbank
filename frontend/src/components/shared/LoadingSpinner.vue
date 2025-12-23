<template>
  <div class="text-center py-5">
    <div
      class="spinner-border text-primary"
      :style="{ width: size, height: size }"
    ></div>
    <p v-if="message" class="mt-3 text-muted">{{ message }}</p>
  </div>
</template>

<script setup>
defineProps({
  message: {
    type: String,
    default: ''
  },
  size: {
    type: String,
    default: '3rem'
  }
})
</script>
