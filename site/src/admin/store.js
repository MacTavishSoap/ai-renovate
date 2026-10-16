import { computed, reactive, ref } from 'vue'
import { baseScene, EDITS } from './scene'

/* ---------------------------------------------------------
   演示数据层:全部是内存里的假数据,刷新即重置。
   接真实后端时,只需要把这里的 reactive 数组换成接口请求。
   --------------------------------------------------------- */

export const ROLES = ['管理员', '设计师', '业务人员']

export const CAPS = [
  { key: 'studio.enter', group: '功能页面', label: '进入功能页面', hint: '生图工坊入口,另需在员工列表里单独开通' },
  { key: 'studio.generate', group: '功能页面', label: '发起生图 / 再次编辑', hint: '基于生图产出新的 3D 版本' },
  { key: 'asset.viewAll', group: '资产', label: '查看全部客户资产', hint: '关闭后只能看到本人名下的私人资产' },
  { key: 'asset.rollback', group: '资产', label: '回溯历史版本', hint: '把资产恢复到任意一个旧版本' },
  { key: 'asset.publicize', group: '资产', label: '公共化 / 私人化', hint: '在私人客户资产与公共演示资产之间转换' },
  { key: 'customer.add', group: '客户', label: '加入所属客户', hint: '为资产指定或新增所属客户' },
  { key: 'customer.privacy', group: '客户', label: '设置客户隐私化', hint: '公共展示时隐藏客户姓名' },
]

export const perms = reactive({
  管理员: Object.fromEntries(CAPS.map((c) => [c.key, true])),
  设计师: {
    'studio.enter': true, 'studio.generate': true, 'asset.viewAll': true, 'asset.rollback': true,
    'asset.publicize': false, 'customer.add': true, 'customer.privacy': false,
  },
  业务人员: {
    'studio.enter': true, 'studio.generate': true, 'asset.viewAll': false, 'asset.rollback': false,
    'asset.publicize': false, 'customer.add': true, 'customer.privacy': true,
  },
})

/* ---------- 员工 ---------- */
export const staff = reactive([
  { id: 1, name: '张霁', role: '管理员', studio: true, joined: '2022-03', gens: 312 },
  { id: 2, name: '林初', role: '设计师', studio: true, joined: '2023-01', gens: 486 },
  { id: 3, name: '周岚', role: '设计师', studio: true, joined: '2023-07', gens: 358 },
  { id: 4, name: '陈默', role: '业务人员', studio: true, joined: '2024-02', gens: 141 },
  { id: 5, name: '李敏', role: '业务人员', studio: true, joined: '2024-05', gens: 96 },
  { id: 6, name: '赵安', role: '业务人员', studio: false, joined: '2025-01', gens: 0 },
  { id: 7, name: '吴桐', role: '设计师', studio: true, joined: '2025-04', gens: 207 },
])

export const meId = ref(1)
export const me = computed(() => staff.find((s) => s.id === meId.value) || staff[0])
export const staffName = (id) => staff.find((s) => s.id === id)?.name ?? '—'

export function can(key) {
  const on = !!perms[me.value.role]?.[key]
  return key === 'studio.enter' ? on && me.value.studio : on
}

export function addStaff(name, role) {
  const id = Math.max(...staff.map((s) => s.id)) + 1
  staff.push({ id, name, role, studio: role !== '业务人员', joined: '2026-10', gens: 0 })
}

/* ---------- 客户 ---------- */
export const customers = reactive([
  { id: 1, name: '王思远', private: true, ownerId: 4 },
  { id: 2, name: '李婉清', private: false, ownerId: 4 },
  { id: 3, name: '陈景然', private: true, ownerId: 5 },
  { id: 4, name: '周明哲', private: true, ownerId: 5 },
  { id: 5, name: '刘雨桐', private: false, ownerId: 4 },
  { id: 6, name: '赵启航', private: true, ownerId: 6 },
  { id: 7, name: '孙若曦', private: true, ownerId: 2 },
  { id: 8, name: '吴子墨', private: false, ownerId: 5 },
  { id: 9, name: '郑清和', private: true, ownerId: 3 },
])

export const maskName = (n) => (n.length > 1 ? n[0] + '*'.repeat(n.length - 1) : n)

export function addCustomer(name, priv = true) {
  const c = { id: Math.max(...customers.map((x) => x.id)) + 1, name, private: priv, ownerId: me.value.id }
  customers.push(c)
  return c
}

export function setCustomerPrivacy(id, value) {
  const c = customers.find((x) => x.id === id)
  if (c) c.private = value
}

