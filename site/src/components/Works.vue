<script setup>
import { works } from '../data'
import Pickets from './Pickets.vue'
</script>

<template>
  <section class="section works" id="works">
    <Pickets />
    <div class="wrap">
      <div class="section__head">
        <div>
          <p class="eyebrow reveal"><span>02</span> SELECTED WORKS · 精选案例</p>
          <h2 class="h2 reveal" style="--d:.1s">被光线与材质<br>慢慢写成的家</h2>
        </div>
        <a class="link reveal" style="--d:.2s" href="#" @click.prevent>全部案例 →</a>
      </div>
      <div class="works__grid">
        <article
          v-for="work in works"
          :key="work.no"
          class="work reveal"
          :class="work.slot"
          :style="work.delay ? { '--d': work.delay } : undefined"
        >
          <a class="work__link" href="#" @click.prevent>
            <figure class="shot">
              <div class="scene" :class="work.scene"><span class="obj"></span></div>
              <div class="flute"></div>
            </figure>
            <div class="work__cap">
              <span class="work__no">{{ work.no }}</span>
              <div>
                <h3>{{ work.name }}</h3>
                <p>{{ work.meta }}</p>
              </div>
              <span class="work__arrow" aria-hidden="true">→</span>
            </div>
          </a>
        </article>
      </div>
    </div>
  </section>
</template>
