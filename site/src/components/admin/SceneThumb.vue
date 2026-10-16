<script setup>
import { computed } from 'vue'
import { sceneVars } from '../../admin/scene'

const props = defineProps({ scene: { type: Object, required: true } })
const vars = computed(() => sceneVars(props.scene))
</script>

<template>
  <div class="thumb" :style="vars">
    <div class="scene"><i class="obj"></i></div>
    <div class="flute"></div>
  </div>
</template>
