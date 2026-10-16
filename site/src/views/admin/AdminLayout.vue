<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Icon from '../../components/admin/Icon.vue'
import { logout } from '../../admin/auth'
import { CAPS, can, canCount, me, meId, staff, toasts } from '../../admin/store'

const route = useRoute()
const router = useRouter()
const meta = computed(() => route.meta)

function exit() {
  logout()
  router.replace('/login')
}

const nav = computed(() => [
  { to: '/admin/assets', no: '01', label: '资产合集' },
  { to: '/admin/staff', no: '02', label: '员工列表' },
  { to: '/admin/permissions', no: '03', label: '权限管理' },
  { to: '/admin/studio', no: '04', label: 'AI 生图', locked: !can('studio.enter') },
])
</script>

<template>
  <div class="ad">
    <aside class="ad-side">
      <RouterLink to="/" class="ad-brand" aria-label="返回官网">FORTUNE<small>员工工作台</small></RouterLink>

      <nav class="ad-nav" aria-label="工作台导航">
        <RouterLink v-for="n in nav" :key="n.to" :to="n.to" class="ad-nav__a">
          <span class="ad-nav__no">{{ n.no }}</span>
          <span>{{ n.label }}</span>
          <Icon v-if="n.locked" name="lock" />
        </RouterLink>
      </nav>

      <div class="ad-me">
        <p class="ad-label">演示 · 切换身份</p>
        <select v-model.number="meId" class="ad-select" aria-label="切换身份">
          <option v-for="s in staff" :key="s.id" :value="s.id">{{ s.name }} · {{ s.role }}</option>
        </select>
        <p class="ad-me__can">可用功能 <b>{{ canCount }}</b> / {{ CAPS.length }}</p>
      </div>

      <div class="ad-side__exit">
        <button type="button" class="ad-back" @click="exit">退出</button>
        <RouterLink to="/" class="ad-back">← 返回官网</RouterLink>
      </div>
    </aside>

    <div class="ad-main">
      <header class="ad-head">
        <p class="eyebrow"><span>{{ meta.no }}</span>{{ meta.en }}</p>
        <h1>{{ meta.title }}</h1>
        <p class="ad-head__desc">{{ meta.desc }}</p>
      </header>
      <RouterView />
    </div>

    <div class="ad-toasts" aria-live="polite">
      <div v-for="t in toasts" :key="t.id" class="ad-toast">{{ t.msg }}</div>
    </div>
  </div>
</template>
