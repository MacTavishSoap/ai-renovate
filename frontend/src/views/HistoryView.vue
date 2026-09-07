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
  pending: { text: '排队中', color: '#ff976a' },
  processing: { text: '生成中', color: '#1989fa' },
  done: { text: '已完成', color: '#07c160' },
  failed: { text: '失败', color: '#ee0a24' },
}

async function onLoad() {
  if (finished.value) return
  loading.value = true
  try {
    const res = await listGenerations(page.value * 20, 20)
    list.value.push(...res.items)
    page.value++
    if (list.value.length >= res.total) {
      finished.value = true
    }
  } catch {
    finished.value = true
  } finally {
    loading.value = false
  }
}

function goPano(id) {
  router.push(`/pano/${id}`)
}

onMounted(() => {
  onLoad()
})
</script>

<template>
  <div class="history-page">
    <van-nav-bar title="生成历史" />

    <van-list
      v-model:loading="loading"
      :finished="finished"
      finished-text="没有更多了"
      @load="onLoad"
    >
      <div
        v-for="item in list"
        :key="item.id"
        class="history-card"
        @click="item.type === 'pano' && item.status === 'done' ? goPano(item.id) : null"
      >
        <div class="card-thumb">
          <img
            v-if="item.output_image_url"
            :src="item.output_image_url"
            alt="缩略图"
          />
          <van-icon v-else name="photo-o" size="40" color="#dcdee0" />
        </div>
        <div class="card-info">
          <div class="card-title">
            {{ item.type === 'pano' ? '全景图' : '效果图' }} #{{ item.id }}
          </div>
          <div class="card-meta">{{ item.created_at }}</div>
          <van-tag
            :color="STATUS_MAP[item.status]?.color"
            plain
            size="medium"
          >
            {{ STATUS_MAP[item.status]?.text || item.status }}
          </van-tag>
        </div>
        <van-icon
          v-if="item.type === 'pano' && item.status === 'done'"
          name="arrow"
          color="#c8c9cc"
        />
      </div>
    </van-list>
  </div>
</template>

<style scoped>
.history-page {
  min-height: 100vh;
}

.history-card {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #fff;
  margin: 8px 16px;
  padding: 12px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.card-thumb {
  width: 64px;
  height: 64px;
  border-radius: 6px;
  overflow: hidden;
  background: #f7f8fa;
  display: flex;
  align-items: center;
  justify-content: center;
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
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 4px;
}

.card-meta {
  font-size: 12px;
  color: #969799;
  margin-bottom: 6px;
}
</style>
