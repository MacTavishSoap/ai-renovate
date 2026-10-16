// 资产缩略图 / 3D 预览用的"光影场景"参数。
// 真实接入生图后,把 scene 换成图片地址即可,其余结构不用动。

export const PALS = [
  { wt: '#3a322b', wb: '#2b2520', ft: '#1d1916', fb: '#14110f', glow: '214,170,110', o1: '#f0d9a8', o2: '#c99a5b', obj: '#413830' },
  { wt: '#3b2f2a', wb: '#2e2420', ft: '#1f1916', fb: '#14100e', glow: '205,140,110', o1: '#f2d6c0', o2: '#c98f73', obj: '#46362e' },
  { wt: '#2f3228', wb: '#24261f', ft: '#1b1c17', fb: '#11120e', glow: '170,176,120', o1: '#e7e2b8', o2: '#b5ae78', obj: '#4a4a3d' },
  { wt: '#34312e', wb: '#27241f', ft: '#1c1a17', fb: '#11100e', glow: '190,175,150', o1: '#efe3c8', o2: '#cdbd98', obj: '#3b3630' },
  { wt: '#2d3230', wb: '#222726', ft: '#191c1b', fb: '#0f1110', glow: '140,175,165', o1: '#d8ece4', o2: '#8fb5a8', obj: '#34403c' },
  { wt: '#382c30', wb: '#2a2024', ft: '#1c1619', fb: '#120e10', glow: '190,120,130', o1: '#f0cfd4', o2: '#bc7b86', obj: '#46343a' },
  { wt: '#33302a', wb: '#26231e', ft: '#1b1915', fb: '#100f0c', glow: '200,185,130', o1: '#f3e8bd', o2: '#c4b070', obj: '#443e32' },
  { wt: '#2c2f35', wb: '#212329', ft: '#17191d', fb: '#0e0f12', glow: '150,165,200', o1: '#dfe6f3', o2: '#8d9bbd', obj: '#343841' },
]

// 五种空间构图:窗洞 / 家具的位置与形状
export const SHAPES = [
  { arch: true, ox: 56, ow: 26, oh: 64, fx: 8, fw: 40, fh: 14 },
  { arch: false, ox: 14, ow: 30, oh: 55, fx: 48, fw: 44, fh: 14 },
  { arch: false, ox: 10, ow: 80, oh: 20, ob: 46, fx: 20, fw: 60, fh: 16, fb: 28 },
  { arch: false, slats: true, ox: 30, ow: 50, oh: 62, fx: 8, fw: 26, fh: 22 },
  { arch: true, ox: 38, ow: 22, oh: 60, fx: 52, fw: 36, fh: 12 },
]

export const baseScene = (pal, shape) => ({ pal, gi: 0.38, obj: null, ...SHAPES[shape] })

export function sceneVars(s) {
  const p = PALS[s.pal % PALS.length]
  const open = s.slats
    ? `repeating-linear-gradient(90deg,${p.o1} 0 26%,transparent 26% 37%)`
    : `linear-gradient(180deg,${p.o1},${p.o2})`
  return {
    '--wall-top': p.wt,
    '--wall-bot': p.wb,
    '--floor-top': p.ft,
    '--floor-bot': p.fb,
    '--glow': `rgba(${p.glow},${s.gi})`,
    '--lx': `${s.ox + s.ow / 2}%`,
    '--ly': '38%',
    '--ox': `${s.ox}%`,
    '--ow': `${s.ow}%`,
    '--oh': `${s.oh}%`,
    '--ob': `${s.ob ?? 32}%`,
    '--or': s.arch ? '999px 999px 0 0' : '0',
    '--open-bg': open,
    '--open-glow': `rgba(${p.glow},.45)`,
    '--fx': `${s.fx}%`,
    '--fw': `${s.fw}%`,
    '--fh': `${s.fh}%`,
    '--fb': `${s.fb ?? 31}%`,
    '--obj': s.obj || p.obj,
  }
}

// 模拟"基于生图再次编辑"产生的变化
export const EDITS = [
  { note: '主光源调为暖光', fn: (s) => ({ ...s, gi: Math.min(0.55, s.gi + 0.1) }) },
  { note: '沙发改为深灰绒面', fn: (s) => ({ ...s, obj: '#3d3b3f' }) },
  {
    note: '扩大窗洞,增加进光',
    fn: (s) => (s.ow > 50
      ? { ...s, oh: Math.min(30, s.oh + 4) }
      : { ...s, ow: Math.min(34, s.ow + 6), oh: Math.min(70, s.oh + 4), ox: Math.max(4, s.ox - 3) }),
  },
  { note: '整体换为冷调材质', fn: (s) => ({ ...s, pal: (s.pal + 4) % PALS.length }) },
  {
    note: '窗洞右移,压低光线',
    fn: (s) => ({ ...s, ox: Math.min(100 - s.ow - 4, s.ox + 6), gi: Math.max(0.2, s.gi - 0.1) }),
  },
  { note: '家具右移,留出动线', fn: (s) => ({ ...s, fx: Math.max(4, Math.min(100 - s.fw - 4, s.fx + 10)) }) },
]
