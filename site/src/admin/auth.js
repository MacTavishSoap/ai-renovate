import { ref } from 'vue'

// 演示用的唯一账号。页面上不提示这组值,也不能在界面里修改。
const NAME = '总管'
const PASSWORD = '888888'
const KEY = 'fortune-admin'

export const accountName = NAME
export const accountPassword = PASSWORD
export const authed = ref(sessionStorage.getItem(KEY) === '1')

export function login(name, password) {
  if (name !== NAME || password !== PASSWORD) return false
  sessionStorage.setItem(KEY, '1')
  authed.value = true
  return true
}

export function logout() {
  sessionStorage.removeItem(KEY)
  authed.value = false
}
