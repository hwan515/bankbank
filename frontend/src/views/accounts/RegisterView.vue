<template>
  <div class="auth-page">
    <div class="auth-card ui-card">
      <div class="head">
        <div class="ui-badge">Bankbook</div>
        <h2 class="title serif-title">회원가입</h2>
        <p class="sub">정보를 입력해 계정을 만들어주세요.</p>
      </div>

      <form @submit.prevent="register" class="form">
        <!-- 이름 -->
        <div class="field">
          <label class="label" for="name">이름</label>
          <input
            id="name"
            type="text"
            class="input"
            placeholder="홍길동"
            v-model.trim="name"
          />
        </div>

        <!-- 나이 -->
        <div class="field">
          <label class="label" for="age">나이</label>
          <input
            id="age"
            type="number"
            inputmode="numeric"
            class="input"
            placeholder="20"
            v-model.number="age"
          />
        </div>

        <!-- 이메일 -->
        <div class="field">
          <label class="label" for="email">이메일</label>
          <input
            id="email"
            type="email"
            class="input"
            placeholder="name@example.com"
            v-model.trim="email"
          />
        </div>

        <!-- 아이디 -->
        <div class="field">
          <label class="label" for="username">아이디</label>
          <div class="input-prefix">
            <span class="prefix">@</span>
            <input
              id="username"
              type="text"
              class="input"
              placeholder="username"
              v-model.trim="username"
            />
          </div>
        </div>

        <!-- 비밀번호 -->
        <div class="field">
          <label class="label" for="password1">비밀번호</label>
          <input
            id="password1"
            type="password"
            class="input"
            placeholder="비밀번호"
            v-model.trim="password1"
          />
          <div class="hint">8자 이상, 영문/숫자 조합을 권장해요.</div>
        </div>

        <!-- 비밀번호 확인 -->
        <div class="field">
          <label class="label" for="password2">비밀번호 확인</label>
          <input
            id="password2"
            type="password"
            class="input"
            placeholder="비밀번호 확인"
            v-model.trim="password2"
          />
        </div>

        <!-- 약관 -->
        <div class="terms">
          <label class="check">
            <input type="checkbox" v-model="terms" />
            <span>(필수) 이용약관 / 개인정보 처리방침 동의</span>
          </label>
        </div>

        <button class="ui-btn ui-btn-primary w100" type="submit" :disabled="loading">
          {{ loading ? '가입 중...' : '가입하기' }}
        </button>

        <div class="foot">
          <span>이미 계정이 있나요?</span>
          <RouterLink :to="{ name: 'login' }" class="link">로그인</RouterLink>
        </div>

        <div v-if="errorMsg" class="error">{{ errorMsg }}</div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useAccountStore } from '@/stores/account'

const router = useRouter()
const accountStore = useAccountStore()

const username = ref('')
const email = ref('')
const password1 = ref('')
const password2 = ref('')
const name = ref('')
const age = ref(null)
const terms = ref(false)

const loading = ref(false)
const errorMsg = ref('')

const register = async () => {
  errorMsg.value = ''

  if (!terms.value) {
    errorMsg.value = '약관에 동의해 주세요.'
    return
  }
  if (password1.value !== password2.value) {
    errorMsg.value = '비밀번호가 일치하지 않아요.'
    return
  }

  const payload = {
    username: username.value,
    password1: password1.value,
    password2: password2.value,
    email: email.value,
    age: age.value,
    // name은 백엔드에서 필드가 없으면 보내지 마 (필요하면 User 모델에 first_name 등으로 저장)
  }

  loading.value = true
  try {
    await accountStore.register(payload) // ✅ register가 async라고 가정
    router.push({ name: 'main' })
  } catch (e) {
    console.error(e)
    errorMsg.value = '회원가입에 실패했어요. 입력값을 확인해 주세요.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* 페이지 배경: 미니멀 + 은은 */
.auth-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
  background:
    radial-gradient(900px 300px at 50% 0%, rgba(27, 95, 122, 0.12), transparent 60%),
    linear-gradient(180deg, var(--bg-alt) 0%, var(--bg) 100%);
}

/* 카드: 우리 컨셉과 동일 */
.auth-card {
  width: 100%;
  max-width: 520px;
  border-radius: var(--radius-lg);
  padding: 22px;
}

/* 헤더 */
.head {
  margin-bottom: 16px;
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

/* 폼 */
.form {
  display: grid;
  gap: 12px;
}

.field {
  display: grid;
  gap: 6px;
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

/* @ prefix */
.input-prefix {
  display: grid;
  grid-template-columns: 40px 1fr;
  align-items: center;
  gap: 8px;
}

.prefix {
  height: 42px;
  display: grid;
  place-items: center;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  background: var(--bg-alt);
  color: var(--ink-soft);
  font-weight: 700;
}

.hint {
  font-size: 12px;
  color: var(--muted);
}

/* 약관 */
.terms {
  margin-top: 2px;
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

/* 버튼 */

/* 하단 */
.foot {
  display: flex;
  justify-content: center;
  gap: 8px;
  font-size: 13px;
  color: var(--muted);
}

.link {
  color: var(--ink);
  font-weight: 700;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.error {
  margin-top: 2px;
  font-size: 13px;
  color: #c0392b;
}
</style>
