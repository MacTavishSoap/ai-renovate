<script setup>
import { computed, ref } from 'vue'
import AssetCard from '../../components/admin/AssetCard.vue'
import AssetDrawer from '../../components/admin/AssetDrawer.vue'
import CustomerModal from '../../components/admin/CustomerModal.vue'
import Switch from '../../components/admin/Switch.vue'
import Icon from '../../components/admin/Icon.vue'
import {
  assets, can, customerLabel, customerOf, customers, maskName, me, setCustomerPrivacy,
  staffName, toast, visibleAssets,
} from '../../admin/store'

const tab = ref('private') // private | public
const q = ref('')
const visitor = ref(true) // 公共库里是否以访客视角查看(隐私化客户显示为 王**)
const openId = ref(null)
const showCust = ref(false)

const openAsset = computed(() => assets.find((a) => a.id === openId.value) ?? null)
const publicView = computed(() => tab.value === 'public' && visitor.value)

function match(a) {
  const s = q.value.trim().toLowerCase()
  if (!s) return true
  // 访客视角下只能按"看得到的名字"搜索,否则会泄露被隐私化的客户姓名
  const who = publicView.value ? customerLabel(a, true) : customerOf(a)?.name
  return [a.name, a.id, who, staffName(a.staffId)].some((x) => x && x.toLowerCase().includes(s))
}

const base = (v) => visibleAssets.value.filter((a) => a.visibility === v)
const counts = computed(() => ({ private: base('private').length, public: base('public').length }))
const list = computed(() => base(tab.value).filter(match))

const stats = computed(() => [
  { k: '资产总数', v: visibleAssets.value.length },
  { k: '私人客户资产', v: counts.value.private },
  { k: '公共演示资产', v: counts.value.public },
  { k: '已隐私化客户', v: customers.filter((c) => c.private).length },
])

// 私人资产按客户分组;新加入、暂无资产的客户也要看得见
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

function setPriv(c, v) {
  setCustomerPrivacy(c.id, v)
  toast(v ? `「${c.name}」已隐私化,公共展示为 ${maskName(c.name)}` : `「${c.name}」已取消隐私化`)
}
</script>

<template>
  <section class="ad-assets">
    <ul class="ad-stats">
      <li v-for="s in stats" :key="s.k"><b>{{ s.v }}</b><span>{{ s.k }}</span></li>
    </ul>

    <p v-if="!can('asset.viewAll')" class="ad-banner">
      <Icon name="lock" />当前身份「{{ me.role }}」无「查看全部客户资产」权限,私人资产仅显示你本人名下的内容。
    </p>

    <div class="ad-bar">
      <div class="ad-tabs" role="tablist">
        <button type="button" role="tab" :aria-selected="tab === 'private'" :class="{ 'is-on': tab === 'private' }" @click="tab = 'private'">
          私人客户资产<em>{{ counts.private }}</em>
        </button>
        <button type="button" role="tab" :aria-selected="tab === 'public'" :class="{ 'is-on': tab === 'public' }" @click="tab = 'public'">
          公共演示资产<em>{{ counts.public }}</em>
        </button>
      </div>
      <div class="ad-bar__r">
        <input v-model="q" class="ad-input ad-input--search" placeholder="搜索资产 / 客户 / 业务人员" aria-label="搜索" />
        <button v-if="can('customer.add')" type="button" class="ad-btn ad-btn--ghost" @click="showCust = true">
          <Icon name="plus" />加入客户
        </button>
      </div>
    </div>

    <!-- 私人:按客户分组 -->
    <template v-if="tab === 'private'">
      <p class="ad-note">私人客户资产只在员工后台可见,按所属客户归类。客户隐私化后,这些资产一旦公共化,客户名会显示为 {{ maskName('王思远') }}。</p>

      <div v-for="g in groups" :key="g.id" class="ad-group">
        <header class="ad-group__head">
          <span class="ad-avatar">{{ g.c ? g.c.name[0] : '?' }}</span>
          <div class="ad-group__who">
            <h3>{{ g.c ? g.c.name : '未指定客户' }}</h3>
            <p>{{ g.items.length }} 项私人资产<template v-if="g.c"> · 负责:{{ staffName(g.c.ownerId) }}</template></p>
          </div>
          <label v-if="g.c" class="ad-group__priv">
            <span>隐私化<small>公共展示为 {{ g.c.private ? maskName(g.c.name) : g.c.name }}</small></span>
            <Switch :model-value="g.c.private" :label="`${g.c.name} 隐私化`" :disabled="!can('customer.privacy')"
                    @update:model-value="setPriv(g.c, $event)" />
          </label>
        </header>
        <div v-if="g.items.length" class="ad-grid">
          <AssetCard v-for="a in g.items" :key="a.id" :asset="a" @open="openId = $event.id" />
        </div>
        <p v-else class="ad-empty">该客户暂无私人资产。基于生图产出的资产会归入这里。</p>
      </div>
      <p v-if="!groups.length" class="ad-empty">没有符合条件的资产。</p>
    </template>

    <!-- 公共:平铺 -->
    <template v-else>
      <div class="ad-visitor">
        <p class="ad-note">公共演示资产对所有人可见,可用于对外演示。</p>
        <label class="ad-visitor__sw">
          <span>访客视角<small>隐私化客户显示为 {{ maskName('王思远') }}</small></span>
          <Switch v-model="visitor" label="访客视角" />
        </label>
      </div>
      <div v-if="list.length" class="ad-grid">
        <AssetCard v-for="a in list" :key="a.id" :asset="a" :public-view="visitor" @open="openId = $event.id" />
      </div>
      <p v-else class="ad-empty">没有符合条件的资产。</p>
    </template>

    <AssetDrawer v-if="openAsset" :key="openAsset.id" :asset="openAsset" @close="openId = null" />
    <CustomerModal v-if="showCust" @close="showCust = false" />
  </section>
</template>
