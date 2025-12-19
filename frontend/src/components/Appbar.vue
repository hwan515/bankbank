<template>
    <v-app-bar :elevation="2">
        <template v-slot:prepend>
            <v-app-bar-nav-icon></v-app-bar-nav-icon>
        </template>

        <v-app-bar-title>Application Bar</v-app-bar-title>
        <v-btn icon>
          <v-icon>mdi-magnify</v-icon>
        </v-btn>

        <v-btn icon>
          <v-icon>mdi-heart</v-icon>
        </v-btn>

        <v-btn v-if="!accountStore.isLogin" icon to="/account/login">
          <v-icon>mdi-account</v-icon>
        </v-btn>

        <v-btn v-else @click="logout">
          <v-icon>mdi-logout</v-icon>
        </v-btn>

        <v-btn icon>
          <v-icon>mdi-dots-vertical</v-icon>
        </v-btn>
    </v-app-bar>
</template>

<script setup>
import { useAccountStore } from '@/stores/account';
import { useRouter } from 'vue-router'
const accountStore = useAccountStore()
const router = useRouter()
const logout =  async () => {
  await accountStore.logout()
  router.push('/')
}

console.log(accountStore.isLogin)
</script>

<style scoped>

</style>