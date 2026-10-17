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
        <figure class="contact__wx">
          <svg viewBox="0 0 25 25" role="img" aria-label="微信二维码">
            <rect width="25" height="25" fill="#fff" />
            <path fill="#1c1916" fill-rule="evenodd" d="M2 2h7v7h-7zM3 3h5v5h-5zM4 4h3v3h-3zM16 2h7v7h-7zM17 3h5v5h-5zM18 4h3v3h-3zM2 16h7v7h-7zM3 17h5v5h-5zM4 18h3v3h-3zM10 2h1v1h-1zM11 2h1v1h-1zM15 2h1v1h-1zM9 3h1v1h-1zM11 3h1v1h-1zM12 3h1v1h-1zM14 3h1v1h-1zM15 3h1v1h-1zM9 4h1v1h-1zM11 4h1v1h-1zM13 4h1v1h-1zM14 4h1v1h-1zM12 5h1v1h-1zM14 5h1v1h-1zM11 6h1v1h-1zM12 6h1v1h-1zM9 7h1v1h-1zM10 7h1v1h-1zM11 7h1v1h-1zM12 7h1v1h-1zM13 7h1v1h-1zM15 7h1v1h-1zM11 8h1v1h-1zM12 8h1v1h-1zM13 8h1v1h-1zM2 9h1v1h-1zM3 9h1v1h-1zM5 9h1v1h-1zM9 9h1v1h-1zM10 9h1v1h-1zM11 9h1v1h-1zM12 9h1v1h-1zM15 9h1v1h-1zM18 9h1v1h-1zM21 9h1v1h-1zM5 10h1v1h-1zM7 10h1v1h-1zM8 10h1v1h-1zM9 10h1v1h-1zM17 10h1v1h-1zM18 10h1v1h-1zM21 10h1v1h-1zM3 11h1v1h-1zM6 11h1v1h-1zM8 11h1v1h-1zM9 11h1v1h-1zM15 11h1v1h-1zM16 11h1v1h-1zM17 11h1v1h-1zM19 11h1v1h-1zM20 11h1v1h-1zM2 12h1v1h-1zM4 12h1v1h-1zM9 12h1v1h-1zM15 12h1v1h-1zM16 12h1v1h-1zM19 12h1v1h-1zM20 12h1v1h-1zM21 12h1v1h-1zM22 12h1v1h-1zM2 13h1v1h-1zM5 13h1v1h-1zM6 13h1v1h-1zM9 13h1v1h-1zM16 13h1v1h-1zM17 13h1v1h-1zM18 13h1v1h-1zM2 14h1v1h-1zM4 14h1v1h-1zM5 14h1v1h-1zM6 14h1v1h-1zM7 14h1v1h-1zM8 14h1v1h-1zM9 14h1v1h-1zM16 14h1v1h-1zM18 14h1v1h-1zM19 14h1v1h-1zM20 14h1v1h-1zM21 14h1v1h-1zM22 14h1v1h-1zM2 15h1v1h-1zM3 15h1v1h-1zM4 15h1v1h-1zM5 15h1v1h-1zM6 15h1v1h-1zM8 15h1v1h-1zM9 15h1v1h-1zM14 15h1v1h-1zM15 15h1v1h-1zM19 15h1v1h-1zM20 15h1v1h-1zM10 16h1v1h-1zM13 16h1v1h-1zM14 16h1v1h-1zM15 16h1v1h-1zM21 16h1v1h-1zM22 16h1v1h-1zM9 17h1v1h-1zM10 17h1v1h-1zM17 17h1v1h-1zM20 17h1v1h-1zM21 17h1v1h-1zM22 17h1v1h-1zM9 18h1v1h-1zM17 18h1v1h-1zM21 18h1v1h-1zM22 18h1v1h-1zM9 19h1v1h-1zM10 19h1v1h-1zM11 19h1v1h-1zM12 19h1v1h-1zM21 19h1v1h-1zM9 20h1v1h-1zM10 20h1v1h-1zM11 20h1v1h-1zM12 20h1v1h-1zM13 20h1v1h-1zM20 20h1v1h-1zM13 21h1v1h-1zM16 21h1v1h-1zM17 21h1v1h-1zM18 21h1v1h-1zM20 21h1v1h-1zM22 21h1v1h-1zM9 22h1v1h-1zM11 22h1v1h-1zM17 22h1v1h-1zM18 22h1v1h-1zM19 22h1v1h-1zM20 22h1v1h-1z" />
            <circle cx="12.5" cy="12.5" r="3.2" fill="#fff" />
            <path fill="#07C160" d="M10.7 10.6c-1.35 0-2.45.9-2.45 2.02 0 .62.34 1.17.88 1.54l-.28.84.86-.43c.3.08.62.13.96.13.1 0 .2 0 .3-.01-.08-.22-.12-.45-.12-.7 0-1.2 1.15-2.17 2.58-2.17.08 0 .16 0 .24.01-.28-.72-1.4-1.23-2.97-1.23zm-.7 1.15a.32.32 0 110 .64.32.32 0 010-.64zm1.45 0a.32.32 0 110 .64.32.32 0 010-.64zM14.55 11.7c-1.28 0-2.32.86-2.32 1.92s1.04 1.92 2.32 1.92c.27 0 .53-.03.77-.1l.92.46-.23-.78c.46-.34.76-.83.76-1.5 0-1.06-1.04-1.92-2.22-1.92zm-.72.95a.28.28 0 110 .56.28.28 0 010-.56zm1.35 0a.28.28 0 110 .56.28.28 0 010-.56z" />
          </svg>
          <figcaption>微信</figcaption>
        </figure>
      </div>
    </div>
  </section>
</template>
