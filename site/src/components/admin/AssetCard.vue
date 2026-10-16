<script setup>
import { computed } from 'vue'
import Icon from './Icon.vue'
import { coverUrl, current, customerLabel, customerOf, fmtDay, lookFilter } from '../../admin/store'

const props = defineProps({ asset: { type: Object, required: true }, visitor: Boolean })
defineEmits(['open'])

const cur = computed(() => current(props.asset))
const label = computed(() => customerLabel(props.asset, props.visitor))
const hidden = computed(() => props.visitor && !!customerOf(props.asset)?.private)
</script>

<template>
  <button type="button" class="ad-card" @click="$emit('open', asset)">
    <span class="ad-card__shot">
      <img :src="coverUrl(asset)" :alt="asset.name" loading="lazy" :style="{ filter: lookFilter(cur.looks) }" />
      <span class="ad-card__ver">第 {{ cur.n }} 版</span>
      <span class="ad-card__go">查看详情</span>
    </span>
    <span class="ad-card__body">
      <span class="ad-card__name">{{ asset.name }}</span>
      <span class="ad-card__meta">
        <span class="ad-card__cust" :class="{ 'is-hidden': hidden }"><Icon v-if="hidden" name="lock" />{{ label }}</span>
        <span>{{ fmtDay(cur.at) }}</span>
      </span>
    </span>
  </button>
</template>
