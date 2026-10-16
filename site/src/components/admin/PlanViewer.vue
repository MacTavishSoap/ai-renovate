<script setup>
// 3D 户型图查看器:沿用项目 manifest 里的「3D 效果图」(正面 / 左 90° / 右 90° / 右 180° / 原始户型)。
import { computed, onMounted, ref } from 'vue'
import { getEffectItemUrl, getEffects, loadManifest } from '@frontend/api/pano'

defineProps({ filter: { type: String, default: 'none' } })

const list = ref([])
const idx = ref(0)

// manifest 里这张图叫「参考示例」,实际是原始平面户型图,换成人能看懂的名字
const NAME = { 'effect_reference.jpg': '原始户型图' }
const views = computed(() => list.value.map((e) => ({ ...e, label: NAME[e.file] || e.label })))
const cur = computed(() => views.value[idx.value])

onMounted(async () => {
  const pano = (await loadManifest()).find((p) => (p.effects || []).length)
  list.value = pano ? getEffects(pano) : []
})
</script>

<template>
  <div class="plan">
    <div class="plan__stage">
      <img v-if="cur" :key="cur.file" :src="getEffectItemUrl(cur.file)" :alt="cur.label" :style="{ filter: cur.file === 'effect_reference.jpg' ? 'none' : filter }" />
    </div>
    <div class="plan__tabs" role="tablist" aria-label="查看角度">
      <button v-for="(v, i) in views" :key="v.file" type="button" role="tab" :aria-selected="i === idx"
              :class="{ 'is-on': i === idx }" @click="idx = i">{{ v.label }}</button>
    </div>
  </div>
</template>
