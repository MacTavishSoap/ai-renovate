<script setup>
import { ref, onMounted, onBeforeUnmount, shallowRef, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Viewer } from '@photo-sphere-viewer/core'
import '@photo-sphere-viewer/core/index.css'
import {
  loadManifest, getPanoById, pickInitialLevel, getPanoUrl,
  getThumbUrl, getEffectUrl, getFloorplanUrl, isMobileDevice
} from '@/api/pano'

const route = useRoute()
const router = useRouter()

// --- DOM refs ---
const container = ref(null)

// --- PSV instance ---
const viewer = shallowRef(null)

// --- State ---
const loading = ref(true)
const error = ref(false)
const errorMsg = ref('')
const list = ref([])
const currentPano = ref(null)
const currentIndex = ref(0)
const currentLevel = ref('mobile')
const uiVisible = ref(true)
const interacted = ref(false)
const showHint = ref(true)

// --- Side panel (效果图 / 户型图) ---
const sidePanel = ref(null) // null | 'effect' | 'floorplan'

const isMobile = isMobileDevice()
const hasMultipleLevels = computed(() =>
  currentPano.value?.levels?.mobile && currentPano.value?.levels?.full
)
const hasScenes = computed(() => list.value.length > 1)
const hasEffect = computed(() => !!currentPano.value?.effectImage)
const hasFloorplan = computed(() => !!currentPano.value?.floorplan)

// --- Idle UI auto-hide ---
let idleTimer = null
function resetIdle() {
  uiVisible.value = true
  if (interacted.value) showHint.value = false
  clearTimeout(idleTimer)
  idleTimer = setTimeout(() => {
    if (!sidePanel.value) uiVisible.value = false
  }, 3500)
}

function onActivity() {
  interacted.value = true
  resetIdle()
}

// --- Build PSV config ---
function buildConfig(panoData, level) {
  const url = getPanoUrl(panoData, level)
  const cfg = {
    container: container.value,
    panorama: url,
    loadingTxt: '',
    defaultZoomLvl: panoData.defaultZoomLvl ?? 50,
    navbar: false,
    minFov: panoData.minFov || 40,
    maxFov: panoData.maxFov || 75,
    defaultYaw: panoData.defaultYaw ?? 0,
    defaultPitch: panoData.defaultPitch ?? 0,
    sphereCorrection: panoData.sphereCorrection || {},
    canvasBackground: '#0A0A0C',
    moveInertia: true,
    mousewheel: true,
    mousemove: true,
    touchmoveTwoFingers: false,
    defaultTransition: { speed: 1200, effect: 'fade' },
    size: { width: '100%', height: '100%' },
  }
  return cfg
}

// --- Init viewer ---
function initViewer(panoData, level) {
  if (viewer.value) {
    viewer.value.destroy()
    viewer.value = null
  }
  loading.value = true
  error.value = false

  const cfg = buildConfig(panoData, level)
  viewer.value = new Viewer(cfg)

  viewer.value.addEventListener('ready', () => {
    loading.value = false
  })

  viewer.value.addEventListener('panorama-error', () => {
    loading.value = false
    error.value = true
    errorMsg.value = '图片加载失败'
  })

  viewer.value.addEventListener('position-updated', onActivity)
  viewer.value.addEventListener('zoom-updated', onActivity)
}

// --- Scene switching ---
function switchScene(index) {
  if (index === currentIndex.value || !list.value.length) return
  const pano = list.value[index]
  if (!pano) return

  currentIndex.value = index
  currentPano.value = pano
  currentLevel.value = pickInitialLevel(pano)
  showHint.value = true
  interacted.value = false
  sidePanel.value = null

  const url = getPanoUrl(pano, currentLevel.value)
  loading.value = true

  viewer.value?.setPanorama(url, {
    transition: { speed: 1200, effect: 'fade' },
  }).then(() => {
    loading.value = false
  }).catch(() => {
    loading.value = false
  })

  resetIdle()
}

