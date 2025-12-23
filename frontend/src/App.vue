<script setup>
import { RouterView } from 'vue-router'
import TheNavbar from '@/components/main/Navbar.vue'
import ChatbotWidget from './components/chatbot/ChatbotWidget.vue';

</script>

<template>
  <TheNavbar />
  <RouterView />
  <ChatbotWidget/>
</template>

<style scoped></style>