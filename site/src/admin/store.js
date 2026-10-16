import { computed, reactive, ref } from 'vue'
import { getEffectItemThumbUrl, getThumbUrl } from '@frontend/api/pano'

/* ---------------------------------------------------------
   演示数据层:全部是内存里的假数据,刷新即重置。
   画面用的是项目里真实的全景图 / 3D 户型图(frontend/public/panoramas)。
   "再次编辑"目前用光影效果来模拟,接真实生图后,只需把每个版本换成生图结果。
   --------------------------------------------------------- */

/* ---------- 光影效果(每次"再次编辑"可叠加) ---------- */
export const LOOKS = {
  warm: { label: '暖光', css: 'sepia(.28) saturate(1.18) brightness(1.04)' },
  cool: { label: '冷调', css: 'hue-rotate(-16deg) saturate(.9) brightness(1.03)' },
  bright: { label: '提亮', css: 'brightness(1.16) contrast(.96)' },
  soft: { label: '柔和', css: 'contrast(.9) saturate(.82) brightness(1.06)' },
  rich: { label: '浓郁', css: 'contrast(1.12) saturate(1.32)' },
  dusk: { label: '黄昏', css: 'sepia(.45) saturate(1.3) brightness(.86) hue-rotate(-8deg)' },
}
export const lookFilter = (keys) => keys.map((k) => LOOKS[k].css).join(' ') || 'none'

/* ---------- 角色与权限 ---------- */
export const ROLES = ['管理员', '设计师', '业务人员']

export const CAPS = [
  { key: 'studio.enter', group: 'AI 生图', label: '使用 AI 生图页面' },
  { key: 'studio.generate', group: 'AI 生图', label: '发起生图 / 再次修改' },
  { key: 'asset.viewAll', group: '资产', label: '查看所有客户的资产' },
  { key: 'asset.rollback', group: '资产', label: '恢复到历史版本' },
  { key: 'asset.publicize', group: '资产', label: '切换「客户专属 / 对外展示」' },
  { key: 'customer.add', group: '客户', label: '添加客户、指定归属' },
  { key: 'customer.privacy', group: '客户', label: '隐藏客户真实姓名' },
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
  { id: 1, name: '张霁', role: '管理员', studio: true, gens: 312 },
  { id: 2, name: '林初', role: '设计师', studio: true, gens: 486 },
  { id: 3, name: '周岚', role: '设计师', studio: true, gens: 358 },
  { id: 4, name: '陈默', role: '业务人员', studio: true, gens: 141 },
  { id: 5, name: '李敏', role: '业务人员', studio: true, gens: 96 },
  { id: 6, name: '赵安', role: '业务人员', studio: false, gens: 0 },
  { id: 7, name: '吴桐', role: '设计师', studio: true, gens: 207 },
])

export const meId = ref(1)
export const me = computed(() => staff.find((s) => s.id === meId.value) || staff[0])
export const staffName = (id) => staff.find((s) => s.id === id)?.name ?? '—'

export function can(key) {
  const on = !!perms[me.value.role]?.[key]
  return key === 'studio.enter' ? on && me.value.studio : on
}
export const canCount = computed(() => CAPS.filter((c) => can(c.key)).length)

/** 员工能否使用 AI 生图:角色授权 且 本人已开通 */
export const studioState = (s) => {
  if (!perms[s.role]['studio.enter']) return 'role'
  return s.studio ? 'on' : 'off'
}

