<template>
     <v-container class="fill-height d-flex align-center justify-center">
        <v-card class="mx-auto px-6 py-8" min-width="344" max-width="344">
            <v-card-title>로그인 하세요.</v-card-title>
            <v-form v-model="form" @submit.prevent="login">
                <v-text-field v-model="username" :readonly="loading" :rules="[required]" class="mb-2" label="username"
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
import {useRouter} from 'vue-router'

const form = ref(null);
const username = ref(null);
const password = ref(null);

const accountStore = useAccountStore();

const router = useRouter()
const login = () => {
    const payload = {
        username: username.value,
        password: password.value,
    }
    const success = accountStore.login(payload);

    if (success) {
        router.push('/')
    }
}
</script>

<style scoped></style>