<script setup>
import { RouterView } from 'vue-router'
import TheNavbar from '@/components/main/Navbar.vue'
import ChatbotWidget from './components/chatbot/ChatbotWidget.vue'
import ToastHost from '@/components/ui/ToastHost.vue'

</script>

<template>
  <TheNavbar />
  <RouterView />
  <ChatbotWidget />
  <ToastHost />
</template>

<style scoped></style>
