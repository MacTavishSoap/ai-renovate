import axios from 'axios'
import { showToast } from 'vant'

const http = axios.create({
  baseURL: '/api',
  timeout: 120000,
})

// 请求拦截：自动加 token
http.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截：统一错误处理
http.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const msg = error.response?.data?.detail || error.message || '请求失败'
    showToast(msg)
    return Promise.reject(error)
  }
)

export default http
