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
      <h1>AI 家装</h1>
      <p>上传照片，一键生成装修效果图 + 360° 全景</p>
    </div>

    <div class="login-form">
      <van-cell-group inset>
        <van-field
          v-model="form.phone"
          label="手机号"
          placeholder="请输入手机号"
          type="tel"
          maxlength="11"
        />
        <van-field
          v-model="form.code"
          label="验证码"
          placeholder="请输入验证码"
          type="digit"
          maxlength="6"
        >
          <template #button>
            <van-button
              size="small"
              :disabled="countdown > 0 || sending"
              :loading="sending"
              @click="onSendCode"
            >
              {{ countdown > 0 ? `${countdown}s` : '发送验证码' }}
            </van-button>
          </template>
        </van-field>
      </van-cell-group>

      <div class="login-btn">
        <van-button type="primary" block round @click="onLogin">
          登录
        </van-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  background: linear-gradient(180deg, #f7f8fa 0%, #e8f0fe 100%);
  padding: 20px;
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.login-header h1 {
  font-size: 28px;
  font-weight: 600;
  color: #1989fa;
  margin-bottom: 8px;
}

.login-header p {
  font-size: 14px;
  color: #969799;
}

.login-btn {
  padding: 20px 16px 0;
}
</style>
