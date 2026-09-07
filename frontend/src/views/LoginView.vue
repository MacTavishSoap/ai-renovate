<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { showSuccessToast, showFailToast } from 'vant'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const form = reactive({
  phone: '',
  code: '',
})

const sending = ref(false)
const countdown = ref(0)

async function onSendCode() {
  if (!/^1\d{10}$/.test(form.phone)) {
    showFailToast('请输入正确的手机号')
    return
  }
  sending.value = true
  try {
    const res = await userStore.sendCode(form.phone)
    showSuccessToast(`验证码已发送（开发期：${res.dev_code}）`)
    countdown.value = 60
    const timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) clearInterval(timer)
    }, 1000)
  } catch {
    /* http 拦截器已处理 */
  } finally {
    sending.value = false
  }
}

async function onLogin() {
  if (!form.phone || !form.code) {
    showFailToast('请填写手机号和验证码')
    return
  }
  try {
    await userStore.login(form.phone, form.code)
    showSuccessToast('登录成功')
    const redirect = route.query.redirect || '/generate'
    router.replace(redirect)
  } catch {
    /* http 拦截器已处理 */
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-header">
      <h1 class="login-title">AI 家装</h1>
      <p class="login-subtitle">拍一张照片，看看装修后的样子</p>
    </div>

    <div class="login-form">
      <div class="field-group">
        <label for="phone" class="field-label">手机号</label>
        <input
          id="phone"
          v-model="form.phone"
          type="tel"
          class="field-input"
          placeholder="请输入手机号"
          maxlength="11"
          inputmode="numeric"
        />
      </div>

      <div class="field-group">
        <label for="code" class="field-label">验证码</label>
        <div class="code-row">
          <input
            id="code"
            v-model="form.code"
            type="text"
            class="field-input"
            placeholder="请输入验证码"
            maxlength="6"
            inputmode="numeric"
          />
          <button
            class="code-btn"
            :disabled="countdown > 0 || sending"
            @click="onSendCode"
          >
            <span v-if="sending">发送中</span>
            <span v-else-if="countdown > 0">{{ countdown }}s</span>
            <span v-else>获取验证码</span>
          </button>
        </div>
      </div>

      <button class="login-btn" :disabled="!form.phone || !form.code" @click="onLogin">
        登录
      </button>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  background: var(--bg);
  padding: var(--space-lg);
  padding-top: calc(var(--space-xl) + env(safe-area-inset-top, 0px));
}

.login-header {
  text-align: center;
  margin-bottom: 48px;
}

.login-title {
  font-size: var(--text-display);
  font-weight: 600;
  color: var(--text);
  margin-bottom: var(--space-sm);
  letter-spacing: -0.5px;
}

.login-subtitle {
  font-size: var(--text-body);
  color: var(--text-muted);
  line-height: var(--leading-normal);
}

.login-form {
  max-width: 360px;
  width: 100%;
  margin: 0 auto;
}

.field-group {
  margin-bottom: var(--space-lg);
}

.field-label {
  display: block;
  font-size: var(--text-body-sm);
  font-weight: 500;
  color: var(--text-muted);
  margin-bottom: var(--space-sm);
}

.field-input {
  width: 100%;
  height: var(--touch-target);
  padding: 0 var(--space-md);
  font-size: var(--text-body-lg);
  font-family: var(--font-sans);
  color: var(--text);
  background: var(--surface);
  border: 1px solid var(--divider);
  border-radius: var(--radius-md);
  outline: none;
  transition: border-color var(--duration-fast) var(--ease-out);
}

.field-input::placeholder {
  color: var(--text-placeholder);
}

.field-input:focus {
  border-color: var(--accent);
}

.code-row {
  display: flex;
  gap: var(--space-sm);
}

.code-row .field-input {
  flex: 1;
}

.code-btn {
  flex-shrink: 0;
  height: var(--touch-target);
  padding: 0 var(--space-md);
  font-size: var(--text-body-sm);
  font-family: var(--font-sans);
  font-weight: 500;
  color: var(--accent);
  background: var(--accent-soft);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background var(--duration-fast) var(--ease-out);
}

.code-btn:hover:not(:disabled) {
  background: rgba(184, 118, 62, 0.12);
}

.code-btn:active:not(:disabled) {
  transform: scale(0.97);
}

.code-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.login-btn {
  width: 100%;
  height: var(--touch-target);
  margin-top: var(--space-lg);
  font-size: var(--text-button);
  font-family: var(--font-sans);
  font-weight: 500;
  color: #fff;
  background: var(--accent);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background var(--duration-fast) var(--ease-out),
              transform var(--duration-fast) var(--ease-out);
}

.login-btn:hover:not(:disabled) {
  background: var(--accent-hover);
}

.login-btn:active:not(:disabled) {
  transform: scale(0.97);
}

.login-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
