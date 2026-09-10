<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { loadManifest, getThumbUrl, getPhotos, getEffects } from '@/api/pano'

const router = useRouter()
const list = ref([])
const loading = ref(true)
const error = ref(false)

onMounted(async () => {
  try {
    list.value = await loadManifest()
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
})

function open(id) {
  router.push(`/pano/${id}`)
}
</script>

<template>
  <div class="gallery">
    <header class="header">
      <div class="header-inner">
        <h1>全景看房</h1>
        <span v-if="!loading" class="count">{{ list.length }} 个场景</span>
      </div>
    </header>

    <!-- 加载骨架 -->
    <div v-if="loading" class="grid">
      <div v-for="i in 2" :key="i" class="card skeleton">
        <div class="thumb-skel" />
        <div class="info-skel">
          <div class="line w-60" />
          <div class="line w-40" />
        </div>
      </div>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="state">
      <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2"><path d="M12 9v4m0 4h.01M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" /></svg>
      <p>加载失败</p>
      <button class="retry" @click="loading = true; error = false; onMounted()">重试</button>
    </div>

    <!-- 空状态 -->
    <div v-else-if="list.length === 0" class="state">
      <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2"><rect x="3" y="3" width="18" height="18" rx="2" /><circle cx="9" cy="9" r="2" /><path d="M21 15l-5-5L5 21" /></svg>
      <p>还没有全景图</p>
      <p class="hint">把图片放入 public/panoramas/ 并编辑 manifest.json</p>
    </div>

    <!-- 卡片网格 -->
    <div v-else class="grid">
      <div
        v-for="pano in list"
        :key="pano.id"
        class="card"
        @click="open(pano.id)"
      >
        <!-- 全景图缩略图 -->
        <div class="thumb-wrap">
          <img
            :src="getThumbUrl(pano)"
            :alt="pano.title"
            loading="lazy"
            class="thumb"
            width="400"
            height="200"
          />
          <span v-if="pano.badge" class="badge">{{ pano.badge }}</span>
          <span class="enter-icon" aria-hidden="true">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M15 3h6v6M14 10l7-7M21 14v5a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5" /></svg>
          </span>
        </div>

        <div class="info">
          <div class="title">{{ pano.title }}</div>
          <div v-if="pano.meta" class="meta">{{ pano.meta }}</div>
        </div>

        <!-- 附属图: 实拍图 + 3D效果图 (有的话才显示) -->
        <div v-if="getPhotos(pano).length || getEffects(pano).length" class="extras">
          <span v-if="getPhotos(pano).length" class="extra-badge">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" /><circle cx="12" cy="13" r="4" /></svg>
            实拍 {{ getPhotos(pano).length }}
          </span>
          <span v-if="getEffects(pano).length" class="extra-badge">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="3" y="3" width="18" height="18" rx="2" /><circle cx="9" cy="9" r="2" /><path d="M21 15l-5-5L5 21" /></svg>
            3D {{ getEffects(pano).length }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.gallery { padding-bottom: var(--space-xl); }

.header {
  position: sticky; top: 0; z-index: 10;
  background: rgba(250, 249, 247, 0.82);
  backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--divider);
}
.header-inner {
  display: flex; align-items: baseline; justify-content: space-between;
  padding: var(--space-md) var(--space-lg);
}
.header h1 { font-size: var(--text-h1); font-weight: 700; letter-spacing: -0.02em; }
.count { font-size: var(--text-caption); color: var(--text-muted); }

.grid {
  display: grid; gap: var(--space-md);
  padding: var(--space-md) var(--space-lg);
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
}

.card {
  background: var(--surface); border-radius: var(--radius-lg);
  overflow: hidden; cursor: pointer; border: none; width: 100%;
  text-align: left; padding: 0;
  box-shadow: var(--shadow-card);
  transition: transform var(--duration-fast) var(--ease-out),
              box-shadow var(--duration-fast) var(--ease-out);
}
.card:hover { transform: translateY(-2px); box-shadow: var(--shadow-raised); }
.card:active { transform: scale(0.98); }

.thumb-wrap { position: relative; aspect-ratio: 2 / 1; overflow: hidden; background: #f0eee9; }
.thumb { width: 100%; height: 100%; object-fit: cover; transition: transform var(--duration-slow) var(--ease-out); }
.card:hover .thumb { transform: scale(1.04); }

.badge {
  position: absolute; top: var(--space-sm); left: var(--space-sm);
  background: var(--dark-surface); backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
  color: #fff; font-size: 11px; font-weight: 500;
  padding: 3px 8px; border-radius: var(--radius-full);
}

.enter-icon {
  position: absolute; bottom: var(--space-sm); right: var(--space-sm);
  width: var(--touch-target); height: var(--touch-target);
  display: flex; align-items: center; justify-content: center;
  background: var(--dark-surface); backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
  color: #fff; border-radius: var(--radius-full);
  opacity: 0; transform: scale(0.8);
  transition: opacity var(--duration-normal) var(--ease-out),
              transform var(--duration-normal) var(--ease-spring);
}
.card:hover .enter-icon { opacity: 1; transform: scale(1); }

.info { padding: var(--space-sm) var(--space-md) var(--space-sm); }
.title { font-size: var(--text-body); font-weight: 600; color: var(--text); }
.meta { font-size: var(--text-caption); color: var(--text-muted); margin-top: 2px; }

/* 附属图区域 */
.extras {
  display: flex; gap: var(--space-sm);
  padding: 0 var(--space-md) var(--space-md);
}
.extra-badge {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 4px 8px; border-radius: var(--radius-full);
  background: #f0eee9; color: var(--text-secondary, #666);
  font-size: 12px; font-weight: 500;
}
.extra-badge svg { opacity: 0.6; }

/* skeleton */
.skeleton { pointer-events: none; }
.thumb-skel { aspect-ratio: 2 / 1; background: #eeece8; animation: shimmer 1.5s infinite; }
.info-skel { padding: var(--space-sm) var(--space-md) var(--space-sm); }
.line { height: 10px; border-radius: var(--radius-sm); background: #eeece8; margin-bottom: var(--space-xs); animation: shimmer 1.5s infinite; }
.w-60 { width: 60%; } .w-40 { width: 40%; }
@keyframes shimmer { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }

/* 状态 */
.state {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: var(--space-sm); padding: 80px var(--space-lg);
  color: var(--text-faint);
}
.state p { font-size: var(--text-body-sm); }
.state .hint { font-size: var(--text-caption); opacity: 0.7; }
.retry {
  margin-top: var(--space-sm); border: 1px solid var(--divider); background: var(--surface);
  color: var(--accent); padding: var(--space-sm) var(--space-lg);
  border-radius: var(--radius-full); font-size: var(--text-body-sm); cursor: pointer;
  transition: background var(--duration-fast) var(--ease-out);
}
.retry:active { background: var(--accent-soft); }

/* transitions */
.expand-enter-active, .expand-leave-active {
  transition: max-height var(--duration-normal) var(--ease-out), opacity var(--duration-normal) var(--ease-out);
  overflow: hidden;
}
.expand-enter-from, .expand-leave-to { max-height: 0; opacity: 0; }
.expand-enter-to, .expand-leave-from { max-height: 500px; opacity: 1; }

@media (max-width: 600px) {
  .grid { grid-template-columns: 1fr; }
  .header-inner { padding: var(--space-md); }
}
</style>
