<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { Tabbar, TabbarItem } from 'vant'

const route = useRoute()

// 全景浏览页 + 画廊页不显示底部导航（沉浸式体验）
const showTabbar = computed(() => !['pano', 'pano-gallery', 'gallery', 'login'].includes(route.name))
</script>

<template>
  <div class="app-container">
    <RouterView v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </RouterView>
    <Tabbar v-if="showTabbar" route>
      <TabbarItem to="/generate" icon="photo-o">生成</TabbarItem>
      <TabbarItem to="/history" icon="clock-o">历史</TabbarItem>
    </Tabbar>
  </div>
</template>

<style scoped>
.app-container {
  min-height: 100vh;
  padding-bottom: var(--van-tabbar-height);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--duration-normal) var(--ease-out);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
