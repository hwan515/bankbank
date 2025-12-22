<template>
  <div class="auth-page">
    <form class="auth-card" @submit.prevent="login">
      <div class="head">
        <div class="badge">Bankbook</div>
        <h1 class="title">로그인</h1>
        <p class="sub">아이디와 비밀번호를 입력해 주세요.</p>
      </div>

      <div class="field">
        <label class="label" for="username">아이디</label>
        <input
          id="username"
          type="text"
          class="input"
          placeholder="username"
          v-model.trim="username"
          autocomplete="username"
        />
      </div>

      <div class="field">
        <label class="label" for="password">비밀번호</label>
        <input
          id="password"
          type="password"
          class="input"
          placeholder="Password"
          v-model.trim="password"
          autocomplete="current-password"
        />
      </div>

      <div class="rowline">
        <label class="check">
          <input type="checkbox" v-model="rememberMe" />
          <span>Remember me</span>
        </label>

        <RouterLink :to="{ name: 'signup' }" class="link">회원가입</RouterLink>
      </div>

      <button class="btn-solid" type="submit" :disabled="loading">
        {{ loading ? '로그인 중...' : 'Sign in' }}
      </button>

      <div v-if="errorMsg" class="error">{{ errorMsg }}</div>

      <div class="foot">© 2017–2025</div>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useAccountStore } from '@/stores/account'

const username = ref('')
const password = ref('')
const rememberMe = ref(false)

const loading = ref(false)
const errorMsg = ref('')

const accountStore = useAccountStore()
const router = useRouter()

const login = async () => {
  errorMsg.value = ''

  if (!username.value || !password.value) {
    errorMsg.value = '아이디와 비밀번호를 입력해 주세요.'
    return
  }

  loading.value = true
  try {
    await accountStore.login({
      username: username.value,
      password: password.value,
      remember: rememberMe.value, // store에서 쓸지 말지는 선택
    })
    router.push({ name: 'main' })
  } catch (e) {
    console.error(e)
    errorMsg.value = '로그인에 실패했어요. 정보를 확인해 주세요.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
  background:
    radial-gradient(900px 300px at 50% 0%, rgba(0,0,0,0.06), transparent 60%),
    linear-gradient(180deg, #fafafa 0%, #ffffff 100%);
}

.auth-card {
  width: 100%;
  max-width: 360px;
  background: #fff;
  border: 1px solid #efefef;
  border-radius: 18px;
  padding: 22px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.08), 0 10px 24px rgba(0,0,0,0.06);
}

.head {
  margin-bottom: 14px;
}

.badge {
  display: inline-block;
  font-size: 12px;
  color: #444;
  background: #f6f6f6;
  border: 1px solid #ededed;
  padding: 6px 10px;
  border-radius: 999px;
}

.title {
  margin: 10px 0 6px;
  font-size: 22px;
  font-weight: 900;
  letter-spacing: -0.3px;
  color: #111;
}

.sub {
  margin: 0;
  font-size: 13px;
  color: #777;
  line-height: 1.5;
}

.field {
  display: grid;
  gap: 6px;
  margin-top: 10px;
}

.label {
  font-size: 12px;
  font-weight: 800;
  color: #111;
}

.input {
  height: 42px;
  border-radius: 12px;
  border: 1px solid #eaeaea;
  background: #fff;
  padding: 0 12px;
  font-size: 14px;
  outline: none;
}

.input:focus {
  border-color: #d8d8d8;
  box-shadow: 0 0 0 0.2rem rgba(0, 0, 0, 0.06);
}

.rowline {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.check {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #444;
  user-select: none;
}

.check input {
  width: 16px;
  height: 16px;
}

.link {
  font-size: 13px;
  color: #111;
  font-weight: 900;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.btn-solid {
  width: 100%;
  height: 44px;
  border-radius: 14px;
  border: 1px solid #111;
  background: #111;
  color: #fff;
  font-weight: 900;
  font-size: 14px;
  cursor: pointer;
  margin-top: 14px;
}

.btn-solid:hover {
  background: #000;
}

.btn-solid:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error {
  margin-top: 10px;
  font-size: 13px;
  color: #c0392b;
}

.foot {
  margin-top: 18px;
  text-align: center;
  font-size: 12px;
  color: #888;
}
</style>
