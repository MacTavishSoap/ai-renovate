import http from './http'

export function sendCode(phone) {
  return http.post('/send-code', { phone })
}

export function login(phone, code) {
  return http.post('/login', { phone, code })
}
