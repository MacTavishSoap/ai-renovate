<script setup>
import Pickets from './Pickets.vue'

const info = [
  { label: '电话', value: '400-000-0000' },
  { label: '邮箱', value: 'hello@fortune.example' },
  { label: '地址', value: '示例市示例路 88 号' },
]
</script>

<template>
  <section class="section contact" id="contact">
    <Pickets />
    <div class="wrap">
      <p class="eyebrow reveal"><span>03</span> CONTACT · 预约</p>
      <h2 class="cta__title reveal" style="--d:.1s">让下一处空间，<br>从一次量房开始</h2>
      <div class="cta__row reveal" style="--d:.2s">
        <a class="btn btn--lg" href="tel:4000000000">预约免费量房</a>
        <dl class="contact__info">
          <div v-for="item in info" :key="item.label">
            <dt>{{ item.label }}</dt>
            <dd>{{ item.value }}</dd>
          </div>
        </dl>
      </div>
    </div>
  </section>
</template>