export function addStaff(name, role) {
  const id = Math.max(...staff.map((s) => s.id)) + 1
  staff.push({ id, name, role, studio: role !== '业务人员', gens: 0 })
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

// kind 'pano' = 全景效果图(Photo Sphere Viewer);'plan' = 3D 户型图(多角度)
export const ROOMS = { livingroom: '客厅', bedroom: '主卧', children: '儿童房', secondbed: '次卧', bathroom: '卫生间' }

// [名称, 类型, 全景编号, 去向, 客户id, 业务员id, 每一版的效果组合[], 回溯到第几版(可选)]
const SEED = [
  ['云栖壹号 · 客厅', 'pano', 'livingroom', 'private', 1, 4, [[], ['warm'], ['warm', 'bright'], ['cool']]],
  ['云栖壹号 · 主卧', 'pano', 'bedroom', 'private', 1, 4, [[], ['soft'], ['soft', 'warm']]],
  ['云栖壹号 · 3D 户型图', 'plan', null, 'private', 1, 4, [[], ['bright']]],
  ['木隐 · 儿童房', 'pano', 'children', 'private', 2, 4, [[], ['rich']]],
  ['岩境 · 客厅', 'pano', 'livingroom', 'private', 3, 5, [[], ['dusk'], ['dusk', 'bright'], ['soft']], 2],
  ['岩境 · 次卧', 'pano', 'secondbed', 'private', 3, 5, [[], ['warm'], ['warm', 'soft']]],
  ['静庐 · 卫生间', 'pano', 'bathroom', 'private', 4, 5, [[], ['cool']]],
  ['澜庭 · 主卧', 'pano', 'bedroom', 'private', 6, 6, [[], ['bright']]],
  ['听松 · 3D 户型图', 'plan', null, 'private', 7, 2, [[], ['rich'], ['rich', 'warm']]],
  ['山海间 · 客厅', 'pano', 'livingroom', 'private', 9, 3, [[], ['cool'], ['cool', 'bright'], ['soft']]],
  ['样板间 · 现代简约客厅', 'pano', 'livingroom', 'public', null, 2, [[], ['bright'], ['bright', 'soft'], ['soft']]],
  ['样板间 · 原木卧室', 'pano', 'bedroom', 'public', 5, 4, [[], ['warm']]],
  ['样板间 · 三居室 3D 户型图', 'plan', null, 'public', null, 3, [[], ['bright'], ['bright', 'soft']]],
  ['澜庭 · 儿童房', 'pano', 'children', 'public', 6, 6, [[], ['soft'], ['soft', 'warm']]],
  ['岩境 · 次卧 方案 B', 'pano', 'secondbed', 'public', 3, 5, [[], ['dusk']]],
]

function build(i, [name, kind, ref, visibility, customerId, staffId, steps, rb]) {
  const designers = [2, 3, 7]
  const t0 = NOW - (i * 29 + 16) * H
  const versions = steps.map((looks, k) => ({
    n: k + 1,
    note: k === 0 ? '初版' : LOOKS[looks[looks.length - 1]].label,
    looks,
    by: k % 2 ? designers[i % 3] : staffId,
    from: k ? k : null,
    at: t0 + k * (5 + (i % 4)) * H,
  }))
  if (rb) {
    const src = versions[rb - 1]
    versions.push({ n: versions.length + 1, note: `恢复到第${rb}版`, looks: [...src.looks], by: designers[i % 3], from: rb, at: t0 + steps.length * 7 * H })
  }
  return { id: `A-${1024 + i}`, name, kind, ref, visibility, customerId, staffId, versions }
}

export const assets = reactive(SEED.map((row, i) => build(i, row)))

export const current = (a) => a.versions[a.versions.length - 1]
export const customerOf = (a) => customers.find((c) => c.id === a.customerId) ?? null

/** 缩略图(沿用项目 api/pano.js 的地址规则) */
export const coverUrl = (a) =>
  a.kind === 'plan'
    ? getEffectItemThumbUrl('effect_front.jpg')
    : getThumbUrl({ file: `${a.ref}.jpg`, levels: { thumb: `${a.ref}_thumb.jpg` } })

// 公共资产所有人可见;私人资产需要"查看所有客户的资产"权限,否则只看本人名下
export const visibleAssets = computed(() =>
  assets.filter((a) => a.visibility === 'public' || can('asset.viewAll') || a.staffId === me.value.id),
)

/** 资产卡片上显示的客户名。访客视角下,隐藏姓名的客户显示为 王** */
export function customerLabel(a, visitor) {
  const c = customerOf(a)
  if (!c) return a.visibility === 'public' ? '样板展示' : '未指定客户'
  return visitor && c.private ? maskName(c.name) : c.name
}

export function setVisibility(a, v) {
  a.visibility = v
}

export function assignCustomer(a, id) {
  a.customerId = id || null
}

export function addVersion(a, note, looks, from) {
  a.versions.push({ n: a.versions.length + 1, note, looks, by: me.value.id, from, at: Date.now() })
  const m = staff.find((s) => s.id === me.value.id)
  if (m) m.gens += 1
}

/** 在某一版的基础上叠加一种效果,生成新的一版 */
export function applyLook(a, base, key) {
  const looks = [...base.looks.filter((k) => k !== key), key].slice(-3)
  addVersion(a, LOOKS[key].label, looks, base.n)
}

/** 恢复到旧版本:不删除任何历史,而是复制它成为最新一版 */
export function rollbackTo(a, ver) {
  addVersion(a, `恢复到第${ver.n}版`, [...ver.looks], ver.n)
}

/* ---------- 工具 ---------- */
const p2 = (n) => String(n).padStart(2, '0')
export const fmt = (t) => {
  const d = new Date(t)
  return `${p2(d.getMonth() + 1)}-${p2(d.getDate())} ${p2(d.getHours())}:${p2(d.getMinutes())}`
}
export const fmtDay = (t) => {
  const d = new Date(t)
  return `${p2(d.getMonth() + 1)}-${p2(d.getDate())}`
}

export const toasts = ref([])
export function toast(msg) {
  const id = Date.now() + Math.random()
  toasts.value.push({ id, msg })
  setTimeout(() => (toasts.value = toasts.value.filter((t) => t.id !== id)), 2600)
}
