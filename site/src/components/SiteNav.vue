<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { jump } from '../jump'

const scrolled = ref(false)
const onScroll = () => { scrolled.value = scrollY > 40 }

onMounted(() => {
  onScroll()
  addEventListener('scroll', onScroll, { passive: true })
})
onUnmounted(() => removeEventListener('scroll', onScroll))
</script>

<template>
  <header class="nav" :class="{ 'is-scrolled': scrolled }">
    <a class="brand" href="#top" aria-label="FORTUNE 回到顶部" @click="jump">FORTUNE</a>
    <nav class="nav__links" aria-label="主导航">
      <a href="#works" @click="jump">精选案例</a>
      <a href="#philosophy" @click="jump">设计理念</a>
      <a href="#contact" @click="jump">联系我们</a>
      <RouterLink class="nav__staff" to="/admin/assets">员工入口</RouterLink>
    </nav>
    <a class="btn btn--sm" href="#contact" @click="jump">预约量房</a>
  </header>
</template>
