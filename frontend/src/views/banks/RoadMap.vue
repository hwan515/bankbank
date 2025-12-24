<template>
  <div class="map-page">
    <BankMap/>
  </div>
</template>

<script setup>
import BankMap from '@/components/bank/BankMap.vue';


</script>


<style scoped>
.map-page {
  min-height: 100%;
  background:
    radial-gradient(900px 300px at 10% 0%, rgba(27, 95, 122, 0.10), transparent 60%),
    linear-gradient(180deg, var(--bg-alt) 0%, var(--bg) 100%);
  padding: 10px 0 24px;
}
</style>
