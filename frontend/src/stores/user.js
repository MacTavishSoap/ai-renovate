import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, sendCode as sendCodeApi } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userId = ref(Number(localStorage.getItem('userId')) || null)
  const credits = ref(Number(localStorage.getItem('credits')) || 0)

  const isLoggedIn = computed(() => !!token.value)

  async function sendCode(phone) {
    return sendCodeApi(phone)
  }

  async function login(phone, code) {
    const res = await loginApi(phone, code)
    token.value = res.token
    userId.value = res.user_id
    credits.value = res.credits
    localStorage.setItem('token', res.token)
    localStorage.setItem('userId', res.user_id)
    localStorage.setItem('credits', res.credits)
  }

  function logout() {
    token.value = ''
    userId.value = null
    credits.value = 0
    localStorage.removeItem('token')
    localStorage.removeItem('userId')
    localStorage.removeItem('credits')
  }

  return { token, userId, credits, isLoggedIn, sendCode, login, logout }
})
