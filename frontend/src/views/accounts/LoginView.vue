<template>
  <div class="auth-page">
    <form class="auth-card ui-card" @submit.prevent="login">
      <div class="head">
        <div class="ui-badge">Bankbook</div>
        <h1 class="title serif-title">로그인</h1>
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

      <button class="ui-btn ui-btn-primary w100 mt-3" type="submit" :disabled="loading">
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
    const ok = await accountStore.login({
      username: username.value,
      password: password.value,
      remember: rememberMe.value, // store에서 쓸지 말지는 선택
    })
    if (ok) {
      router.push({ name: 'main' })
    } else {
      errorMsg.value = '로그인에 실패했어요. 정보를 확인해 주세요.'
    }
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
    radial-gradient(900px 300px at 50% 0%, rgba(27, 95, 122, 0.12), transparent 60%),
    linear-gradient(180deg, var(--bg-alt) 0%, var(--bg) 100%);
}

.auth-card {
  width: 100%;
  max-width: 360px;
  border-radius: var(--radius-lg);
  padding: 22px;
}

.head {
  margin-bottom: 14px;
}


.title {
  margin: 10px 0 6px;
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.3px;
  color: var(--ink);
}

.sub {
  margin: 0;
  font-size: 13px;
  color: var(--muted);
  line-height: 1.5;
}

.field {
  display: grid;
  gap: 6px;
  margin-top: 10px;
}

.label {
  font-size: 12px;
  font-weight: 700;
  color: var(--ink);
}

.input {
  height: 42px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  background: var(--surface);
  padding: 0 12px;
  font-size: 14px;
  outline: none;
}

.input:focus {
  border-color: rgba(27, 95, 122, 0.5);
  box-shadow: 0 0 0 0.2rem rgba(27, 95, 122, 0.15);
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
  color: var(--ink-soft);
  user-select: none;
}

.check input {
  width: 16px;
  height: 16px;
}

.link {
  font-size: 13px;
  color: var(--ink);
  font-weight: 700;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
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
  color: var(--muted);
}
</style>
