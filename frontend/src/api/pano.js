/**
 * 全景图 manifest 加载与工具函数
 * 图片放在 public/panoramas/，manifest.json 声明每张图的元数据
 * 上线时只需替换 manifest.json + 图片文件，无需重新 build
 *
 * 与后端 API 解耦：本模块只负责静态 manifest 资源加载，
 * 后端 generation 产生的全景图 URL 由调用方注入。
 */

let cache = null

export async function loadManifest() {
  if (cache) return cache
  const res = await fetch('/panoramas/manifest.json')
  if (!res.ok) return []
  cache = await res.json()
  return cache
}

export function getPanoById(list, id) {
  return list.find(p => p.id === id)
}

/**
 * 根据设备能力选初始画质层级
 * 手机 / 慢速 → mobile（更小尺寸的图），桌面 → full
 */
export function pickInitialLevel(pano) {
  const isMobile = /iPhone|iPad|Android|Mobile/i.test(navigator.userAgent)
  const conn = navigator.connection
  const slow = conn && /2g|3g|slow/.test(conn.effectiveType || '')
  if ((isMobile || slow) && pano.levels?.mobile) return 'mobile'
  return 'full'
}

export function getPanoUrl(pano, level = 'full') {
  const file = pano.levels?.[level] || pano.levels?.full || pano.file
  return `/panoramas/${file}`
}

export function getThumbUrl(pano) {
  return `/panoramas/${pano.levels?.thumb || pano.levels?.mobile || pano.levels?.full || pano.file}`
}

/** 效果图 URL（可选，不一定有） */
export function getEffectUrl(pano) {
  if (!pano.effectImage) return null
  return `/panoramas/${pano.effectImage}`
}

/** 效果图缩略图 */
export function getEffectThumbUrl(pano) {
  if (!pano.effectImage) return null
  const name = pano.effectImage.replace(/\.\w+$/, '')
  return `/panoramas/${name}_thumb.jpg`
}

/** 实拍图列表 (photos 数组，每个 {file, label}) */
export function getPhotos(pano) {
  return pano.photos || []
}

export function getPhotoUrl(file) {
  return `/panoramas/${file}`
}

export function getPhotoThumbUrl(file) {
  const name = file.replace(/\.\w+$/, '')
  return `/panoramas/${name}_thumb.jpg`
}

/** 3D 效果图列表 (effects 数组，每个 {file, label}) */
export function getEffects(pano) {
  return pano.effects || []
}

export function getEffectItemUrl(file) {
  return `/panoramas/${file}`
}

export function getEffectItemThumbUrl(file) {
  const name = file.replace(/\.\w+$/, '')
  return `/panoramas/${name}_thumb.jpg`
}

/** 户型图 URL（可选，不一定有） */
export function getFloorplanUrl(pano) {
  if (!pano.floorplan) return null
  return `/panoramas/${pano.floorplan}`
}

/** 户型图缩略图 */
export function getFloorplanThumbUrl(pano) {
  if (!pano.floorplan) return null
  const name = pano.floorplan.replace(/\.\w+$/, '')
  return `/panoramas/${name}_thumb.jpg`
}

export function isMobileDevice() {
  return /iPhone|iPad|Android|Mobile/i.test(navigator.userAgent)
}
