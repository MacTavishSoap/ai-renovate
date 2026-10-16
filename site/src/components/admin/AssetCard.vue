<script setup>
import { computed } from 'vue'
import SceneThumb from './SceneThumb.vue'
import Icon from './Icon.vue'
import { current, customerLabel, customerOf, fmt } from '../../admin/store'

const props = defineProps({ asset: { type: Object, required: true }, publicView: Boolean })
defineEmits(['open'])

const cur = computed(() => current(props.asset))
const label = computed(() => customerLabel(props.asset, props.publicView))
const masked = computed(() => props.publicView && !!customerOf(props.asset)?.private)
</script>

<template>
  <button type="button" class="ad-card" @click="$emit('open', asset)">
    <span class="ad-card__shot">
      <SceneThumb :scene="cur.scene" />
      <span class="ad-card__ver">v{{ cur.n }}</span>
      <span class="ad-card__tag">{{ asset.visibility === 'public' ? '公共演示' : '私人' }}</span>
    </span>
    <span class="ad-card__body">
      <span class="ad-card__name">{{ asset.name }}</span>
      <span class="ad-card__meta">
        <span class="ad-card__cust" :class="{ 'is-masked': masked }">
          <Icon v-if="masked" name="lock" />{{ label }}
        </span>
        <span>{{ fmt(cur.at) }}</span>
      </span>
    </span>
  </button>
</template>