// --- Quality switching ---
function switchLevel(level) {
  if (level === currentLevel.value || !currentPano.value) return
  currentLevel.value = level
  loading.value = true

  const pos = viewer.value?.getPosition()
  const zoom = viewer.value?.getZoomLevel()
  const url = getPanoUrl(currentPano.value, level)

  const img = new Image()
  img.onload = () => {
    if (!viewer.value) return
    const opts = { transition: { speed: 800, effect: 'fade' } }
    if (pos) {
      opts.position = { yaw: pos.yaw, pitch: pos.pitch }
      opts.zoom = zoom
    }
    viewer.value.setPanorama(url, opts).then(() => {
      loading.value = false
    }).catch(() => {
      loading.value = false
    })
  }
  img.onerror = () => { loading.value = false }
  img.src = url
}

// --- Side panel ---
function openPanel(type) {
  sidePanel.value = type
}
function closePanel() {
  sidePanel.value = null
  resetIdle()
}

// --- Navigation ---
function goBack() {
  router.back()
}

function shareLink() {
  if (navigator.share) {
    navigator.share({ url: window.location.href }).catch(() => {})
  } else {
    navigator.clipboard?.writeText(window.location.href)
  }
}

// --- Lifecycle ---
onMounted(async () => {
  try {
    list.value = await loadManifest()
    const idx = list.value.findIndex(p => p.id === route.params.id)
    const index = idx >= 0 ? idx : 0
    const pano = list.value[index]
    if (!pano) {
      error.value = true
      errorMsg.value = '未找到全景图'
      loading.value = false
      return
    }
    currentIndex.value = index
    currentPano.value = pano
    currentLevel.value = pickInitialLevel(pano)
    initViewer(pano, currentLevel.value)
  } catch {
    error.value = true
    errorMsg.value = '加载失败'
    loading.value = false
  }

  const el = container.value
  if (el) {
    el.addEventListener('touchstart', onActivity, { passive: true })
    el.addEventListener('mousemove', onActivity, { passive: true })
  }
  resetIdle()
})

onBeforeUnmount(() => {
  clearTimeout(idleTimer)
  const el = container.value
  if (el) {
    el.removeEventListener('touchstart', onActivity)
    el.removeEventListener('mousemove', onActivity)
  }
  if (viewer.value) {
    viewer.value.destroy()
    viewer.value = null
  }
})

function preventGesture(e) { e.preventDefault() }
document.addEventListener('gesturestart', preventGesture, { passive: false })
</script>

