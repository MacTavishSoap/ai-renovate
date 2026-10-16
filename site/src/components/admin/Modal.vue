<script setup>
import { onMounted, onUnmounted } from 'vue'
import Icon from './Icon.vue'

defineProps({ title: String, width: { type: Number, default: 440 } })
const emit = defineEmits(['close'])

const esc = (e) => {
  if (e.key === 'Escape') emit('close')
}
onMounted(() => addEventListener('keydown', esc))
onUnmounted(() => removeEventListener('keydown', esc))
</script>

<template>
  <Teleport to="body">
    <div class="ad-modal" @pointerdown.self="emit('close')">
      <div class="ad-modal__box" role="dialog" aria-modal="true" :aria-label="title" :style="{ width: width + 'px' }">
        <header class="ad-modal__head">
          <h2>{{ title }}</h2>
          <button type="button" class="ad-x" aria-label="关闭" @click="emit('close')"><Icon name="close" /></button>
        </header>
        <div class="ad-modal__body"><slot /></div>
        <footer v-if="$slots.foot" class="ad-modal__foot"><slot name="foot" /></footer>
      </div>
    </div>
  </Teleport>
</template>
