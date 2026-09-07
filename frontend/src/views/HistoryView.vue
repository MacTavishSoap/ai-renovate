<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { listGenerations } from '@/api/generations'

const router = useRouter()
const list = ref([])
const loading = ref(false)
const finished = ref(false)
const page = ref(0)

const STATUS_MAP = {
  pending: { text: '排队中', color: 'var(--warning)' },
  processing: { text: '生成中', color: 'var(--accent)' },
  done: { text: '已完成', color: 'var(--success)' },
  failed: { text: '失败', color: 'var(--error)' },
}

async function onLoad() {
  if (finished.value) return
  loading.value = true
  try {
    const res = await listGenerations(page.value * 20, 20)
    list.value.push(...res.items)
    page.value++
    if (list.value.length >= res.total) finished.value = true
  } catch {
    finished.value = true
  } finally {
    loading.value = false
  }
}

function goPano(id) {
  router.push(`/pano/${id}`)
}

onMounted(() => onLoad())
</script>

<template>
  <div class="history-page">
    <header class="page-header">
      <h1 class="page-title">生成历史</h1>
    </header>

    <!-- 空状态 -->
    <div v-if="!loading && list.length === 0" class="empty-state">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
        <rect x="3" y="3" width="18" height="18" rx="2" />
        <circle cx="9" cy="9" r="2" />
        <path d="M21 15l-5-5L5 21" />
      </svg>
      <p class="empty-text">还没有生成记录</p>
      <button class="empty-action" @click="router.push('/generate')">去生成第一张</button>
    </div>

    <!-- 列表 -->
    <div v-else class="list">
      <div
        v-for="item in list"
        :key="item.id"
        class="card"
        @click="item.type === 'pano' && item.status === 'done' ? goPano(item.id) : null"
      >
        <div class="card-thumb">
          <img v-if="item.output_image_url" :src="item.output_image_url" alt="" />
          <svg v-else width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="3" width="18" height="18" rx="2" />
            <circle cx="9" cy="9" r="2" />
            <path d="M21 15l-5-5L5 21" />
          </svg>
        </div>
        <div class="card-info">
          <div class="card-title">
            {{ item.type === 'pano' ? '全景图' : '效果图' }} #{{ item.id }}
          </div>
          <div class="card-meta">{{ item.created_at }}</div>
          <span class="card-status" :style="{ color: STATUS_MAP[item.status]?.color }">
            {{ STATUS_MAP[item.status]?.text || item.status }}
          </span>
        </div>
        <svg
          v-if="item.type === 'pano' && item.status === 'done'"
          class="card-arrow"
          width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
        >
          <path d="M9 18l6-6-6-6" />
        </svg>
      </div>

      <!-- 加载骨架 -->
      <div v-if="loading" class="skeleton-card">
        <div class="skeleton-thumb"></div>
        <div class="skeleton-info">
          <div class="skeleton-line w-60"></div>
          <div class="skeleton-line w-40"></div>
        </div>
      </div>

      <div v-if="finished && list.length > 0" class="list-end">没有更多了</div>
    </div>
  </div>
</template>

<style scoped>
.history-page {
  padding-bottom: var(--space-xl);
}

.page-header {
  padding: var(--space-lg) var(--space-md) var(--space-md);
}

.page-title {
  font-size: var(--text-h1);
  font-weight: 600;
  color: var(--text);
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-md);
  padding: 80px var(--space-md);
  color: var(--text-muted);
}

.empty-text {
  font-size: var(--text-body);
}

.empty-action {
  height: 36px;
  padding: 0 var(--space-lg);
  font-size: var(--text-body-sm);
  font-weight: 500;
  color: #fff;
  background: var(--accent);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  margin-top: var(--space-sm);
}

/* 列表 */
.list {
  padding: 0 var(--space-md);
}

.card {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  background: var(--surface);
  padding: var(--space-md);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  margin-bottom: var(--space-sm);
  cursor: pointer;
  transition: box-shadow var(--duration-fast) var(--ease-out);
}

.card:hover {
  box-shadow: var(--shadow-raised);
}

.card:active {
  transform: scale(0.99);
}

.card-thumb {
  width: 64px;
  height: 64px;
  border-radius: var(--radius-sm);
  overflow: hidden;
  background: var(--bg);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--divider);
  flex-shrink: 0;
}

.card-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-info {
  flex: 1;
  min-width: 0;
}

.card-title {
  font-size: var(--text-body);
  font-weight: 500;
  color: var(--text);
  margin-bottom: 4px;
}

.card-meta {
  font-size: var(--text-caption);
  color: var(--text-muted);
  margin-bottom: 6px;
}

.card-status {
  font-size: var(--text-caption);
  font-weight: 500;
}

.card-arrow {
  color: var(--text-muted);
  flex-shrink: 0;
}

/* 骨架 */
.skeleton-card {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  background: var(--surface);
  padding: var(--space-md);
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-sm);
}

.skeleton-thumb {
  width: 64px;
  height: 64px;
  border-radius: var(--radius-sm);
  background: var(--divider);
  animation: pulse 1.5s ease infinite;
}

.skeleton-info {
  flex: 1;
}

.skeleton-line {
  height: 14px;
  border-radius: var(--radius-sm);
  background: var(--divider);
  margin-bottom: var(--space-sm);
  animation: pulse 1.5s ease infinite;
}

.w-60 { width: 60%; }
.w-40 { width: 40%; }

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 0.3; }
}

.list-end {
  text-align: center;
  font-size: var(--text-caption);
  color: var(--text-muted);
  padding: var(--space-lg) 0;
}
</style>
