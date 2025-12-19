// Utilities
import { defineStore } from 'pinia'
import axios from 'axios'

export const useAccountStore = defineStore('account', () => {

    const login = async (payload) => {
        const res = await axios ({
            method:'get',
            url:'http://localhost:8000/api/v1/account',
            data: {
                username:payload.username,
                password:payload.password
            }
        })


    }

})
