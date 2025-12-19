// Utilities
import { defineStore } from 'pinia'
import axios from 'axios'
import {ref} from 'vue'
import { ca } from 'vuetify/locale'
export const useAccountStore = defineStore('account', () => {
    
    //  토큰 설정. 
    const token = ref(null)

    const isLogin = computed(() => !!token.value)
    // # 로그인 
    const login = async (payload) => {
        try {
            const res= await axios.post(
            'http://localhost:8000/accounts/login',
             {
                username:payload.username,
                password:payload.password
            }
            
        )
            token.value = res.data.key

            // axios 전역 헤더 설정. 
            axios.defaults.headers.common['Authorization'] = `Token ${token.value}`
            return true
        } catch(err) {
            console.error('로그인 실패', err)
            return false
        }
    }

    const logout = async() => {
        try {
            await axios.post(
                'http://localhost:8000/accounts/logout',
            )
        } catch(e) {

        } finally {
            token.value = null
            delete axios.defaults.headers.common.Authorization
            localStorage.removeItem('token')
        }
    }
    return  {
        login, token, isLogin, logout
    }
})
