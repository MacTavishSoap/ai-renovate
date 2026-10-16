<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import Room3D from './Room3D.vue'
import Switch from './Switch.vue'
import Modal from './Modal.vue'
import Icon from './Icon.vue'
import CustomerModal from './CustomerModal.vue'
import { EDITS } from '../../admin/scene'
import { reduce } from '../../data'
import {
  addVersion, assignCustomer, can, current, customerOf, customers, fmt, maskName,
  rollbackTo, setCustomerPrivacy, setVisibility, staffName, toast,
} from '../../admin/store'

const props = defineProps({ asset: { type: Object, required: true } })
const emit = defineEmits(['close'])

const cur = computed(() => current(props.asset))
const sel = ref(cur.value.n) // 正在查看的版本号
const selVer = computed(() => props.asset.versions.find((v) => v.n === sel.value) ?? cur.value)
const preview = computed(() => selVer.value.n !== cur.value.n)
const timeline = computed(() => [...props.asset.versions].reverse())

const cust = computed(() => customerOf(props.asset))
const isPublic = computed(() => props.asset.visibility === 'public')

/* ---------- 版本 ---------- */
function rollback(v) {
  if (!can('asset.rollback')) return
  rollbackTo(props.asset, v)
  sel.value = current(props.asset).n
  toast(`已回溯至 v${v.n},生成新版本 v${sel.value}(历史完整保留)`)
}

/* ---------- 再次编辑 ---------- */
const pick = ref(-1)
const prompt = ref('')
const busy = ref(false)

function regenerate() {
  if (busy.value || !can('studio.generate')) return
  const base = selVer.value
  const edit = EDITS[pick.value >= 0 ? pick.value : (props.asset.versions.length + 2) % EDITS.length]
  const note = prompt.value.trim() || edit.note
  busy.value = true
  setTimeout(() => {
    addVersion(props.asset, note, edit.fn({ ...base.scene }), base.n)
    sel.value = current(props.asset).n
    busy.value = false
    prompt.value = ''
    pick.value = -1
    toast(`已基于 v${base.n} 生成新版本 v${sel.value}`)
  }, reduce ? 0 : 1100)
}

/* ---------- 客户 ---------- */
const showNewCust = ref(false)

function onCust(e) {
  const v = e.target.value
  if (v === '__new') {
    e.target.value = props.asset.customerId ?? ''
    showNewCust.value = true
    return
  }
  assignCustomer(props.asset, v ? Number(v) : null)
  toast(v ? `已归属客户「${customerOf(props.asset).name}」` : '已取消客户归属')
}
const onNewCust = (c) => assignCustomer(props.asset, c.id)

function setPriv(v) {
  setCustomerPrivacy(cust.value.id, v)
  toast(v ? `「${cust.value.name}」已隐私化` : `「${cust.value.name}」已取消隐私化`)
}

/* ---------- 公共化 / 私人化 ---------- */
const showPub = ref(false)
const pubLabel = computed(() => {
  if (!cust.value) return '演示样板(无客户信息)'
  return cust.value.private ? maskName(cust.value.name) : cust.value.name
})

