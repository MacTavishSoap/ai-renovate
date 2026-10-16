<script setup>
import { ref } from 'vue'
import { reduce } from '../data'
import { jump } from '../jump'

const hero = ref(null)
const flute = ref(null)
const lit = ref(false)
const bars = Array.from({ length: 24 }, (_, i) => i)

function move(e) {
  if (reduce || !hero.value || !flute.value) return
  const r = hero.value.getBoundingClientRect()
  flute.value.style.setProperty('--mx', `${e.clientX - r.left}px`)
  flute.value.style.setProperty('--my', `${e.clientY - r.top}px`)
  lit.value = true
}

function leave() {
  lit.value = false
}
</script>

<template>
  <section ref="hero" class="hero" aria-label="首屏" @pointermove="move" @pointerleave="leave">
    <div class="hero__media" aria-hidden="true">
      <div class="scene scene--hero"></div>
      <div ref="flute" class="flute flute--hero" :class="{ 'is-lit': lit }"></div>
      <div class="hero__shade"></div>
    </div>

    <div v-if="!reduce" class="curtain" aria-hidden="true">
      <i v-for="i in bars" :key="i" :style="{ '--i': i }"></i>
    </div>

    <div class="hero__inner">
      <p class="eyebrow hero__in" style="--d:1.0s">DESIGN &amp; RENOVATION STUDIO</p>
      <h1 class="wordmark fluted-text hero__in" style="--d:1.15s">FORTUNE<span class="sr-only"> 空间设计与整装</span></h1>
      <div class="hero__row hero__in" style="--d:1.35s">
        <p class="hero__zh">空间，是一种缓慢的奢侈</p>
        <div class="hero__cta">
          <a class="btn" href="#contact" @click="jump">预约免费量房</a>
          <a class="link" href="#works" @click="jump">浏览案例</a>
        </div>
      </div>
      <div class="hero__meta hero__in" style="--d:1.5s">
        <span>全案设计 · 整装施工 · 软装陈设</span>
        <span class="scroll" aria-hidden="true">SCROLL</span>
      </div>
    </div>
  </section>
</template>
