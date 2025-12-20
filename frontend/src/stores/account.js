// Utilities
import { defineStore } from 'pinia'
import axios from 'axios'
import {ref, computed} from 'vue'
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

    const register = async(payload) => {
        try {
            await axios.post(
                'http://localhost:8000/accounts/signup/',
            {
                username:payload.username,
                age:payload.age,
                password1:payload.password1,
                password2:payload.password2,
                email:payload.email,
                terms:payload.terms,
            }
        )
            return true
        } catch(error) {
            console.log(error); 
            return false
        }
    }

    return  {
        login, token, isLogin, logout, register
    }
})
