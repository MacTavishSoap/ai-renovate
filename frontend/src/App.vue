<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { Tabbar, TabbarItem } from 'vant'

const route = useRoute()

// 全景浏览页不显示底部导航
const showTabbar = computed(() => !['pano', 'login'].includes(route.name))
</script>

<template>
  <div class="app-container">
    <RouterView />
    <Tabbar v-if="showTabbar" route>
      <TabbarItem to="/generate" icon="photo-o">生成</TabbarItem>
      <TabbarItem to="/history" icon="clock-o">历史</TabbarItem>
    </Tabbar>
  </div>
</template>

<style scoped>
.app-container {
  min-height: 100vh;
  padding-bottom: 50px; /* Tabbar 高度 */
}
</style>
