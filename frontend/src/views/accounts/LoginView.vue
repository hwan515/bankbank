<template>
  <div class="d-flex justify-content-center align-items-center min-vh-100">
    <form class="text-center p-4 shadow rounded bg-white" style="width: 100%; max-width: 330px;" @submit.prevent="login">
      <h1 class="h3 mb-3 fw-normal">Please sign in</h1>

      <div class="form-floating mb-2">
        <input type="text" class="form-control" id="floatingInput" placeholder="Enter your username" v-model="username">
        <label for="floatingInput">username</label>
      </div>

      <div class="form-floating mb-2">
        <input type="password" class="form-control" id="floatingPassword" placeholder="Password" v-model="password">
        <label for="floatingPassword">Password</label>
      </div>

      <div class="form-check text-start my-3">
        <input class="form-check-input" type="checkbox" id="checkDefault">
        <label class="form-check-label" for="checkDefault">
          Remember me
        </label>
      </div>

      <button class="btn btn-primary w-100 py-2" type="submit" >Sign in</button>
      <p class="mt-5 mb-3 text-body-secondary">© 2017–2025</p>
    </form>
  </div>
</template>


<script setup>
import { useAccountStore } from '@/stores/account';
import { ref } from 'vue'
import { useRouter } from 'vue-router';

const username = ref(null)
const password = ref(null)

// AccountStore 선언
const accountStore = useAccountStore()

const router = useRouter()
// 
const login = () => {
    const payload = {
        username:username.value,
        password:password.value,
    }

    const success = accountStore.login(payload)

    if (success) {
        router.push('/')
    } else {
        // 현재 리다이렉트 
    }
}

</script>

<style scoped></style>