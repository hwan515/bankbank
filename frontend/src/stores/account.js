// Utilities
import { defineStore } from 'pinia'
import axios from 'axios'
import { ref, computed } from 'vue'
export const useAccountStore = defineStore('account', () => {
    const API_BASE_URL =
        import.meta.env.VITE_API_BASE_URL ||
        import.meta.env.VITE_API_URL ||
        'http://localhost:8000'
    const apiBaseUrl = API_BASE_URL.replace(/\/$/, '')
    const buildUrl = (path) => `${apiBaseUrl}${path}`

    //  토큰 설정. 
    const token = ref(localStorage.getItem("token")) // 새로고침 복원
    if (token.value) {
        axios.defaults.headers.common["Authorization"] = `Token ${token.value}`
    }
    const isLogin = computed(() => !!token.value)
    // # 로그인 
    const login = async (payload) => {
        try {
            const res = await axios.post(
                buildUrl('/accounts/login'),
                {
                    username: payload.username,
                    password: payload.password
                }

            )
            const authToken = res.data?.key
            if (!authToken) {
                throw new Error('로그인 응답에 토큰이 없습니다.')
            }
            token.value = authToken
            // axios 전역 헤더 설정. 
            localStorage.setItem("token", token.value)
            axios.defaults.headers.common['Authorization'] = `Token ${token.value}`
            return true
        } catch (err) {
            console.error('로그인 실패', err)
            return false
        }
    }

    const clearAuth = () => {
        token.value = null
        delete axios.defaults.headers.common.Authorization
        localStorage.removeItem('token')
    }

    const logout = async () => {
        try {
            await axios.post(
                buildUrl('/accounts/logout'),
            )
        } catch (e) {

        } finally {
            clearAuth()
        }
    }

    const register = async (payload) => {
        try {
            await axios.post(
                buildUrl('/accounts/signup/'),
                {
                    username: payload.username,
                    age: payload.age,
                    password1: payload.password1,
                    password2: payload.password2,
                    email: payload.email,
                    terms: payload.terms,
                }
            )
            return true
        } catch (error) {
            console.log(error);
            return false
        }
    }

    const loadProfile = async () => {
        try {
            const response = await axios.get(
                buildUrl('/api/accounts/profile')
            )
            console.log(response.data)
            return response.data; // 보통 data만 리턴하는 게 편함
        }
        catch (error) {
            console.log(error);
            return false
        }

    }

    const updateProfile = async (payload) => {
        try {
            // 백엔드에서 /accounts/profile/ PATCH로 greeting 수정하도록 만들기
            const res = await axios.patch(buildUrl('/api/accounts/profile/'), payload);
            return res.data; // 업데이트된 프로필 리턴해도 됨
        } catch (e) {
            console.error("프로필 수정 실패", e?.response?.data || e);
            return false;
        }
    };

    const addInformation = async (payload) => {
        try {
            const res = await axios.post(buildUrl('/api/accounts/information/'), payload)
            return res.data; 
        } catch(e) {
            console.error('정보 생성 실패', e?.response?.data || e);
            return false; 
        }
    }

    const load_information = async() => {
        try {
            const response = await axios.get(buildUrl('/api/accounts/information'))
            return response.data;    
        } catch(e) {
            console.error('정보 불러오기 실패', e?.response?.data || e)
            return false;
        }
        

    }

    if (typeof window !== 'undefined') {
        window.addEventListener('auth:logout', () => {
            clearAuth()
        })
    }

    return {
        login, token, isLogin, logout, clearAuth, register, loadProfile, updateProfile, addInformation, load_information
    }
})
