<script setup>
// 360° 全景查看器。
// 与项目 frontend/src/views/PanoView.vue 使用同一套:
// Photo Sphere Viewer v5、同样的视角参数、manifest 与多清晰度选择(api/pano.js)。
// PanoView 是整页组件(固定铺满、依赖路由与全局样式),这里把它的查看器部分嵌进后台。
import { onBeforeUnmount, onMounted, ref, shallowRef, watch } from 'vue'
import { Viewer } from '@photo-sphere-viewer/core'
import '@photo-sphere-viewer/core/index.css'
import { getPanoById, getPanoUrl, loadManifest, pickInitialLevel } from '@frontend/api/pano'
import { reduce } from '../../data'

const props = defineProps({
  panoId: { type: String, required: true },
  filter: { type: String, default: 'none' }, // 当前版本的光影效果
})

const box = ref(null)
const viewer = shallowRef(null)
const loading = ref(true)
const failed = ref(false)
const hint = ref(true)

let raf = 0
let idleAt = 0

function config(pano) {
  return {
    container: box.value,
    panorama: getPanoUrl(pano, pickInitialLevel(pano)),
    loadingTxt: '',
    defaultZoomLvl: pano.defaultZoomLvl ?? 50,
    navbar: false,
    minFov: pano.minFov || 40,
    maxFov: pano.maxFov || 75,
    defaultYaw: pano.defaultYaw ?? 0,
    defaultPitch: pano.defaultPitch ?? 0,
    sphereCorrection: pano.sphereCorrection || {},
    canvasBackground: '#0A0A0C',
    moveInertia: true,
    mousewheel: true,
    mousemove: true,
    touchmoveTwoFingers: false,
    defaultTransition: { speed: 1200, effect: 'fade' },
    size: { width: '100%', height: '100%' },
  }
}

async function open() {
  loading.value = true
  failed.value = false
  try {
    const pano = getPanoById(await loadManifest(), props.panoId)
    if (!pano) throw new Error('missing')
    if (viewer.value) {
      await viewer.value.setPanorama(getPanoUrl(pano, pickInitialLevel(pano)), { transition: false })
      loading.value = false
      return
    }
    const v = new Viewer(config(pano))
    viewer.value = v
    v.addEventListener('ready', () => { loading.value = false })
    v.addEventListener('panorama-error', () => { loading.value = false; failed.value = true })
  } catch {
    loading.value = false
    failed.value = true
  }
}

// 没人操作时缓慢自转,让人一眼看出这是 360° 的
function spin() {
  const v = viewer.value
  if (v && !loading.value && !reduce && performance.now() > idleAt) {
    const p = v.getPosition()
    v.rotate({ yaw: p.yaw + 0.0011, pitch: p.pitch })
  }
  raf = requestAnimationFrame(spin)
}
function touched() {
  idleAt = performance.now() + 6000
  hint.value = false
}

onMounted(() => {
  open()
  raf = requestAnimationFrame(spin)
  for (const ev of ['pointerdown', 'wheel', 'touchstart']) box.value.addEventListener(ev, touched, { passive: true })
})
onBeforeUnmount(() => {
  cancelAnimationFrame(raf)
  viewer.value?.destroy()
  viewer.value = null
})
watch(() => props.panoId, open)
</script>

<template>
  <div class="pano">
    <div ref="box" class="pano__view" :style="{ filter }"></div>
    <Transition name="ad-fade">
      <div v-if="loading" class="pano__cover"><i class="pano__ring"></i></div>
    </Transition>
    <div v-if="failed" class="pano__cover pano__cover--err">全景图加载失败,请通过服务器地址访问</div>
    <p v-if="hint && !loading && !failed" class="pano__hint">拖动画面,环顾四周</p>
  </div>
</template>
