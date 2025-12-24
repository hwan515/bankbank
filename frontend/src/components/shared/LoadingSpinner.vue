<template>
  <div class="text-center py-5">
    <div
      class="spinner-border ui-text-accent"
      :style="{ width: size, height: size }"
    ></div>
    <p v-if="message" class="mt-3 ui-sub">{{ message }}</p>
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