function toVisibility(v) {
  if (!can('asset.publicize') || props.asset.visibility === v) return
  if (v === 'public') { showPub.value = true; return }
  setVisibility(props.asset, 'private')
  toast('已转为私人客户资产')
}
function confirmPublic() {
  setVisibility(props.asset, 'public')
  showPub.value = false
  toast('已公共化,现在显示在「公共演示资产」中')
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
          <p class="ad-label">{{ asset.id }} · {{ asset.source }}</p>
          <h2>{{ asset.name }}</h2>
        </div>
        <button type="button" class="ad-x" aria-label="关闭" @click="emit('close')"><Icon name="close" /></button>
      </header>

      <div class="ad-drawer__body">
        <!-- 左:3D 与版本历史 -->
        <div class="ad-col">
          <div class="ad-viewer">
            <Room3D :scene="selVer.scene" />
            <div class="ad-viewer__bar" :class="{ 'is-preview': preview }">
              <template v-if="preview">
                <span>正在预览 <b>v{{ selVer.n }}</b> · {{ selVer.note }}</span>
                <span class="ad-viewer__acts">
                  <button v-if="can('asset.rollback')" type="button" class="ad-btn ad-btn--sm" @click="rollback(selVer)">
                    <Icon name="undo" />回溯到此版本
                  </button>
                  <button type="button" class="ad-btn ad-btn--sm ad-btn--ghost" @click="sel = cur.n">返回当前</button>
                </span>
              </template>
              <template v-else>
                <span>当前版本 <b>v{{ cur.n }}</b> · {{ cur.note }}</span>
              </template>
            </div>
            <div v-if="busy" class="ad-viewer__busy"><i></i><span>基于 v{{ selVer.n }} 重新生成中…</span></div>
          </div>

          <section class="ad-panel">
            <h3 class="ad-panel__t">版本历史 <small>共 {{ asset.versions.length }} 版 · 回溯不会删除任何历史</small></h3>
            <ol class="ad-tl">
              <li v-for="v in timeline" :key="v.n" :class="{ 'is-sel': v.n === sel, 'is-cur': v.n === cur.n }">
                <button type="button" class="ad-tl__row" @click="sel = v.n">
                  <span class="ad-tl__n">v{{ v.n }}</span>
                  <span class="ad-tl__main">
                    <b>{{ v.note }}</b>
                    <small>{{ staffName(v.by) }} · {{ fmt(v.at) }}<template v-if="v.from"> · 基于 v{{ v.from }}</template></small>
                  </span>
                  <em v-if="v.n === cur.n" class="ad-chip ad-chip--on">当前</em>
                </button>
                <button v-if="v.n !== cur.n && can('asset.rollback')" type="button" class="ad-tl__rb"
                        @click="rollback(v)"><Icon name="undo" />回溯</button>
              </li>
            </ol>
            <p v-if="!can('asset.rollback')" class="ad-hint">当前身份无「回溯历史版本」权限,仅可预览。</p>
          </section>
        </div>

        <!-- 右:属性与操作 -->
        <div class="ad-col">
          <section class="ad-panel">
            <h3 class="ad-panel__t">资产归属</h3>
            <div class="ad-seg" role="group" aria-label="资产类型">
              <button type="button" :class="{ 'is-on': !isPublic }" :disabled="!can('asset.publicize')" @click="toVisibility('private')">私人客户资产</button>
              <button type="button" :class="{ 'is-on': isPublic }" :disabled="!can('asset.publicize')" @click="toVisibility('public')">公共演示资产</button>
            </div>
            <p class="ad-hint">
              <template v-if="!can('asset.publicize')">当前身份无「公共化 / 私人化」权限。</template>
              <template v-else-if="isPublic">已对外演示。转为私人后,将只在员工后台可见。</template>
              <template v-else>仅员工后台可见。公共化后会进入演示库,客户名按隐私设置显示。</template>
            </p>
          </section>

          <section class="ad-panel">
            <h3 class="ad-panel__t">所属客户</h3>
            <select class="ad-select" :value="asset.customerId ?? ''" :disabled="!can('customer.add')" @change="onCust">
              <option value="">未指定客户</option>
              <option v-for="c in customers" :key="c.id" :value="c.id">{{ c.name }}{{ c.private ? ' · 隐私' : '' }}</option>
              <option v-if="can('customer.add')" value="__new">＋ 新增客户…</option>
            </select>

            <div v-if="cust" class="ad-row ad-row--box">
              <div>
                <strong>客户隐私化</strong>
                <p class="ad-hint">公共展示为 <b class="ad-mono">{{ cust.private ? maskName(cust.name) : cust.name }}</b></p>
              </div>
              <Switch :model-value="cust.private" label="客户隐私化" :disabled="!can('customer.privacy')" @update:model-value="setPriv" />
            </div>
            <p v-if="cust && !can('customer.privacy')" class="ad-hint">当前身份无「设置客户隐私化」权限。</p>
            <p v-if="!can('customer.add')" class="ad-hint">当前身份无「加入所属客户」权限。</p>
          </section>

          <section class="ad-panel">
            <h3 class="ad-panel__t">再次编辑 <small>基于 v{{ selVer.n }} 生成新版本</small></h3>
            <div class="ad-chips">
              <button v-for="(e, i) in EDITS" :key="e.note" type="button" class="ad-chipbtn"
                      :class="{ 'is-on': pick === i }" :disabled="!can('studio.generate')"
                      @click="pick = pick === i ? -1 : i">{{ e.note }}</button>
            </div>
            <input v-model="prompt" class="ad-input" placeholder="补充描述(可选),如:窗帘换成亚麻质感"
                   :disabled="!can('studio.generate')" maxlength="40" @keydown.enter="regenerate" />
            <button type="button" class="ad-btn ad-btn--block" :disabled="busy || !can('studio.generate')" @click="regenerate">
              {{ busy ? '生成中…' : `基于 v${selVer.n} 再次生成` }}
            </button>
            <p v-if="!can('studio.generate')" class="ad-hint">当前身份无「发起生图 / 再次编辑」权限。</p>
          </section>

          <section class="ad-panel ad-panel--plain">
            <dl class="ad-dl">
              <div><dt>业务人员</dt><dd>{{ staffName(asset.staffId) }}</dd></div>
              <div><dt>最近更新</dt><dd>{{ fmt(cur.at) }}</dd></div>
              <div><dt>版本数</dt><dd>{{ asset.versions.length }}</dd></div>
            </dl>
          </section>
        </div>
      </div>
    </aside>

    <Modal v-if="showPub" title="公共化到演示库" @close="showPub = false">
      <p class="ad-p">公共化后,这件资产会出现在「公共演示资产」中,所有人可见。</p>
      <div class="ad-row ad-row--box">
        <div>
          <p class="ad-label">演示库中的客户显示</p>
          <strong class="ad-big">{{ pubLabel }}</strong>
        </div>
        <Icon v-if="cust?.private" name="lock" />
      </div>
      <div v-if="cust" class="ad-row ad-row--box">
        <div>
          <strong>客户「{{ cust.name }}」隐私化</strong>
          <p class="ad-hint">会同时影响该客户名下的其他公共资产</p>
        </div>
        <Switch :model-value="cust.private" label="客户隐私化" :disabled="!can('customer.privacy')" @update:model-value="setPriv" />
      </div>
      <template #foot>
        <button type="button" class="ad-btn ad-btn--ghost" @click="showPub = false">取消</button>
        <button type="button" class="ad-btn" @click="confirmPublic">确认公共化</button>
      </template>
    </Modal>

    <CustomerModal v-if="showNewCust" @close="showNewCust = false" @done="onNewCust" />
  </div>
</template>
