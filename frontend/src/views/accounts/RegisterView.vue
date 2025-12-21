<template>
  <div class="signup-page d-flex justify-content-center align-items-center min-vh-100">
    <div class="card shadow-sm border-0 signup-card">
      <div class="card-body p-4 p-md-5">
        <h2 class="fw-bold mb-1">회원가입</h2>
        <p class="text-body-secondary mb-4">정보를 입력해 계정을 만들어주세요.</p>

        <form @submit.prevent="register">
          <!-- 이름 -->
          <div class="form-floating mb-3">
            <input type="text" class="form-control" id="name" placeholder="홍길동" v-model.trim="name"/>
            <label for="name">이름</label>
          </div>

          <!-- 나이 -->
          <div class="form-floating mb-3">
            <input type="text" class="form-control" id="age" placeholder="20" v-model.trim="age"/>
            <label for="age">나이</label>
          </div>

          <!-- 이메일 -->
          <div class="form-floating mb-3">
            <input type="email" class="form-control" id="email" placeholder="name@example.com" v-model.trim="email"/>
            <label for="email">이메일</label>
          </div>
          

          <!-- 아이디(Username) -->
          <div class="input-group mb-3">
            <span class="input-group-text">@</span>
            <div class="form-floating flex-grow-1">
              <input
                type="text"
                class="form-control"
                id="username"
                placeholder="username"
                v-model.trim="username"
              />
              <label for="username">아이디</label>
            </div>
          </div>

          <!-- 비밀번호 -->
          <div class="form-floating mb-3">
            <input type="password" class="form-control" id="password" placeholder="Password" v-model.trim="password1"/>
            <label for="password">비밀번호</label>
            <div class="form-text">8자 이상, 영문/숫자 조합을 권장해요.</div>
          </div>

          <!-- 비밀번호 확인 -->
          <div class="form-floating mb-3">
            <input type="password" class="form-control" id="password2" placeholder="Password 확인" v-model.trim="password2"/>
            <label for="password2">비밀번호 확인</label>
          </div>

          <!-- 약관 동의 -->
          <div class="d-flex justify-content-between align-items-center mb-3">
            <div class="form-check">
              <input class="form-check-input" type="checkbox" id="agree" v-model="terms"/>
              <label class="form-check-label" for="agree">
                (필수) 이용약관 / 개인정보 처리방침 동의
              </label>
            </div>
          </div>

          <!-- 가입 버튼 -->
          <button class="btn btn-primary w-100 py-2" type="submit">
            가입하기
          </button>

          <div class="text-center mt-3">
            <span class="text-body-secondary">이미 계정이 있나요?</span>
            <a href="#" class="ms-1 link-primary text-decoration-none">로그인</a>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAccountStore } from '@/stores/account'
import {ref} from 'vue'
import { useRouter } from 'vue-router'

    const username = ref(null)
    const email = ref(null)
    const password1 = ref(null)
    const password2 = ref(null)
    const name = ref(null)
    const terms = ref(false)

    const accountStore = useAccountStore()

    const router = useRouter()
    const register = () => {
        const payload = {
            username : username.value,
            password1: password1.value,
            password2: password2.value,
            // name : name.value,
            age : age.value,
            terms: terms.value,
            email : email.value, 
        }

        const success = accountStore.register(payload)

        if (success) {
            router.push("/")
        } else {

        }
    }
</script>

<style scoped>
.signup-page {
  background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
}

.signup-card {
  width: 100%;
  max-width: 520px;
  border-radius: 18px;
}

.form-control:focus {
  box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.15);
}

.input-group .form-floating > .form-control {
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
}
</style>


<script setup>

</script>

<style scoped>

</style>