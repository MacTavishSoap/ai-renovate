<script setup>
import { computed, ref } from 'vue'
import AssetCard from '../../components/admin/AssetCard.vue'
import AssetDrawer from '../../components/admin/AssetDrawer.vue'
import CustomerModal from '../../components/admin/CustomerModal.vue'
import Switch from '../../components/admin/Switch.vue'
import Icon from '../../components/admin/Icon.vue'
import {
  assets, can, customerLabel, customerOf, customers, maskName, me, setCustomerPrivacy, staff,
  staffName, studioState, toast, visibleAssets,
} from '../../admin/store'

const tab = ref('private') // private | public
const q = ref('')
const visitor = ref(true) // 对外展示里,是否按访客看到的样子显示
const openId = ref(null)
const showCust = ref(false)

const openAsset = computed(() => assets.find((a) => a.id === openId.value) ?? null)
const asVisitor = computed(() => tab.value === 'public' && visitor.value)

function match(a) {
  const s = q.value.trim().toLowerCase()
  if (!s) return true
  // 访客视角下只按"看得到的名字"搜索,否则会泄露被隐藏的客户姓名
  const who = asVisitor.value ? customerLabel(a, true) : customerOf(a)?.name
  return [a.name, who].some((x) => x && x.toLowerCase().includes(s))
}

const base = (v) => visibleAssets.value.filter((a) => a.visibility === v)
const counts = computed(() => ({ private: base('private').length, public: base('public').length }))
const list = computed(() => base(tab.value).filter(match))

// 一眼看懂:员工 → 资产 → 客户 → 去向
const flow = computed(() => [
  { k: '员工', v: staff.filter((s) => studioState(s) === 'on').length, u: '人', c: '可使用 AI 生图' },
  { k: '资产', v: visibleAssets.value.length, u: '件', c: '已生成' },
  { k: '客户', v: customers.filter((c) => can('asset.viewAll') || c.ownerId === me.value.id).length, u: '位', c: '已建档' },
])

// 私人资产按客户分组;新添加、暂无资产的客户也要看得见
const groups = computed(() => {
  const byC = new Map()
  for (const a of list.value) {
    const k = a.customerId ?? 0
    if (!byC.has(k)) byC.set(k, [])
    byC.get(k).push(a)
  }
  if (!q.value.trim()) {
    for (const c of customers) {
      if (!byC.has(c.id) && (can('asset.viewAll') || c.ownerId === me.value.id)) byC.set(c.id, [])
    }
  }
  return [...byC]
    .map(([id, items]) => ({ id, c: customers.find((c) => c.id === id) ?? null, items }))
    // 有资产的在前(已指定客户优先),暂无资产的客户排在最后
    .sort((a, b) => (!a.items.length) - (!b.items.length) || (!a.c) - (!b.c) || b.items.length - a.items.length)
})

function setHide(c, v) {
  setCustomerPrivacy(c.id, v)
  toast(v ? `已隐藏「${c.name}」的真实姓名` : `已显示「${c.name}」的真实姓名`)
}
</script>

<template>
  <section class="ad-assets">
    <ul class="ad-flow" aria-label="整体情况">
      <li v-for="s in flow" :key="s.k">
        <span class="ad-flow__k">{{ s.k }}</span>
        <b>{{ s.v }}<small>{{ s.u }}</small></b>
        <span class="ad-flow__c">{{ s.c }}</span>
      </li>
      <li class="ad-flow__split">
        <span class="ad-flow__k">去向</span>
        <b><i><Icon name="lock" /></i>{{ counts.private }}<small>件 客户专属</small></b>
        <b><i><Icon name="globe" /></i>{{ counts.public }}<small>件 对外展示</small></b>
      </li>
    </ul>

    <p v-if="!can('asset.viewAll')" class="ad-banner">
      <Icon name="lock" />你的身份只能看到自己名下的客户专属资产
    </p>

    <div class="ad-bar">
      <div class="ad-tabs" role="tablist">
        <button type="button" role="tab" :aria-selected="tab === 'private'" :class="{ 'is-on': tab === 'private' }" @click="tab = 'private'">
          <Icon name="lock" />私人客户资产<em>{{ counts.private }}</em>
        </button>
        <button type="button" role="tab" :aria-selected="tab === 'public'" :class="{ 'is-on': tab === 'public' }" @click="tab = 'public'">
          <Icon name="globe" />公共演示资产<em>{{ counts.public }}</em>
        </button>
      </div>
      <div class="ad-bar__r">
        <input v-model="q" class="ad-input ad-input--search" placeholder="搜索客户或资产名称" aria-label="搜索" />
        <button v-if="can('customer.add')" type="button" class="ad-btn ad-btn--ghost" @click="showCust = true">
          <Icon name="plus" />添加客户
        </button>
      </div>
    </div>

    <!-- 私人:按客户分组 -->
    <template v-if="tab === 'private'">
      <div v-for="g in groups" :key="g.id" class="ad-group">
        <header class="ad-group__head">
          <span class="ad-avatar">{{ g.c ? g.c.name[0] : '?' }}</span>
          <div class="ad-group__who">
            <h3>{{ g.c ? g.c.name : '未指定客户' }}</h3>
            <p>{{ g.items.length }} 件资产<template v-if="g.c"> · 业务人员 {{ staffName(g.c.ownerId) }}</template></p>
          </div>
          <div v-if="g.c" class="ad-group__priv">
            <span class="ad-chip" :class="{ 'ad-chip--on': g.c.private }">对外显示 {{ g.c.private ? maskName(g.c.name) : g.c.name }}</span>
            <label>
              <span>隐藏真实姓名</span>
              <Switch :model-value="g.c.private" :label="`隐藏${g.c.name}的真实姓名`" :disabled="!can('customer.privacy')"
                      @update:model-value="setHide(g.c, $event)" />
            </label>
          </div>
        </header>
        <div v-if="g.items.length" class="ad-grid">
          <AssetCard v-for="a in g.items" :key="a.id" :asset="a" @open="openId = $event.id" />
        </div>
        <p v-else class="ad-empty">暂无资产</p>
      </div>
      <p v-if="!groups.length" class="ad-empty">没有找到相关资产</p>
    </template>

    <!-- 公共:平铺 -->
    <template v-else>
      <div class="ad-visitor">
        <label>
          <Switch v-model="visitor" label="按访客看到的样子显示" />
          <span>按访客看到的样子显示</span>
        </label>
      </div>
      <div v-if="list.length" class="ad-grid">
        <AssetCard v-for="a in list" :key="a.id" :asset="a" :visitor="visitor" @open="openId = $event.id" />
      </div>
      <p v-else class="ad-empty">没有找到相关资产</p>
    </template>

    <AssetDrawer v-if="openAsset" :key="openAsset.id" :asset="openAsset" @close="openId = null" />
    <CustomerModal v-if="showCust" @close="showCust = false" />
  </section>
</template>
