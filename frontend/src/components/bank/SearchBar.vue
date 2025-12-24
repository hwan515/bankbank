<template>
  <form class="bar" @submit.prevent="submit">
    <input class="input" v-model="q" placeholder="예: 강남역 카페" />
    <button class="ui-btn ui-btn-primary" type="submit">검색</button>
  </form>
</template>

<script setup>
import { ref } from "vue";
import { useMapStore } from "@/stores/maps";

const q = ref("");
const mapStore = useMapStore();

const submit = () => {
  mapStore.search(q.value);
};
</script>

<style scoped>
.bar { display: flex; gap: 8px; margin-bottom: 10px; }
.input {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: var(--surface);
}
.input:focus {
  border-color: rgba(27, 95, 122, 0.5);
  box-shadow: 0 0 0 0.2rem rgba(27, 95, 122, 0.15);
}
</style>
