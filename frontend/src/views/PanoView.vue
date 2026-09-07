<script setup>
import { ref, onMounted, onBeforeUnmount, shallowRef } from 'vue'
import { useRoute } from 'vue-router'
import { showNotify } from 'vant'
import { Viewer } from 'photo-sphere-viewer'
import { VirtualTourPlugin } from 'photo-sphere-viewer/dist/plugins/virtual-tour'
import 'photo-sphere-viewer/dist/photo-sphere-viewer.css'
import { getGeneration } from '@/api/generations'

const route = useRoute()
const viewerContainer = ref(null)
const viewer = shallowRef(null)

// 当前生成任务数据
const generation = ref(null)
// 场景列表（同项目的其他全景图）
const scenes = ref([])
const currentScene = ref(0)

// 占位全景图（开发期用 pano-demo 的测试图）
const PLACEHOLDER_PANO = 'https://photo-sphere-viewer-data.netlify.app/assets/sphere.jpg'

async function loadData() {
  const id = route.params.id
  try {
    generation.value = await getGeneration(id)
    // TODO: 如果 generation 有 pano_url 用真实的，否则用占位图
    // 当前开发期用占位全景图
    scenes.value = [
      { id: 'scene-1', name: '客厅', panorama: PLACEHOLDER_PANO },
    ]
  } catch {
    // 开发期：API 可能没启动，用占位数据
    scenes.value = [
      { id: 'scene-1', name: '客厅', panorama: PLACEHOLDER_PANO },
      { id: 'scene-2', name: '卧室', panorama: 'https://photo-sphere-viewer-data.netlify.app/assets/sphere-cropped.jpg' },
    ]
  }
}

function initViewer() {
  if (!viewerContainer.value || scenes.value.length === 0) return

  const nodes = scenes.value.map((s, i) => ({
    id: s.id,
    label: s.name,
    panorama: s.panorama,
    // 连接到相邻场景（环形）
    links: scenes.value.length > 1
      ? [{ nodeId: scenes.value[(i + 1) % scenes.value.length].id }]
      : [],
  }))

  viewer.value = new Viewer({
    container: viewerContainer.value,
    defaultZoomLvl: 50,
    navbar: ['zoom', 'move', 'fullscreen', 'caption'],
    plugins: [
      [
        VirtualTourPlugin,
        {
          positionMode: 'manual',
          renderMode: '3d',
          nodes,
          startNodeId: nodes[0].id,
        },
      ],
    ],
  })

  // 切换场景时更新当前索引
  viewer.value.addEventListener('node-changed', (e) => {
    const idx = scenes.value.findIndex((s) => s.id === e.node.id)
    if (idx >= 0) currentScene.value = idx
  })
}

function switchScene(index) {
  const scene = scenes.value[index]
  if (!scene || !viewer.value) return
  const plugin = viewer.value.getPlugin(VirtualTourPlugin)
  plugin.setCurrentNode(scene.id)
}

function goBack() {
  history.back()
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
    <!-- 全景容器 -->
    <div ref="viewerContainer" class="viewer-container"></div>

    <!-- 顶部栏 -->
    <div class="pano-header">
      <van-icon name="arrow-left" size="20" color="#fff" @click="goBack" />
      <span class="pano-title">
        {{ generation?.type === 'pano' ? '全景图' : '全景浏览' }}
        {{ scenes.length > 1 ? `· ${scenes[currentScene]?.name || ''}` : '' }}
      </span>
      <van-icon name="share-o" size="20" color="#fff" />
    </div>

    <!-- 底部场景轮播（多个场景时显示） -->
    <div v-if="scenes.length > 1" class="scene-bar">
      <div class="scene-scroll">
        <div
          v-for="(scene, i) in scenes"
          :key="scene.id"
          :class="['scene-thumb', { active: i === currentScene }]"
          @click="switchScene(i)"
        >
          {{ scene.name }}
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.pano-page {
  position: fixed;
  inset: 0;
  background: #000;
  overflow: hidden;
}

.viewer-container {
  width: 100%;
  height: 100%;
}

.pano-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  padding-top: calc(12px + env(safe-area-inset-top, 0px));
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0.6), transparent);
}

.pano-title {
  flex: 1;
  color: #fff;
  font-size: 16px;
  font-weight: 500;
}

.scene-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 10;
  padding: 12px 0 calc(12px + env(safe-area-inset-bottom, 0px));
  background: linear-gradient(to top, rgba(0, 0, 0, 0.7), transparent);
}

.scene-scroll {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding: 0 16px;
  scrollbar-width: none;
}

.scene-scroll::-webkit-scrollbar {
  display: none;
}

.scene-thumb {
  flex-shrink: 0;
  padding: 8px 16px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.8);
  font-size: 13px;
  transition: all 0.2s;
}

.scene-thumb.active {
  background: #1989fa;
  color: #fff;
}
</style>
