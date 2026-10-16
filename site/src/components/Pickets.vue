<script setup>
import { pickets, reduce } from '../data'

const N = pickets.length

function wave(e) {
  if (reduce) return
  const el = e.currentTarget
  const r = el.getBoundingClientRect()
  const x = (e.clientX - r.left) / r.width
  ;[...el.children].forEach((b, i) => {
    const k = Math.max(0, 1 - Math.abs(i / (N - 1) - x) * 7)
    b.style.transform = `scaleY(${1 + k * 0.55})`
  })
}

function reset(e) {
  ;[...e.currentTarget.children].forEach((b) => (b.style.transform = ''))
}
</script>

<template>
  <div class="pickets" aria-hidden="true" @pointermove="wave" @pointerleave="reset">
    <i v-for="p in pickets" :key="p.i" :style="{ '--h': p.h, '--i': p.i }"></i>
  </div>
</template>