/* ---------- 资产与版本 ---------- */
const H = 3600e3
const NOW = Date.UTC(2026, 9, 16, 2, 0)
const DESIGNERS = [2, 3, 7]

// [项目, 空间, 色调, 构图, 可见性, 客户id, 业务员id, 版本数, 回溯到第几版(可选)]
const SEED = [
  ['云栖壹号', '客厅', 0, 0, 'private', 1, 4, 4],
  ['云栖壹号', '主卧', 1, 1, 'private', 1, 4, 3],
  ['木隐', '书房', 1, 1, 'private', 2, 4, 2],
  ['岩境', '餐厨', 2, 2, 'private', 3, 5, 4, 2],
  ['岩境', '客厅', 3, 3, 'private', 3, 5, 3],
  ['静庐', '茶室', 3, 3, 'private', 4, 5, 2],
  ['澜庭', '玄关', 4, 4, 'private', 6, 6, 2],
  ['听松', '露台', 7, 0, 'private', 7, 2, 3],
  ['山海间', '主卧', 5, 1, 'private', 9, 3, 4],
  ['云栖壹号', '客厅 · 方案 B', 0, 0, 'public', 2, 4, 3],
  ['样板 · 现代轻奢', '客厅', 6, 0, 'public', null, 2, 4],
  ['样板 · 原木格栅', '卧室', 1, 1, 'public', 5, 4, 2],
  ['样板 · 石材与黄铜', '餐厨', 2, 2, 'public', null, 3, 3],
  ['澜庭', '客厅', 4, 4, 'public', 6, 6, 3],
  ['岩境', '书房', 2, 2, 'public', 3, 5, 2],
]

function build(i, [project, room, pal, shape, visibility, customerId, staffId, n, rb]) {
  const t0 = NOW - (i * 29 + 16) * H
  let scene = baseScene(pal, shape)
  const versions = [{ n: 1, note: '初版 · 户型图与风格词生图', scene, by: staffId, from: null, at: t0 }]
  for (let k = 1; k < n; k++) {
    const edit = EDITS[(i + k) % EDITS.length]
    scene = edit.fn(scene)
    versions.push({
      n: k + 1,
      note: edit.note,
      scene,
      by: k % 2 ? staffId : DESIGNERS[i % 3],
      from: k,
      at: t0 + k * (5 + (i % 4)) * H,
    })
  }
  if (rb) {
    const src = versions[rb - 1]
    versions.push({ n: versions.length + 1, note: `回溯至 v${rb}`, scene: { ...src.scene }, by: DESIGNERS[i % 3], from: rb, at: t0 + n * 7 * H })
  }
  return { id: `A-${1024 + i}`, name: `${project} · ${room}`, source: `生图 #${1040 + i}`, visibility, customerId, staffId, versions }
}

export const assets = reactive(SEED.map((row, i) => build(i, row)))

export const current = (a) => a.versions[a.versions.length - 1]
export const customerOf = (a) => customers.find((c) => c.id === a.customerId) ?? null

// 仅可见:公共资产所有人可见;私人资产需要"查看全部"权限,否则只看本人名下
export const visibleAssets = computed(() =>
  assets.filter((a) => a.visibility === 'public' || can('asset.viewAll') || a.staffId === me.value.id),
)

/** 资产卡片上显示的客户名。公共视图下,被隐私化的客户显示为 王** */
export function customerLabel(a, publicView) {
  const c = customerOf(a)
  if (!c) return publicView || a.visibility === 'public' ? '演示样板' : '未指定客户'
  return publicView && c.private ? maskName(c.name) : c.name
}

export function setVisibility(a, v) {
  a.visibility = v
}

export function assignCustomer(a, id) {
  a.customerId = id || null
}

export function addVersion(a, note, scene, from) {
  a.versions.push({ n: a.versions.length + 1, note, scene, by: me.value.id, from, at: Date.now() })
  const m = staff.find((s) => s.id === me.value.id)
  if (m) m.gens += 1
}

export function rollbackTo(a, ver) {
  addVersion(a, `回溯至 v${ver.n}`, { ...ver.scene }, ver.n)
}

/* ---------- 工具 ---------- */
const p2 = (n) => String(n).padStart(2, '0')
export const fmt = (t) => {
  const d = new Date(t)
  return `${p2(d.getMonth() + 1)}-${p2(d.getDate())} ${p2(d.getHours())}:${p2(d.getMinutes())}`
}

export const toasts = ref([])
export function toast(msg) {
  const id = Date.now() + Math.random()
  toasts.value.push({ id, msg })
  setTimeout(() => (toasts.value = toasts.value.filter((t) => t.id !== id)), 2600)
}
