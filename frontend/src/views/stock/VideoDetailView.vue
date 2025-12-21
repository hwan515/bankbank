<template>
  <div class="container py-5">
    <h3>Video Detail</h3>
    <p>videoId: {{ route.params.id }}</p>

    <div class="ratio ratio-16x9">
      <iframe
        :src="`https://www.youtube.com/embed/${route.params.id}`"
        title="YouTube player"
        allowfullscreen
      ></iframe>
    </div>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
const route = useRoute()
</script>


<style lang="scss" scoped>

</style>