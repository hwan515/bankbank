<template>
     <v-container class="fill-height d-flex align-center justify-center">
        <v-card class="mx-auto px-6 py-8" min-width="344" max-width="344">
            <v-card-title>로그인 하세요.</v-card-title>
            <v-form v-model="form" @submit.prevent="login">
                <v-text-field v-model="email" :readonly="loading" :rules="[required]" class="mb-2" label="Email"
                    clearable></v-text-field>

                <v-text-field v-model="password" :readonly="loading" :rules="[required]" label="Password" type="password"
                    placeholder="Enter your password" clearable></v-text-field>

                <br>

                <v-btn :disabled="!form" :loading="loading" color="success" size="large" type="submit" variant="elevated"
                    block>
                    Sign In
                </v-btn>
            </v-form>
        </v-card>
    </v-container>
</template>

<script setup>
import { useAccountStore } from '@/stores/account'
import { ref } from 'vue'

const form = ref(null)
const email = ref(null)
const password = ref(null)

const accountStore = useAccountStore()

const login = () => {
    accountStore.login(payload)
}
</script>

<style scoped></style>