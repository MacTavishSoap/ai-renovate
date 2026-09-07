<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getGeneration } from '@/api/generations'

const route = useRoute()
const generation = ref(null)

onMounted(async () => {
  try {
    generation.value = await getGeneration(route.params.id)
  } catch {
    // 开发期占位
  }
})
</script>

<template>
  <div class="compare-page">
    <van-nav-bar title="原图 vs 效果图" />

    <div v-if="generation" class="compare-container">
      <div class="compare-item">
        <div class="compare-label">原图</div>
        <img
          v-if="generation.input_image_url"
          :src="generation.input_image_url"
          alt="原图"
        />
        <van-empty v-else description="无原图" />
      </div>
      <div class="compare-item">
        <div class="compare-label">效果图</div>
        <img
          v-if="generation.output_image_url"
          :src="generation.output_image_url"
          alt="效果图"
        />
        <van-empty v-else description="生成中..." />
      </div>
    </div>

    <van-loading v-else class="loading" type="spinner" />
  </div>
</template>

<style scoped>
.compare-page {
  min-height: 100vh;
}

.compare-container {
  display: flex;
  gap: 2px;
  padding: 0;
}

.compare-item {
  flex: 1;
  position: relative;
}

.compare-label {
  position: absolute;
  top: 8px;
  left: 8px;
  z-index: 1;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
}

.compare-item img {
  width: 100%;
  height: auto;
}

.loading {
  display: flex;
  justify-content: center;
  padding: 60px 0;
}
</style>
