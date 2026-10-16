<script setup>
import { useRoute, useRouter } from 'vue-router'
import { accountName, accountPassword, login } from '../../admin/auth'

const route = useRoute()
const router = useRouter()

function keep(e, value) {
  if (e.target.value !== value) e.target.value = value
}

function submit() {
  if (!login(accountName, accountPassword)) return
  const next = route.query.to
  router.replace(typeof next === 'string' && next.startsWith('/admin') ? next : '/admin/assets')
}
</script>

<template>
  <main class="gate">
    <form class="gate__card" @submit.prevent="submit">
      <p class="gate__brand">FORTUNE</p>
      <h1>员工工作台</h1>

      <label class="ad-field">
        <span>用户名称</span>
        <input class="ad-input" name="username" :value="accountName" readonly autocomplete="off"
               tabindex="-1" @input="keep($event, accountName)" />
      </label>
      <label class="ad-field">
        <span>密码</span>
        <input class="ad-input" type="password" name="password" :value="accountPassword" readonly autocomplete="off"
               tabindex="-1" @input="keep($event, accountPassword)" />
      </label>

      <button type="submit" class="ad-btn ad-btn--block" autofocus>登录</button>
      <RouterLink class="gate__back" to="/">返回官网</RouterLink>
    </form>
  </main>
</template>
