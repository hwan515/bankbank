import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', () => {
  const isAuthenticated = ref(false)

  function logout() {
    isAuthenticated.value = false
  }

  function login() {
    isAuthenticated.value = true
  }

  return { isAuthenticated, login, logout }
})