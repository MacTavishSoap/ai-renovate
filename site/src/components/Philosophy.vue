<script setup>
import { reduce, stats } from '../data'
</script>

<template>
  <section class="section philosophy" id="philosophy">
    <div class="wrap">
      <p class="eyebrow reveal"><span>01</span> PHILOSOPHY · 设计理念</p>
      <h2 class="statement reveal" style="--d:.1s">
        我们不堆砌材料，只处理光、比例与秩序。<br>
        让每一处细节，都值得被长久地使用。
      </h2>
      <dl class="stats">
        <div v-for="(s, i) in stats" :key="s.label" class="reveal" :style="{ '--d': `${i * 0.12}s` }">
          <dt>{{ s.label }}</dt>
          <dd>
            <b :data-count="s.value">{{ reduce ? s.value : 0 }}</b>
            <sup v-if="s.plus">+</sup>
            <span class="unit">{{ s.unit }}</span>
          </dd>
        </div>
      </dl>
    </div>
  </section>
</template>
