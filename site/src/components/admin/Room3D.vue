<script setup>
// 纯 CSS 3D 的"房间盒子":后墙 + 左右墙 + 地面 + 天花 + 一件立体家具。
// 数据来自 scene 参数,接入真实生图后,这里换成模型/全景图查看器即可。
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { sceneVars } from '../../admin/scene'
import { reduce } from '../../data'

const props = defineProps({ scene: { type: Object, required: true } })

const W = 620 // 房间宽(与 admin.css 中的 --RW 对应)
const H = 340
const D = 520
const BASE_Y = -14
const BASE_X = 6

const vars = computed(() => {
  const s = props.scene
  const bw = (s.fw / 100) * W
  const bh = (s.fh / 100) * (H / 0.68)
  const bd = Math.max(80, bw * 0.42)
  return {
    ...sceneVars(s),
    '--bw': `${bw}px`,
    '--bh': `${bh}px`,
    '--bd': `${bd}px`,
    '--cx': `${-W / 2 + ((s.fx + s.fw / 2) / 100) * W}px`,
    '--cz': `${-D / 2 + bd / 2 + 26}px`,
  }
})

const stage = ref(null)
const k = ref(1)
const ry = ref(BASE_Y)
const rx = ref(BASE_X)

let ro, raf
let ty = BASE_Y // 用户给的目标角度
let tx = BASE_X
let cy = BASE_Y // 平滑后的当前角度
let cx = BASE_X
let amp = reduce ? 0 : 7 // 空闲时的缓慢摆动幅度
let dragging = false
let sx = 0
let sy = 0
let by = 0
let bx = 0

const clamp = (v, a, b) => Math.min(b, Math.max(a, v))

function down(e) {
  dragging = true
  sx = e.clientX
  sy = e.clientY
  by = ty
  bx = tx
  e.currentTarget.setPointerCapture?.(e.pointerId)
}
function move(e) {
  if (!dragging) return
  ty = clamp(by + (e.clientX - sx) * 0.2, -34, 34)
  tx = clamp(bx - (e.clientY - sy) * 0.12, -6, 18)
}
function up() {
  dragging = false
}
function reset() {
  ty = BASE_Y
  tx = BASE_X
}

function loop(t) {
  const goal = reduce || dragging ? 0 : 7
  amp += (goal - amp) * 0.05
  cy += (ty + Math.sin(t / 2600) * amp - cy) * 0.14
  cx += (tx + Math.cos(t / 3100) * amp * 0.25 - cx) * 0.14
  ry.value = cy
  rx.value = cx
  raf = requestAnimationFrame(loop)
}

onMounted(() => {
  const fit = () => { k.value = stage.value.clientWidth / 640 }
  fit()
  ro = new ResizeObserver(fit)
  ro.observe(stage.value)
  raf = requestAnimationFrame(loop)
})
onUnmounted(() => {
  ro?.disconnect()
  cancelAnimationFrame(raf)
})
</script>

<template>
  <div
    ref="stage"
    class="room"
    :style="vars"
    role="img"
    aria-label="可拖动旋转的 3D 空间预览"
    @pointerdown="down"
    @pointermove="move"
    @pointerup="up"
    @pointercancel="up"
    @dblclick="reset"
  >
    <div class="room__cam" :style="{ '--k': k }">
      <div class="room__box" :style="{ transform: `translateZ(-60px) rotateX(${rx}deg) rotateY(${ry}deg)` }">
        <div class="rf rf--back"><div class="scene"></div></div>
        <div class="rf rf--left"></div>
        <div class="rf rf--right"></div>
        <div class="rf rf--floor"></div>
        <div class="rf rf--ceil"></div>

        <div class="fbox">
          <i class="ff ff--s"></i>
          <i class="ff ff--f"></i>
          <i class="ff ff--b"></i>
          <i class="ff ff--l"></i>
          <i class="ff ff--r"></i>
          <i class="ff ff--t"></i>
        </div>
      </div>
    </div>
    <p class="room__hint">拖动旋转 · 双击复位</p>
  </div>
</template>
