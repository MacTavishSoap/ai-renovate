export const stats = [
  { label: '设计施工经验', value: 12, unit: '年' },
  { label: '已交付住宅', value: 480, unit: '套', plus: true },
  { label: '隐蔽工程质保', value: 5, unit: '年' },
]

export const works = [
  { no: '01', name: '云栖壹号', meta: '142㎡ · 三居整装 · 现代轻奢', scene: 's1', slot: 'work--1' },
  { no: '02', name: '木隐', meta: '96㎡ · 两居 · 原木格栅', scene: 's2', slot: 'work--2', delay: '.12s' },
  { no: '03', name: '岩境', meta: '188㎡ · 大平层 · 石材与黄铜', scene: 's3', slot: 'work--3' },
  { no: '04', name: '静庐', meta: '320㎡ · 别墅 · 全案设计', scene: 's4', slot: 'work--4', delay: '.12s' },
]

export const pickets = Array.from({ length: 90 }, (_, i) => ({
  i,
  h: (0.15 + 0.49 * Math.abs(Math.sin(i * 0.21) * Math.cos(i * 0.057 + 0.8))).toFixed(3),
}))

export const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches
