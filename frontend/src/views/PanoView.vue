<script setup>
import { ref, onMounted, onBeforeUnmount, shallowRef } from 'vue'
import { useRoute } from 'vue-router'
import { Viewer } from 'photo-sphere-viewer'
import 'photo-sphere-viewer/dist/photo-sphere-viewer.css'
import { getGeneration } from '@/api/generations'

const route = useRoute()
const viewerContainer = ref(null)
const viewer = shallowRef(null)

const generation = ref(null)
const scenes = ref([])
const currentScene = ref(0)
const loading = ref(true)

// 开发期占位全景图
const PLACEHOLDER_PANOS = [
  'https://photo-sphere-viewer-data.netlify.app/assets/sphere.jpg',
  'https://photo-sphere-viewer-data.netlify.app/assets/sphere-cropped.jpg',
]
const PLACEHOLDER_NAMES = ['客厅', '卧室']

async function loadData() {
  const id = route.params.id
  try {
    generation.value = await getGeneration(id)
    scenes.value = PLACEHOLDER_PANOS.map((url, i) => ({
      id: `scene-${i}`,
      name: PLACEHOLDER_NAMES[i] || `场景${i + 1}`,
      panorama: url,
    }))
  } catch {
    scenes.value = PLACEHOLDER_PANOS.map((url, i) => ({
      id: `scene-${i}`,
      name: PLACEHOLDER_NAMES[i] || `场景${i + 1}`,
      panorama: url,
    }))
  }
}

function initViewer() {
  if (!viewerContainer.value || scenes.value.length === 0) return
  viewer.value = new Viewer({
    container: viewerContainer.value,
    panorama: scenes.value[0].panorama,
    defaultZoomLvl: 50,
    navbar: ['zoom', 'move', 'fullscreen'],
    loadingTxt: '加载全景图...',
    size: { width: '100%', height: '100%' },
  })
  loading.value = false
}

function switchScene(index) {
  if (index === currentScene.value || !viewer.value) return
  currentScene.value = index
  viewer.value.setPanorama(scenes.value[index].panorama, {
    transition: { speed: 1500 },
  })
}

function goBack() {
  history.back()
}

function shareLink() {
  navigator.clipboard?.writeText(window.location.href)
}

onMounted(async () => {
  await loadData()
  initViewer()
})

onBeforeUnmount(() => {
  if (viewer.value) {
    viewer.value.destroy()
    viewer.value = null
  }
})
</script>

<template>
  <div class="pano-page">
    <div ref="viewerContainer" class="viewer-container"></div>

    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p class="loading-text">正在加载全景图...</p>
    </div>

    <header class="pano-header">
      <button class="header-btn" @click="goBack" aria-label="返回">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M19 12H5M12 19l-7-7 7-7" />
        </svg>
      </button>
      <span class="pano-title">{{ scenes[currentScene]?.name || '全景浏览' }}</span>
      <button class="header-btn" @click="shareLink" aria-label="分享">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="18" cy="5" r="3" /><circle cx="6" cy="12" r="3" /><circle cx="18" cy="19" r="3" />
          <line x1="8.59" y1="13.51" x2="15.42" y2="17.49" />
          <line x1="15.41" y1="6.51" x2="8.59" y2="10.49" />
        </svg>
      </button>
    </header>

    <nav v-if="scenes.length > 1" class="scene-bar" aria-label="场景切换">
      <div class="scene-scroll">
        <button
          v-for="(scene, i) in scenes"
          :key="scene.id"
          :class="['scene-chip', { active: i === currentScene }]"
          @click="switchScene(i)"
        >
          {{ scene.name }}
        </button>
      </div>
    </nav>
  </div>
</template>

<style scoped>
.pano-page {
  position: fixed;
  inset: 0;
  background: var(--dark);
  overflow: hidden;
}

.viewer-container {
  width: 100%;
  height: 100%;
}

.viewer-container :deep(.psv-navbar) {
  background: rgba(0, 0, 0, 0.4);
}

.loading-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-md);
  background: var(--dark);
  z-index: 5;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  font-size: var(--text-body-sm);
  color: rgba(255, 255, 255, 0.7);
}

.pano-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md);
  padding-top: calc(var(--space-md) + env(safe-area-inset-top, 0px));
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0.5), transparent);
}

.header-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: var(--touch-target);
  height: var(--touch-target);
  color: #fff;
  background: none;
  border: none;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}

.header-btn:active {
  opacity: 0.6;
}

.pano-title {
  flex: 1;
  color: #fff;
  font-size: var(--text-h3);
  font-weight: 600;
  text-align: center;
}

.scene-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 10;
  padding: var(--space-md) 0 calc(var(--space-md) + env(safe-area-inset-bottom, 0px));
  background: linear-gradient(to top, rgba(0, 0, 0, 0.6), transparent);
}

.scene-scroll {
  display: flex;
  gap: var(--space-sm);
  overflow-x: auto;
  overflow-y: hidden;
  padding: 0 var(--space-md);
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.scene-scroll::-webkit-scrollbar {
  display: none;
}

.scene-chip {
  flex-shrink: 0;
  height: 36px;
  padding: 0 var(--space-md);
  font-size: var(--text-body-sm);
  font-family: var(--font-sans);
  font-weight: 500;
  color: rgba(255, 255, 255, 0.75);
  background: rgba(255, 255, 255, 0.15);
  border: none;
  border-radius: var(--radius-full);
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
  transition: background var(--duration-fast) var(--ease-out),
              color var(--duration-fast) var(--ease-out);
}

.scene-chip.active {
  background: var(--accent);
  color: #fff;
}

.scene-chip:active {
  transform: scale(0.95);
}

@media (prefers-reduced-motion: reduce) {
  .loading-spinner {
    animation: none;
  }
}
</style>