<template>
  <div class="viewer-page" :class="{ 'ui-hidden': !uiVisible }">
    <!-- PSV mounts here -->
    <div ref="container" class="psv-container" />

    <!-- Loading overlay -->
    <Transition name="fade">
      <div v-if="loading" class="overlay loading-overlay">
        <div class="loader-ring" />
        <p class="loader-text">{{ currentPano?.title || '加载中' }}</p>
      </div>
    </Transition>

    <!-- Error overlay -->
    <Transition name="fade">
      <div v-if="error" class="overlay error-overlay">
        <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2"><path d="M12 9v4m0 4h.01M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" /></svg>
        <p>{{ errorMsg }}</p>
        <button class="retry-btn" @click="goBack">返回列表</button>
      </div>
    </Transition>

    <!-- Top bar (glass) -->
    <header class="topbar">
      <button class="icon-btn" @click="goBack" aria-label="返回">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5M12 19l-7-7 7-7" /></svg>
      </button>
      <div class="title-area">
        <span class="title">{{ currentPano?.title || '全景浏览' }}</span>
        <span v-if="currentPano?.meta" class="subtitle">{{ currentPano.meta }}</span>
      </div>
      <button class="icon-btn" @click="shareLink" aria-label="分享">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3" /><circle cx="6" cy="12" r="3" /><circle cx="18" cy="19" r="3" /><line x1="8.59" y1="13.51" x2="15.42" y2="17.49" /><line x1="15.41" y1="6.51" x2="8.59" y2="10.49" /></svg>
      </button>
    </header>

    <!-- Right-side tools (效果图 / 户型图) -->
    <div v-if="hasEffect || hasFloorplan" class="side-tools">
      <button v-if="hasEffect" class="side-btn" :class="{ active: sidePanel === 'effect' }" @click="sidePanel === 'effect' ? closePanel() : openPanel('effect')" aria-label="效果图">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><rect x="3" y="3" width="18" height="18" rx="2" /><circle cx="9" cy="9" r="2" /><path d="M21 15l-5-5L5 21" /></svg>
        <span class="side-label">效果图</span>
      </button>
      <button v-if="hasFloorplan" class="side-btn" :class="{ active: sidePanel === 'floorplan' }" @click="sidePanel === 'floorplan' ? closePanel() : openPanel('floorplan')" aria-label="户型图">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M3 9h18M9 21V9M21 9v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V9" /><path d="M3 9V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v4" /></svg>
        <span class="side-label">户型图</span>
      </button>
    </div>

    <!-- Side panel (slide-in) -->
    <Transition name="slide-panel">
      <aside v-if="sidePanel" class="side-panel">
        <header class="panel-header">
          <span>{{ sidePanel === 'effect' ? '效果图' : '户型图' }}</span>
          <button class="icon-btn small" @click="closePanel" aria-label="关闭">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 6L6 18M6 6l12 12" /></svg>
          </button>
        </header>
        <div class="panel-body">
          <img
            v-if="sidePanel === 'effect' && currentPano?.effectImage"
            :src="getEffectUrl(currentPano)"
            alt="效果图"
            class="panel-img"
          />
          <img
            v-if="sidePanel === 'floorplan' && currentPano?.floorplan"
            :src="getFloorplanUrl(currentPano)"
            alt="户型图"
            class="panel-img"
          />
        </div>
      </aside>
    </Transition>

    <!-- Drag hint -->
    <Transition name="fade-slow">
      <div v-if="showHint && !loading && !sidePanel" class="drag-hint">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M9 11V6a2 2 0 0 1 4 0v5M9 11a2 2 0 0 0-4 0v3a7 7 0 0 0 14 0v-3a2 2 0 0 0-4 0" /></svg>
        <span>拖动浏览</span>
      </div>
    </Transition>

    <!-- Quality pill -->
    <div v-if="hasMultipleLevels" class="quality-pill">
      <button :class="{ active: currentLevel === 'mobile' }" @click="switchLevel('mobile')">流畅</button>
      <button :class="{ active: currentLevel === 'full' }" @click="switchLevel('full')">高清</button>
    </div>

    <!-- Scene navigation strip -->
    <nav v-if="hasScenes" class="scene-strip" aria-label="场景切换">
      <div class="scene-scroll">
        <button
          v-for="(pano, i) in list"
          :key="pano.id"
          :class="['scene-thumb', { active: i === currentIndex }]"
          @click="switchScene(i)"
        >
          <img :src="getThumbUrl(pano)" :alt="pano.title" loading="lazy" />
          <span class="scene-label">{{ pano.title }}</span>
        </button>
      </div>
    </nav>
  </div>
</template>

<style scoped>
.viewer-page {
  position: fixed; inset: 0; background: #0A0A0C; overflow: hidden; touch-action: none;
}
.psv-container { width: 100%; height: 100%; touch-action: none; }

