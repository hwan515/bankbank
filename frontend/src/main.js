import { createApp } from 'vue'
import { createPinia } from 'pinia'
import 'bootstrap/dist/css/bootstrap.min.css'
import './assets/theme.css'
import './assets/ui.css'

import App from './App.vue'
import router from './router'
import 'bootstrap'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// 앱 마운트 전 인증 상태 초기화
import { useUserStore } from './stores/user'
const userStore = useUserStore()
userStore.initAuth()

app.mount('#app')
