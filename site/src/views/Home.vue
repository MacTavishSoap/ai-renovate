<script setup>
import { onMounted, onUnmounted } from 'vue'
import { bindMotion } from '../motion'
import SiteNav from '../components/SiteNav.vue'
import Hero from '../components/Hero.vue'
import Philosophy from '../components/Philosophy.vue'
import Works from '../components/Works.vue'
import Contact from '../components/Contact.vue'
import SiteFoot from '../components/SiteFoot.vue'

let stop
onMounted(() => { stop = bindMotion() })
onUnmounted(() => stop?.())
</script>

<template>
  <div class="rails" aria-hidden="true"><i></i><i></i><i></i><i></i></div>
  <SiteNav />
  <main id="top">
    <Hero />
    <Philosophy />
    <Works />
    <Contact />
  </main>
  <SiteFoot />
</template>
