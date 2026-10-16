<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import PanoViewer from './PanoViewer.vue'
import PlanViewer from './PlanViewer.vue'
import Switch from './Switch.vue'
import Modal from './Modal.vue'
import Icon from './Icon.vue'
import CustomerModal from './CustomerModal.vue'
import { reduce } from '../../data'
import {
  applyLook, assignCustomer, can, coverUrl, current, customerLabel, customerOf, customers, fmt,
  LOOKS, lookFilter, maskName, rollbackTo, setCustomerPrivacy, setVisibility, staffName, toast,
} from '../../admin/store'

const props = defineProps({ asset: { type: Object, required: true } })
const emit = defineEmits(['close'])

const cur = computed(() => current(props.asset))
const sel = ref(cur.value.n) // 正在查看的版本号
const selVer = computed(() => props.asset.versions.find((v) => v.n === sel.value) ?? cur.value)
const preview = computed(() => selVer.value.n !== cur.value.n)
const filter = computed(() => lookFilter(selVer.value.looks))
const cust = computed(() => customerOf(props.asset))
const isPublic = computed(() => props.asset.visibility === 'public')

/* ---------- 修改记录 ---------- */
const film = ref(null)
watch(sel, () => nextTick(() => film.value?.querySelector('.is-sel')?.scrollIntoView({ block: 'nearest', inline: 'nearest' })))

function restore(v) {
  if (!can('asset.rollback')) return
  rollbackTo(props.asset, v)
  sel.value = current(props.asset).n
  toast(`已恢复到第 ${v.n} 版,所有历史版本都还在`)
}

/* ---------- 继续修改 ---------- */
const pick = ref('')
const busy = ref(false)

function regenerate() {
  if (!pick.value || busy.value || !can('studio.generate')) return
  const base = selVer.value
  const key = pick.value
  busy.value = true
  setTimeout(() => {
    applyLook(props.asset, base, key)
    sel.value = current(props.asset).n
    busy.value = false
    pick.value = ''
    toast(`已生成第 ${sel.value} 版(${LOOKS[key].label}),之前的版本都还在`)
  }, reduce ? 0 : 1200)
}

/* ---------- 属于哪位客户 ---------- */
const showNewCust = ref(false)

function onCust(e) {
  const v = e.target.value
  if (v === '__new') {
    e.target.value = props.asset.customerId ?? ''
    showNewCust.value = true
    return
  }
  assignCustomer(props.asset, v ? Number(v) : null)
  toast(v ? `已归属到「${customerOf(props.asset).name}」` : '已取消客户归属')
}
const onNewCust = (c) => assignCustomer(props.asset, c.id)

function setHide(v) {
  setCustomerPrivacy(cust.value.id, v)
  toast(v ? `已隐藏「${cust.value.name}」的真实姓名` : `已显示「${cust.value.name}」的真实姓名`)
}
const shownName = (c) => (c.private ? maskName(c.name) : c.name)

/* ---------- 谁能看到 ---------- */
const showPub = ref(false)
const pubLabel = computed(() => (cust.value ? shownName(cust.value) : '样板展示'))

function toVisibility(v) {
  if (!can('asset.publicize') || props.asset.visibility === v) return
  if (v === 'public') { showPub.value = true; return }
  setVisibility(props.asset, 'private')
  toast('已改为客户专属,只有内部员工能看到')
}
function confirmPublic() {
  setVisibility(props.asset, 'public')
  showPub.value = false
  toast('已设为对外展示')
}

/* ---------- 抽屉自身 ---------- */
const onKey = (e) => {
  if (e.key === 'Escape' && !document.querySelector('.ad-modal')) emit('close')
}
onMounted(() => {
  addEventListener('keydown', onKey)
  document.body.style.overflow = 'hidden'
})
onUnmounted(() => {
  removeEventListener('keydown', onKey)
  document.body.style.overflow = ''
})
</script>

