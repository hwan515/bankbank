<<template>

    <!-- 로딩 모달 -->
  <v-dialog v-model="loading" persistent width="auto">
    <v-card class="pa-6 d-flex align-center" rounded="lg">
      <v-progress-circular indeterminate size="32" class="mr-4" />
      <div>처리 중...</div>
    </v-card>
  </v-dialog>
    <!--  회원가입 페이지 만들어야 됨.-->
    <v-card class="mx-auto" max-width="344" title="User Registration">
        <v-container>
            <v-text-field v-model="username" color="primary" label="username" variant="underlined"></v-text-field>

            <v-text-field v-model="email" color="primary" label="Email" variant="underlined"></v-text-field>

            <v-text-field v-model="password" color="primary" label="Password" placeholder="Enter your password"
                variant="underlined"></v-text-field>

            <v-text-field v-model="age" color="primary" label="age" placeholder="Enter your age"
                variant="underlined"></v-text-field>

            <v-checkbox v-model="terms" color="secondary" label="I agree to site terms and conditions"></v-checkbox>
        </v-container>

        <v-divider></v-divider>

        <v-card-actions>
            <v-spacer></v-spacer>

            <v-btn color="success" @click="register">
                Complete Registration

                <v-icon icon="mdi-chevron-right" end></v-icon>
            </v-btn>
        </v-card-actions>
    </v-card>
</template>

    <script setup>
    import { useAccountStore } from '@/stores/account'
    import { ref } from 'vue'
    import { useRouter } from 'vue-router'

    const loading = ref(false)

    const username = ref(null)
    const age = ref(null)
    const email = ref(null)
    const password = ref(null)
    const terms = ref(false)

    const router = useRouter()
    const accountStore = useAccountStore()

    const register = async () => {
        loading.value = true
        try {
            const payload = {
            username: username.value,
            age: age.value,
            email: email.value,
            password: password.value,
            terms: terms.value,
        }

        const success = await accountStore.register(payload)

        console.log(success)
        if (success) {
            router.push('/')
        } else {
            router.push('#')
        }
        }
     finally {
        loading.value = false
    }
}
</script>

    <style lang="scss" scoped></style>