/* --- Overlays --- */
.overlay {
  position: absolute; inset: 0; z-index: 30;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: var(--space-md);
}
.loading-overlay { background: #0A0A0C; }
.error-overlay { color: rgba(255,255,255,0.6); }
.loader-ring {
  width: 36px; height: 36px;
  border: 2.5px solid rgba(255,255,255,0.12);
  border-top-color: var(--accent); border-radius: 50%;
  animation: spin 0.9s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.loader-text { font-size: var(--text-body-sm); color: rgba(255,255,255,0.5); }
.retry-btn {
  border: 1px solid rgba(255,255,255,0.15); background: transparent;
  color: #fff; padding: var(--space-sm) var(--space-lg);
  border-radius: var(--radius-full); font-size: var(--text-body-sm); cursor: pointer;
}
.retry-btn:active { background: rgba(255,255,255,0.08); }

/* --- Top bar --- */
.topbar {
  position: absolute; top: 0; left: 0; right: 0; z-index: 20;
  display: flex; align-items: center; gap: var(--space-sm);
  padding: var(--space-md);
  padding-top: calc(var(--space-md) + env(safe-area-inset-top, 0px));
  background: linear-gradient(to bottom, rgba(0,0,0,0.45), transparent);
  transition: opacity var(--duration-slow) var(--ease-out), transform var(--duration-slow) var(--ease-out);
}
.ui-hidden .topbar { opacity: 0; transform: translateY(-100%); pointer-events: none; }

.icon-btn {
  display: flex; align-items: center; justify-content: center;
  width: var(--touch-target); height: var(--touch-target); flex-shrink: 0;
  color: #fff; background: rgba(255,255,255,0.08);
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255,255,255,0.06); border-radius: var(--radius-full);
  cursor: pointer;
  transition: background var(--duration-fast) var(--ease-out), transform var(--duration-fast) var(--ease-out);
}
.icon-btn:active { transform: scale(0.92); background: rgba(255,255,255,0.14); }
.icon-btn.small { width: 36px; height: 36px; }

.title-area { flex: 1; min-width: 0; text-align: center; display: flex; flex-direction: column; gap: 1px; }
.title { font-size: var(--text-body); font-weight: 600; color: #fff; text-shadow: 0 1px 6px rgba(0,0,0,0.4); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.subtitle { font-size: var(--text-caption); color: rgba(255,255,255,0.55); }

/* --- Side tools (vertical, right edge) --- */
.side-tools {
  position: absolute; right: var(--space-md); top: 50%; transform: translateY(-50%); z-index: 20;
  display: flex; flex-direction: column; gap: var(--space-sm);
  transition: opacity var(--duration-slow) var(--ease-out), transform var(--duration-slow) var(--ease-out);
}
.ui-hidden .side-tools { opacity: 0; transform: translateY(-50%) translateX(120%); pointer-events: none; }

.side-btn {
  display: flex; flex-direction: column; align-items: center; gap: 4px;
  background: var(--dark-surface);
  backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
  border: 1px solid var(--dark-border); border-radius: var(--radius-md);
  padding: 10px 8px; color: rgba(255,255,255,0.7);
  cursor: pointer; width: 56px;
  transition: all var(--duration-fast) var(--ease-out);
}
.side-btn:active { transform: scale(0.94); }
.side-btn.active { background: var(--accent); color: #fff; border-color: var(--accent); }
.side-label { font-size: 10px; font-weight: 500; }

/* --- Side panel --- */
.side-panel {
  position: absolute; right: 0; top: 0; bottom: 0; z-index: 40;
  width: min(420px, 85vw); background: rgba(14, 14, 16, 0.96);
  backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
  display: flex; flex-direction: column;
  box-shadow: -8px 0 32px rgba(0,0,0,0.4);
}
.panel-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: var(--space-md);
  padding-top: calc(var(--space-md) + env(safe-area-inset-top, 0px));
  border-bottom: 1px solid var(--dark-border);
  color: #fff; font-size: var(--text-h3); font-weight: 600;
}
.panel-body {
  flex: 1; overflow-y: auto; padding: var(--space-md);
  display: flex; align-items: flex-start; justify-content: center;
}
.panel-img {
  width: 100%; border-radius: var(--radius-md);
  border: 1px solid var(--dark-border);
}

/* --- Drag hint --- */
.drag-hint {
  position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 15;
  display: flex; flex-direction: column; align-items: center; gap: var(--space-sm);
  color: rgba(255,255,255,0.45); pointer-events: none;
}
.drag-hint svg { animation: nudge 2s var(--ease-out) infinite; }
.drag-hint span { font-size: var(--text-caption); }
@keyframes nudge {
  0%, 100% { transform: translateX(0); opacity: 0.45; }
  50% { transform: translateX(8px); opacity: 0.8; }
}

/* --- Quality pill --- */
.quality-pill {
  position: absolute; right: var(--space-md); z-index: 20;
  bottom: calc(var(--space-md) + env(safe-area-inset-bottom, 0px));
  display: flex; gap: 2px;
  background: var(--dark-surface);
  backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
  border: 1px solid var(--dark-border);
  border-radius: var(--radius-full); padding: 3px;
  transition: opacity var(--duration-slow) var(--ease-out), transform var(--duration-slow) var(--ease-out);
}
.ui-hidden .quality-pill { opacity: 0; transform: translateY(120%); pointer-events: none; }
.viewer-page:has(.scene-strip) .quality-pill {
  bottom: calc(96px + var(--space-md) + env(safe-area-inset-bottom, 0px));
}
.quality-pill button {
  border: none; background: transparent; color: rgba(255,255,255,0.45);
  font-size: var(--text-caption); font-weight: 500;
  padding: 6px 14px; border-radius: var(--radius-full); cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
}
.quality-pill button.active { background: rgba(255,255,255,0.14); color: #fff; }
.quality-pill button:active { transform: scale(0.94); }

/* --- Scene strip --- */
.scene-strip {
  position: absolute; bottom: 0; left: 0; right: 0; z-index: 20;
  padding: var(--space-md) var(--space-sm) calc(var(--space-sm) + env(safe-area-inset-bottom, 0px));
  background: linear-gradient(to top, rgba(0,0,0,0.55), transparent);
  transition: opacity var(--duration-slow) var(--ease-out), transform var(--duration-slow) var(--ease-out);
}
.ui-hidden .scene-strip { opacity: 0; transform: translateY(100%); pointer-events: none; }
.scene-scroll {
  display: flex; gap: var(--space-sm); overflow-x: auto; overflow-y: hidden;
  scroll-snap-type: x mandatory; scrollbar-width: none; -ms-overflow-style: none;
  padding: 0 var(--space-sm);
}
.scene-scroll::-webkit-scrollbar { display: none; }
.scene-thumb {
  position: relative; flex-shrink: 0; width: 96px; height: 56px;
  border: 2px solid transparent; border-radius: var(--radius-md);
  overflow: hidden; cursor: pointer; padding: 0;
  background: rgba(255,255,255,0.05); scroll-snap-align: start;
  transition: border-color var(--duration-fast) var(--ease-out), transform var(--duration-fast) var(--ease-out);
}
.scene-thumb img { width: 100%; height: 100%; object-fit: cover; }
.scene-thumb.active { border-color: var(--accent); transform: scale(1.04); }
.scene-thumb:active { transform: scale(0.96); }
.scene-label {
  position: absolute; bottom: 0; left: 0; right: 0;
  padding: 12px 6px 3px; background: linear-gradient(to top, rgba(0,0,0,0.7), transparent);
  color: #fff; font-size: 10px; font-weight: 500;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; text-align: center;
}

/* --- Transitions --- */
.fade-enter-active, .fade-leave-active { transition: opacity 0.4s var(--ease-out); }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.fade-slow-enter-active, .fade-slow-leave-active { transition: opacity 0.6s var(--ease-out); }
.fade-slow-enter-from, .fade-slow-leave-to { opacity: 0; }

.slide-panel-enter-active, .slide-panel-leave-active {
  transition: transform var(--duration-normal) var(--ease-out);
}
.slide-panel-enter-from, .slide-panel-leave-to { transform: translateX(100%); }

:deep(.psv-loader) { display: none !important; }

@media (min-width: 768px) {
  .scene-thumb { width: 120px; height: 68px; }
}
</style>