<template>
  <div class="ad-drawer" @pointerdown.self="emit('close')">
    <aside class="ad-drawer__panel" role="dialog" aria-modal="true" :aria-label="asset.name">
      <header class="ad-drawer__head">
        <div>
          <h2>{{ asset.name }}</h2>
          <p class="ad-tags">
            <span class="ad-tag" :class="isPublic ? 'is-public' : 'is-private'">
              <Icon :name="isPublic ? 'globe' : 'lock'" />{{ isPublic ? '对外展示' : '客户专属' }}
            </span>
            <span class="ad-tag">{{ customerLabel(asset, false) }}</span>
            <span class="ad-tag">共 {{ asset.versions.length }} 版</span>
          </p>
        </div>
        <button type="button" class="ad-x" aria-label="关闭" @click="emit('close')"><Icon name="close" /></button>
      </header>

      <div class="ad-drawer__body">
        <!-- 左:3D 画面 + 修改记录 -->
        <div class="ad-col">
          <div class="ad-stage">
            <PanoViewer v-if="asset.kind === 'pano'" :pano-id="asset.ref" :filter="filter" />
            <PlanViewer v-else :filter="filter" />
            <div v-if="busy" class="ad-stage__busy"><i></i><span>正在生成新的一版…</span></div>
          </div>

          <div class="ad-now" :class="{ 'is-preview': preview }">
            <template v-if="preview">
              <span>正在查看 <b>第 {{ selVer.n }} 版</b>,这不是最新版</span>
              <span class="ad-now__acts">
                <button v-if="can('asset.rollback')" type="button" class="ad-btn ad-btn--sm" @click="restore(selVer)"><Icon name="undo" />恢复到这一版</button>
                <span v-else class="ad-lock"><Icon name="lock" />无权限恢复</span>
                <button type="button" class="ad-btn ad-btn--sm ad-btn--ghost" @click="sel = cur.n">回到最新版</button>
              </span>
            </template>
            <span v-else>当前使用 <b>第 {{ cur.n }} 版</b> · {{ cur.note }}</span>
          </div>

          <section>
            <h3 class="ad-h3">修改记录<small>点击可预览</small></h3>
            <ol ref="film" class="ad-film">
              <li v-for="v in asset.versions" :key="v.n">
                <button type="button" class="ad-film__item" :class="{ 'is-sel': v.n === sel }" @click="sel = v.n">
                  <span class="ad-film__img">
                    <img :src="coverUrl(asset)" :alt="`第 ${v.n} 版`" :style="{ filter: lookFilter(v.looks) }" />
                    <em v-if="v.n === cur.n">使用中</em>
                  </span>
                  <span class="ad-film__cap"><b>第 {{ v.n }} 版</b><small>{{ v.note }}</small></span>
                  <span class="ad-film__by">{{ staffName(v.by) }} · {{ fmt(v.at) }}</span>
                </button>
              </li>
            </ol>
          </section>
        </div>

        <!-- 右:三步操作 -->
        <div class="ad-col">
          <section class="ad-step">
            <h3 class="ad-step__t"><i>1</i>属于哪位客户<span v-if="!can('customer.add')" class="ad-lock"><Icon name="lock" />无权限</span></h3>
            <select class="ad-select" :value="asset.customerId ?? ''" :disabled="!can('customer.add')" @change="onCust">
              <option value="">未指定客户</option>
              <option v-for="c in customers" :key="c.id" :value="c.id">{{ c.name }}</option>
              <option v-if="can('customer.add')" value="__new">＋ 添加新客户…</option>
            </select>
            <div v-if="cust" class="ad-row ad-row--box">
              <div>
                <strong>隐藏真实姓名</strong>
                <p class="ad-sub">对外显示为 <b class="ad-mono">{{ shownName(cust) }}</b></p>
              </div>
              <span v-if="!can('customer.privacy')" class="ad-lock"><Icon name="lock" />无权限</span>
              <Switch v-else :model-value="cust.private" label="隐藏真实姓名" @update:model-value="setHide" />
            </div>
          </section>

          <section class="ad-step">
            <h3 class="ad-step__t"><i>2</i>谁能看到<span v-if="!can('asset.publicize')" class="ad-lock"><Icon name="lock" />无权限</span></h3>
            <div class="ad-opt" role="group" aria-label="谁能看到">
              <button type="button" :class="{ 'is-on': !isPublic }" :disabled="!can('asset.publicize')" @click="toVisibility('private')">
                <Icon name="lock" /><strong>客户专属</strong><small>仅内部员工</small>
              </button>
              <button type="button" :class="{ 'is-on': isPublic }" :disabled="!can('asset.publicize')" @click="toVisibility('public')">
                <Icon name="globe" /><strong>对外展示</strong><small>所有人可见</small>
              </button>
            </div>
          </section>

          <section class="ad-step">
            <h3 class="ad-step__t"><i>3</i>继续修改<span v-if="!can('studio.generate')" class="ad-lock"><Icon name="lock" />无权限</span></h3>
            <div class="ad-chips">
              <button v-for="(l, k) in LOOKS" :key="k" type="button" class="ad-chipbtn" :class="{ 'is-on': pick === k }"
                      :disabled="!can('studio.generate') || busy" @click="pick = pick === k ? '' : k">{{ l.label }}</button>
            </div>
            <button type="button" class="ad-btn ad-btn--block" :disabled="!pick || busy || !can('studio.generate')" @click="regenerate">
              {{ busy ? '生成中…' : pick ? `生成新一版 · ${LOOKS[pick].label}` : '先选一种效果' }}
            </button>
          </section>
        </div>
      </div>
    </aside>

    <Modal v-if="showPub" title="设为对外展示" @close="showPub = false">
      <div class="ad-confirm">
        <img :src="coverUrl(asset)" :alt="asset.name" :style="{ filter }" />
        <div>
          <p class="ad-sub">访客将看到</p>
          <strong class="ad-big">{{ pubLabel }}</strong>
          <p class="ad-sub">{{ asset.name }}</p>
        </div>
      </div>
      <div v-if="cust" class="ad-row ad-row--box">
        <strong>隐藏「{{ cust.name }}」的真实姓名</strong>
        <span v-if="!can('customer.privacy')" class="ad-lock"><Icon name="lock" />无权限</span>
        <Switch v-else :model-value="cust.private" label="隐藏真实姓名" @update:model-value="setHide" />
      </div>
      <template #foot>
        <button type="button" class="ad-btn ad-btn--ghost" @click="showPub = false">取消</button>
        <button type="button" class="ad-btn" @click="confirmPublic">确认对外展示</button>
      </template>
    </Modal>

    <CustomerModal v-if="showNewCust" @close="showNewCust = false" @done="onNewCust" />
  </div>
</template>
