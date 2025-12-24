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

<style>
  :root {
  --font-sans: 'Inter', 'Pretendard', -apple-system, BlinkMacSystemFont,
    'Apple SD Gothic Neo', 'Noto Sans KR', 'Segoe UI', Roboto, sans-serif;
}

html,
body {
  font-family: var(--font-sans);
  font-size: 14px;
  line-height: 1.6;
  letter-spacing: -0.1px;
  color: #111;
}

h1, h2, h3, h4, h5 {
  letter-spacing: -0.3px;
  font-weight: 700;
}


button,
input,
textarea,
select {
  font-family: inherit;
  letter-spacing: -0.1px;
}


.text-muted,
.help,
.subtitle {
  font-size: 12px;
  color: #777;
}


body {
  font-family: var(--font-sans) !important;
}

button {
  font-size: 13px;
  font-weight: 600;
}


:root {
  --font-sans: 'Inter', 'Pretendard', -apple-system, BlinkMacSystemFont,
    'Apple SD Gothic Neo', sans-serif;
}

body {
  font-family: var(--font-sans) !important;
  font-size: 14px;
  line-height: 1.6;
  letter-spacing: -0.1px;
  color: #111;
}


</style>